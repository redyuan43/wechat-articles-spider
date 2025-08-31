import os
import re
import requests
from bs4 import BeautifulSoup
import html2text
from datetime import datetime
import time
import json
from collections import Counter
import jieba
import jieba.analyse


class WeChatArticleAdvancedCrawler:
    def __init__(self, output_dir='wechat_articles'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化html2text转换器
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        self.h.bypass_tables = False

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/'
        }
        
        # 关键词权重配置
        self.keyword_weights = {
            'title': 3.0,      # 标题中的关键词权重
            'subtitle': 2.0,   # 副标题权重
            'strong': 1.5,     # 加粗文本权重
            'normal': 1.0      # 普通文本权重
        }

    def get_safe_title(self, title):
        safe_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]
        return safe_title.strip()

    def extract_all_metadata(self, soup, response_text, url):
        """全面提取文章元数据"""
        metadata = {
            'url': url,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 1. 提取公众号名称 (nickname)
        nickname = None
        # 方法1: rich_media_meta_nickname
        nickname_elem = soup.find('span', class_='rich_media_meta rich_media_meta_nickname')
        if nickname_elem:
            nickname = nickname_elem.get_text().strip()
        
        # 方法2: js_name
        if not nickname:
            js_name = soup.find('a', id='js_name')
            if js_name:
                nickname = js_name.get_text().strip()
        
        # 方法3: profile_nickname
        if not nickname:
            profile_nickname = soup.find('strong', class_='profile_nickname')
            if profile_nickname:
                nickname = profile_nickname.get_text().strip()
        
        # 方法4: 从meta标签
        if not nickname:
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                nickname = meta_author.get('content', '')
        
        # 方法5: 从script变量中提取
        if not nickname:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # 尝试匹配 nickname
                    nick_match = re.search(r'nickname\s*=\s*["\'](.*?)["\']', script.string)
                    if nick_match:
                        nickname = nick_match.group(1)
                        break
                    # 尝试匹配 user_name
                    user_match = re.search(r'user_name\s*=\s*["\'](.*?)["\']', script.string)
                    if user_match:
                        nickname = user_match.group(1)
                        break
        
        metadata['nickname'] = nickname or '未知公众号'
        
        # 2. 提取文章标题 (title)
        title = None
        # 方法1: activity-name
        title_elem = soup.find('h1', {'id': 'activity-name'})
        if title_elem:
            title = title_elem.get_text().strip()
        
        # 方法2: rich_media_title
        if not title:
            title_elem = soup.find('h1', class_='rich_media_title')
            if title_elem:
                title = title_elem.get_text().strip()
        
        # 方法3: og:title
        if not title:
            og_title = soup.find('meta', {'property': 'og:title'})
            if og_title:
                title = og_title.get('content', '')
        
        # 方法4: 从script中提取
        if not title:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    title_match = re.search(r'msg_title\s*=\s*["\'](.*?)["\']', script.string)
                    if title_match:
                        title = title_match.group(1)
                        break
        
        metadata['title'] = title or '无标题'
        
        # 3. 文章链接 (link) - 已经有url参数
        metadata['link'] = url
        
        # 4. 提取发布时间 (publish_time) 和日期 (publish_date)
        publish_time = None
        
        # 方法1: publish_time元素
        time_elem = soup.find('em', id='publish_time')
        if time_elem:
            publish_time = time_elem.get_text().strip()
        
        # 方法2: meta标签
        if not publish_time:
            meta_time = soup.find('meta', {'property': 'og:article:published_time'})
            if meta_time:
                publish_time = meta_time.get('content', '')
        
        # 方法3: script变量
        if not publish_time:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # 尝试多种格式
                    time_patterns = [
                        r'publish_time\s*=\s*["\'](.*?)["\']',
                        r'ct\s*=\s*["\'](.*?)["\']',
                        r'createTime\s*:\s*["\'](.*?)["\']',
                        r'svr_time\s*=\s*["\'](.*?)["\']'
                    ]
                    for pattern in time_patterns:
                        time_match = re.search(pattern, script.string)
                        if time_match:
                            publish_time = time_match.group(1)
                            break
                    if publish_time:
                        break
        
        # 方法4: 从时间戳转换
        if not publish_time:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # 尝试获取时间戳
                    timestamp_match = re.search(r'ct\s*=\s*(\d{10})', script.string)
                    if timestamp_match:
                        timestamp = int(timestamp_match.group(1))
                        publish_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        break
        
        if publish_time:
            metadata['publish_time'] = publish_time
            # 提取日期部分
            try:
                if re.match(r'\d{4}-\d{2}-\d{2}', publish_time):
                    metadata['publish_date'] = publish_time.split(' ')[0]
                elif re.match(r'\d{10}', publish_time):
                    # 如果是时间戳
                    metadata['publish_date'] = datetime.fromtimestamp(int(publish_time)).strftime('%Y-%m-%d')
                else:
                    metadata['publish_date'] = publish_time
            except:
                metadata['publish_date'] = publish_time
        else:
            metadata['publish_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            metadata['publish_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # 5. 提取其他有用信息
        # 提取文章ID相关信息
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # mid
                mid_match = re.search(r'mid\s*=\s*["\']*(\d+)', script.string)
                if mid_match:
                    metadata['mid'] = mid_match.group(1)
                
                # sn
                sn_match = re.search(r'sn\s*=\s*["\']*([a-zA-Z0-9]+)', script.string)
                if sn_match:
                    metadata['sn'] = sn_match.group(1)
                
                # idx
                idx_match = re.search(r'idx\s*=\s*["\']*(\d+)', script.string)
                if idx_match:
                    metadata['idx'] = idx_match.group(1)
                
                # biz
                biz_match = re.search(r'__biz\s*=\s*["\']*([^"\'\s]+)', script.string)
                if biz_match:
                    metadata['biz'] = biz_match.group(1)
                
                # comment_id
                comment_match = re.search(r'comment_id\s*=\s*["\']*(\d+)', script.string)
                if comment_match:
                    metadata['comment_id'] = comment_match.group(1)
                
                # appmsgid
                appmsg_match = re.search(r'appmsgid\s*=\s*["\']*(\d+)', script.string)
                if appmsg_match:
                    metadata['appmsgid'] = appmsg_match.group(1)
        
        # 从URL中提取参数
        if 'mid=' in url:
            mid_match = re.search(r'mid=(\d+)', url)
            if mid_match and 'mid' not in metadata:
                metadata['mid'] = mid_match.group(1)
        
        if 'sn=' in url:
            sn_match = re.search(r'sn=([a-zA-Z0-9]+)', url)
            if sn_match and 'sn' not in metadata:
                metadata['sn'] = sn_match.group(1)
        
        if '__biz=' in url:
            biz_match = re.search(r'__biz=([^&]+)', url)
            if biz_match and 'biz' not in metadata:
                metadata['biz'] = biz_match.group(1)
        
        return metadata
    
    def fetch_article_content(self, soup):
        """提取文章完整内容文本"""
        content_div = soup.find('div', {'id': 'js_content'})
        if not content_div:
            return "", {}
        
        # 获取纯文本内容
        text_content = content_div.get_text(separator='\n', strip=True)
        
        # 获取结构化内容用于关键词权重分析
        structured_content = {
            'title': [],
            'subtitle': [],
            'strong': [],
            'normal': []
        }
        
        # 提取标题文本
        title_elem = soup.find('h1', {'id': 'activity-name'})
        if title_elem:
            structured_content['title'].append(title_elem.get_text().strip())
        
        # 提取所有子标题 (h2, h3, h4)
        for tag in content_div.find_all(['h2', 'h3', 'h4']):
            structured_content['subtitle'].append(tag.get_text().strip())
        
        # 提取所有加粗文本
        for tag in content_div.find_all(['strong', 'b']):
            structured_content['strong'].append(tag.get_text().strip())
        
        # 提取普通段落文本
        for tag in content_div.find_all('p'):
            # 排除已经在strong中的文本
            text = tag.get_text().strip()
            if text and not any(strong in text for strong in structured_content['strong']):
                structured_content['normal'].append(text)
        
        return text_content, structured_content
    
    def analyze_keywords(self, text_content, structured_content, top_k=20):
        """分析关键词并计算加权得分"""
        # 使用jieba进行中文分词
        words = jieba.cut(text_content)
        
        # 统计词频
        word_counts = Counter()
        for word in words:
            # 过滤掉单字和标点符号
            if len(word) > 1 and not re.match(r'^[^\w]+$', word):
                word_counts[word] += 1
        
        # 计算加权得分
        keyword_scores = {}
        
        # 为不同位置的关键词赋予不同权重
        for word, count in word_counts.items():
            score = 0
            
            # 检查关键词在不同位置出现的次数
            for title_text in structured_content['title']:
                if word in title_text:
                    score += self.keyword_weights['title'] * title_text.count(word)
            
            for subtitle_text in structured_content['subtitle']:
                if word in subtitle_text:
                    score += self.keyword_weights['subtitle'] * subtitle_text.count(word)
            
            for strong_text in structured_content['strong']:
                if word in strong_text:
                    score += self.keyword_weights['strong'] * strong_text.count(word)
            
            # 普通文本中的得分
            score += self.keyword_weights['normal'] * count
            
            if score > 0:
                keyword_scores[word] = score
        
        # 获取TF-IDF关键词
        try:
            tfidf_keywords = jieba.analyse.extract_tags(text_content, topK=top_k, withWeight=True)
        except:
            tfidf_keywords = []
        
        # 合并结果
        analysis_result = {
            'keyword_counts': dict(word_counts.most_common(top_k)),
            'keyword_scores': dict(sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]),
            'tfidf_keywords': {word: weight for word, weight in tfidf_keywords},
            'total_words': sum(word_counts.values()),
            'unique_words': len(word_counts)
        }
        
        return analysis_result

    def download_wechat_image(self, img_url, article_image_dir):
        """下载并保存微信公众号图片"""
        try:
            # 微信图片特殊处理
            if 'mmbiz.qpic.cn' in img_url:
                if not img_url.startswith(('http://', 'https://')):
                    img_url = 'https://' + img_url

                # 提取图片格式参数
                fmt_match = re.search(r'wx_fmt=([^&]+)', img_url)
                fmt = fmt_match.group(1) if fmt_match else 'jpeg'

                # 构造高质量图片URL
                if '/0?' in img_url:
                    img_url = img_url.replace('/0?', '/640?')
                elif '?' not in img_url:
                    img_url += '?wx_fmt=' + fmt

                # 添加时间戳防止缓存
                img_url += f'&timestamp={int(time.time())}'

            headers = self.headers.copy()
            response = requests.get(img_url, headers=headers, stream=True, timeout=10)

            if response.status_code == 200:
                # 确定文件扩展名
                content_type = response.headers.get('Content-Type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    ext = '.jpg'  # 默认

                # 生成图片文件名
                img_name = f'{int(time.time() * 1000)}{ext}'
                img_path = os.path.join(article_image_dir, img_name)

                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                return img_name

        except Exception as e:
            print(f"下载微信图片失败: {img_url}, 错误: {str(e)[:100]}")
        return None

    def extract_real_image_url(self, img_element):
        """提取真实的图片URL"""
        for attr in ['data-src', 'src', 'data-original', 'data-wx-src']:
            img_url = img_element.get(attr)
            if img_url:
                if 'mmbiz.qpic.cn' in img_url:
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = 'https://' + img_url
                    return img_url
                elif img_url.startswith('//'):
                    return 'https:' + img_url
                elif img_url.startswith('/'):
                    return 'https://mp.weixin.qq.com' + img_url
                else:
                    return img_url
        return None

    def process_article(self, url):
        """处理单篇文章，提取所有数据"""
        try:
            print(f"\n{'='*50}")
            print(f"开始处理文章: {url}")
            print(f"{'='*50}")

            # 获取文章HTML
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            if response.status_code != 200:
                print(f"无法获取文章: {url}, 状态码: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取所有元数据
            metadata = self.extract_all_metadata(soup, response.text, url)
            
            print(f"\n文章信息:")
            print(f"  公众号: {metadata['nickname']}")
            print(f"  标题: {metadata['title']}")
            print(f"  发布时间: {metadata['publish_time']}")
            
            # 获取文章内容
            text_content, structured_content = self.fetch_article_content(soup)
            metadata['content_length'] = len(text_content)
            
            # 分析关键词
            if text_content:
                print(f"\n正在分析关键词...")
                keyword_analysis = self.analyze_keywords(text_content, structured_content)
                metadata['keyword_analysis'] = keyword_analysis
                
                print(f"  总词数: {keyword_analysis['total_words']}")
                print(f"  独特词数: {keyword_analysis['unique_words']}")
                print(f"  Top 5 关键词 (按得分):")
                for i, (word, score) in enumerate(list(keyword_analysis['keyword_scores'].items())[:5], 1):
                    print(f"    {i}. {word}: {score:.2f}")
            
            # 创建文章目录
            safe_title = self.get_safe_title(metadata['title'])
            article_dir = os.path.join(self.output_dir, safe_title)
            os.makedirs(article_dir, exist_ok=True)
            
            # 创建图片目录
            article_image_dir = os.path.join(article_dir, 'images')
            os.makedirs(article_image_dir, exist_ok=True)

            # 处理文章内容div
            content_div = soup.find('div', {'id': 'js_content'})
            if content_div:
                # 下载并替换图片链接
                img_count = 0
                for img in content_div.find_all('img'):
                    img_url = self.extract_real_image_url(img)
                    if img_url:
                        img_filename = self.download_wechat_image(img_url, article_image_dir)
                        if img_filename:
                            img_count += 1
                            img['src'] = f'images/{img_filename}'
                
                print(f"\n共处理 {img_count} 张图片")
                metadata['image_count'] = img_count

                # 转换为Markdown格式
                html_content = str(content_div)
                markdown_content = self.h.handle(html_content)
            else:
                markdown_content = "未找到文章内容"
                metadata['image_count'] = 0

            # 生成完整的Markdown文档
            full_markdown = self.generate_full_markdown(metadata, markdown_content, text_content)
            
            # 保存Markdown文件
            markdown_path = os.path.join(article_dir, f"{safe_title}.md")
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(full_markdown)
            print(f"\nMarkdown文件已保存: {markdown_path}")
            
            # 保存纯文本内容
            text_path = os.path.join(article_dir, f"{safe_title}_content.txt")
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"纯文本内容已保存: {text_path}")
            
            # 保存完整的元数据JSON
            metadata_path = os.path.join(article_dir, f"{safe_title}_metadata.json")
            # 确保metadata可以JSON序列化
            json_metadata = json.loads(json.dumps(metadata, ensure_ascii=False, default=str))
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(json_metadata, f, ensure_ascii=False, indent=2)
            print(f"元数据已保存: {metadata_path}")
            
            # 保存关键词分析结果
            if 'keyword_analysis' in metadata:
                keywords_path = os.path.join(article_dir, f"{safe_title}_keywords.json")
                with open(keywords_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata['keyword_analysis'], f, ensure_ascii=False, indent=2)
                print(f"关键词分析已保存: {keywords_path}")
            
            print(f"\n{'='*50}")
            print(f"文章处理完成!")
            print(f"{'='*50}")
            
            return metadata

        except Exception as e:
            print(f"\n处理文章 {url} 时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_full_markdown(self, metadata, markdown_content, text_content_preview=""):
        """生成完整的Markdown文档"""
        md = f"# {metadata['title']}\n\n"
        
        # 文章信息表格
        md += "## 文章信息\n\n"
        md += "| 项目 | 内容 |\n"
        md += "|------|------|\n"
        md += f"| 公众号名称 | {metadata['nickname']} |\n"
        md += f"| 文章标题 | {metadata['title']} |\n"
        md += f"| 发布时间 | {metadata['publish_time']} |\n"
        md += f"| 发布日期 | {metadata['publish_date']} |\n"
        md += f"| 文章链接 | [点击查看]({metadata['link']}) |\n"
        
        if 'biz' in metadata:
            md += f"| 公众号ID | {metadata.get('biz', 'N/A')} |\n"
        if 'mid' in metadata:
            md += f"| 文章MID | {metadata.get('mid', 'N/A')} |\n"
        if 'sn' in metadata:
            md += f"| 文章SN | {metadata.get('sn', 'N/A')} |\n"
        if 'idx' in metadata:
            md += f"| 文章索引 | {metadata.get('idx', 'N/A')} |\n"
        
        md += f"| 内容长度 | {metadata.get('content_length', 0)} 字符 |\n"
        md += f"| 图片数量 | {metadata.get('image_count', 0)} 张 |\n"
        md += f"| 抓取时间 | {metadata['crawl_time']} |\n"
        md += "\n"
        
        # 关键词分析
        if 'keyword_analysis' in metadata:
            analysis = metadata['keyword_analysis']
            md += "## 关键词分析\n\n"
            
            md += "### 统计信息\n"
            md += f"- 总词数: {analysis['total_words']}\n"
            md += f"- 独特词数: {analysis['unique_words']}\n\n"
            
            md += "### Top 10 关键词（按加权得分）\n\n"
            md += "| 排名 | 关键词 | 得分 |\n"
            md += "|------|--------|------|\n"
            for i, (word, score) in enumerate(list(analysis['keyword_scores'].items())[:10], 1):
                md += f"| {i} | {word} | {score:.2f} |\n"
            md += "\n"
            
            md += "### Top 10 关键词（按出现次数）\n\n"
            md += "| 排名 | 关键词 | 次数 |\n"
            md += "|------|--------|------|\n"
            for i, (word, count) in enumerate(list(analysis['keyword_counts'].items())[:10], 1):
                md += f"| {i} | {word} | {count} |\n"
            md += "\n"
            
            if analysis.get('tfidf_keywords'):
                md += "### TF-IDF 关键词\n\n"
                md += "| 排名 | 关键词 | 权重 |\n"
                md += "|------|--------|------|\n"
                for i, (word, weight) in enumerate(list(analysis['tfidf_keywords'].items())[:10], 1):
                    md += f"| {i} | {word} | {weight:.4f} |\n"
                md += "\n"
        
        md += "---\n\n"
        md += "## 文章内容\n\n"
        md += markdown_content
        
        # 评论区
        md += "\n\n---\n\n"
        md += "## 评论区\n\n"
        if metadata.get('comment_id'):
            md += f"评论ID: {metadata['comment_id']}\n\n"
            md += "注：微信公众号评论需要通过特殊接口获取完整内容。\n"
        else:
            md += "暂无评论或评论已关闭\n"
        
        return md

    def read_urls_from_file(self, file_path='urls.txt'):
        """从文本文件读取URL列表，自动去重并跳过已抓取的文章"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []
        
        # 去重
        unique_urls = list(dict.fromkeys(all_urls))
        if len(unique_urls) < len(all_urls):
            print(f"发现重复URL，已去重：{len(all_urls)} -> {len(unique_urls)}")
        
        # 检查已抓取的文章
        processed_urls = self.get_processed_urls()
        new_urls = []
        
        for url in unique_urls:
            if url in processed_urls:
                print(f"跳过已抓取: {url}")
            else:
                new_urls.append(url)
        
        # 更新urls.txt文件，只保留未处理的URL
        if len(new_urls) < len(unique_urls):
            with open(file_path, 'w', encoding='utf-8') as f:
                for url in new_urls:
                    f.write(url + '\n')
            print(f"已更新{file_path}，移除已处理的URL")
        
        return new_urls
    
    def get_processed_urls(self):
        """获取已经处理过的URL列表"""
        processed_urls = set()
        
        # 检查每个子目录的metadata.json文件
        if os.path.exists(self.output_dir):
            for item in os.listdir(self.output_dir):
                item_path = os.path.join(self.output_dir, item)
                if os.path.isdir(item_path):
                    # 查找metadata.json文件
                    metadata_files = [f for f in os.listdir(item_path) if f.endswith('_metadata.json')]
                    for metadata_file in metadata_files:
                        metadata_path = os.path.join(item_path, metadata_file)
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                if 'url' in metadata:
                                    processed_urls.add(metadata['url'])
                        except:
                            continue
        
        return processed_urls
    
    def generate_summary_report(self, all_metadata):
        """生成汇总报告"""
        if not all_metadata:
            return
        
        report_path = os.path.join(self.output_dir, 'summary_report.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 微信文章抓取汇总报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"总计抓取文章数: {len(all_metadata)}\n\n")
            
            f.write("## 文章列表\n\n")
            f.write("| 序号 | 公众号 | 标题 | 发布时间 | 词数 | 图片数 |\n")
            f.write("|------|--------|------|----------|------|--------|\n")
            
            for i, meta in enumerate(all_metadata, 1):
                f.write(f"| {i} | {meta['nickname']} | {meta['title'][:30]}{'...' if len(meta['title']) > 30 else ''} | ")
                f.write(f"{meta['publish_time']} | {meta.get('content_length', 0)} | {meta.get('image_count', 0)} |\n")
            
            f.write("\n## 公众号统计\n\n")
            nickname_counts = Counter(meta['nickname'] for meta in all_metadata)
            f.write("| 公众号 | 文章数 |\n")
            f.write("|--------|--------|\n")
            for nickname, count in nickname_counts.most_common():
                f.write(f"| {nickname} | {count} |\n")
        
        print(f"\n汇总报告已生成: {report_path}")


if __name__ == "__main__":
    crawler = WeChatArticleAdvancedCrawler()
    
    try:
        article_urls = crawler.read_urls_from_file('urls.txt')
        print(f"从文件读取到 {len(article_urls)} 个URL")
    except FileNotFoundError:
        print("未找到urls.txt文件，请创建该文件并每行放入一个URL")
        exit()
    
    all_metadata = []
    for url in article_urls:
        metadata = crawler.process_article(url)
        if metadata:
            all_metadata.append(metadata)
        time.sleep(2)  # 添加延迟避免被封
    
    # 生成汇总报告
    crawler.generate_summary_report(all_metadata)