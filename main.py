import os
import re
import requests
from bs4 import BeautifulSoup
import html2text
from datetime import datetime
import time


class WeChatArticleCrawler:
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

    def get_safe_title(self, title):
        safe_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]
        return safe_title.strip()

    # 下载并保存微信公众号图片到文章对应的图片目录
    def download_wechat_image(self, img_url, article_image_dir):
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

                return img_name  # 只返回文件名，不包含路径

        except Exception as e:
            print(f"下载微信图片失败: {img_url}, 错误: {str(e)[:100]}")
        return None

    def extract_real_image_url(self, img_element):
        # 尝试多种可能的属性
        for attr in ['data-src', 'src', 'data-original', 'data-wx-src']:
            img_url = img_element.get(attr)
            if img_url:
                # 处理微信的图片URL
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
        # 处理单篇文章
        try:
            print(f"\n开始处理文章: {url}")

            # 获取文章HTML
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            if response.status_code != 200:
                print(f"无法获取文章: {url}, 状态码: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取文章标题
            title = soup.find('h1', {'id': 'activity-name'})
            title = title.get_text().strip() if title else '无标题'
            safe_title = self.get_safe_title(title)
            print(f"文章标题: {title}")

            # 提取发布日期
            date = soup.find('em', id='publish_time')
            date = date.get_text().strip() if date else datetime.now().strftime('%Y-%m-%d')

            # 创建文章对应的图片目录
            article_image_dir = os.path.join(self.output_dir, 'images', safe_title)
            os.makedirs(article_image_dir, exist_ok=True)

            # 处理图片
            content_div = soup.find('div', {'id': 'js_content'})
            if not content_div:
                print(f"未找到文章内容: {url}")
                return None

            # 下载并替换图片链接
            img_count = 0
            for img in content_div.find_all('img'):
                img_url = self.extract_real_image_url(img)
                if img_url:
                    print(f"发现图片: {img_url}")
                    img_filename = self.download_wechat_image(img_url, article_image_dir)
                    if img_filename:
                        img_count += 1
                        # 在Markdown中使用相对路径
                        img['src'] = f'/images/{safe_title}/{img_filename}'
                        print(f"图片下载成功: {img_filename}")
                    else:
                        print("图片下载失败")
                else:
                    print("未找到有效的图片URL")

            print(f"共处理 {img_count} 张图片")

            # 转换为Markdown格式
            html_content = str(content_div)
            markdown_content = self.h.handle(html_content)

            # 添加标题和日期
            markdown_content = f"# {title}\n\n发布时间: {date}\n\n{markdown_content}"

            # 保存文章(Markdown文件放在根目录)
            article_filename = f"{safe_title}.md"
            article_path = os.path.join(self.output_dir, article_filename)

            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"成功保存文章: {article_path}")
            return article_path

        except Exception as e:
            print(f"处理文章 {url} 时出错: {e}")
            return None

    def read_urls_from_file(self, file_path='urls.txt'):
        # 从文本文件读取URL列表
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls


if __name__ == "__main__":
    # 使用示例
    crawler = WeChatArticleCrawler()

    # 从urls.txt文件读取URL列表
    try:
        article_urls = crawler.read_urls_from_file('urls.txt')
        print(f"从文件读取到 {len(article_urls)} 个URL")
    except FileNotFoundError:
        print("未找到urls.txt文件，请创建该文件并每行放入一个URL")
        exit()

    for url in article_urls:
        crawler.process_article(url)
        time.sleep(2)  # 添加延迟避免被封