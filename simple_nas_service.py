#!/usr/bin/env python3
"""
NAS微信文章爬虫服务 - 简化版
监听单个urls.txt文件，处理完后自动清空
专为Debian NAS系统设计
"""

import os
import sys
import time
import json
import logging
import threading
import re
from datetime import datetime
from pathlib import Path
from typing import List

# 检查并安装依赖
def install_dependencies():
    """检查并安装必要的依赖"""
    required = ['flask', 'requests', 'beautifulsoup4', 'html2text', 'jieba']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"📦 正在安装依赖: {', '.join(missing)}")
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        except:
            print(f"⚠️ 请手动安装: pip install {' '.join(missing)}")
            return False
    return True

# 安装依赖
if not install_dependencies():
    sys.exit(1)

from flask import Flask, render_template_string, jsonify
from wechat_crawler import WeChatArticleAdvancedCrawler

class SimpleNASService:
    def __init__(self):
        self.config = {
            "urls_file": "urls.txt",
            "output_dir": "wechat_articles", 
            "log_file": "service.log",
            "web_port": 8080,
            "check_interval": 2
        }
        
        self.setup_logging()
        self.crawler = WeChatArticleAdvancedCrawler(output_dir=self.config['output_dir'])
        self.stats = {
            'total_processed': 0,
            'success_count': 0,
            'last_processed': None,
            'service_start_time': datetime.now()
        }
        self.current_status = "等待文件更新..."
        
        # 确保文件存在
        if not os.path.exists(self.config['urls_file']):
            with open(self.config['urls_file'], 'w', encoding='utf-8') as f:
                f.write("")
        
        self.logger.info("🚀 服务初始化完成")
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_urls(self, content: str) -> List[str]:
        """提取微信文章URL"""
        patterns = [
            r'https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_\-]+',
            r'https://mp\.weixin\.qq\.com/s\?[^"\s\n]+',
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            urls.extend(matches)
        
        # 去重并清理
        unique_urls = []
        for url in urls:
            clean_url = url.split('?')[0] if '?' in url else url
            if clean_url not in unique_urls:
                unique_urls.append(clean_url)
        
        return unique_urls
    
    def process_urls_file(self):
        """处理urls.txt文件"""
        try:
            # 读取文件内容
            with open(self.config['urls_file'], 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                return  # 文件为空，无需处理
            
            self.logger.info("📁 检测到URLs文件更新")
            self.current_status = "正在提取URLs..."
            
            # 提取URL
            urls = self.extract_urls(content)
            
            if not urls:
                self.logger.info("⚠️ 未找到有效的微信文章URL")
                self.clear_urls_file()
                return
            
            self.logger.info(f"🔗 发现 {len(urls)} 个URL，开始处理...")
            self.current_status = f"正在处理 {len(urls)} 个URL..."
            
            # 处理每个URL
            success_count = 0
            for i, url in enumerate(urls, 1):
                self.current_status = f"正在处理 {i}/{len(urls)}: {url[:50]}..."
                self.logger.info(f"🚀 [{i}/{len(urls)}] 处理: {url}")
                
                try:
                    result = self.crawler.process_article(url)
                    if result:
                        success_count += 1
                        self.logger.info(f"✅ [{i}/{len(urls)}] 成功: {url}")
                    else:
                        self.logger.error(f"❌ [{i}/{len(urls)}] 失败: {url}")
                except Exception as e:
                    self.logger.error(f"❌ [{i}/{len(urls)}] 异常: {url} - {e}")
                
                # 添加延迟避免被封
                time.sleep(1)
            
            # 更新统计
            self.stats['total_processed'] += len(urls)
            self.stats['success_count'] += success_count
            self.stats['last_processed'] = datetime.now()
            
            # 清空文件
            self.clear_urls_file()
            
            self.current_status = f"✅ 完成处理 {len(urls)} 个URL，成功 {success_count} 个"
            self.logger.info(f"🎉 批次处理完成: {success_count}/{len(urls)} 成功")
            
        except Exception as e:
            self.current_status = f"❌ 处理出错: {str(e)}"
            self.logger.error(f"❌ 处理URLs文件时出错: {e}")
    
    def clear_urls_file(self):
        """清空URLs文件"""
        try:
            with open(self.config['urls_file'], 'w', encoding='utf-8') as f:
                f.write("")
            self.logger.info("🧹 URLs文件已清空")
        except Exception as e:
            self.logger.error(f"❌ 清空文件失败: {e}")

class URLFileChecker:
    def __init__(self, service):
        self.service = service
        self.last_size = 0
        self.checking = False
    
    def check_file_not_empty(self):
        """检查文件是否非空"""
        try:
            urls_file = self.service.config['urls_file']
            if os.path.exists(urls_file):
                file_size = os.path.getsize(urls_file)
                return file_size > 0
            return False
        except Exception as e:
            self.service.logger.error(f"❌ 检查文件大小失败: {e}")
            return False
    
    def start_checking(self):
        """开始定期检查文件"""
        self.checking = True
        while self.checking:
            try:
                if self.check_file_not_empty():
                    # 文件不为空，处理URLs
                    threading.Thread(target=self.service.process_urls_file, daemon=True).start()
                    # 等待处理完成后再继续检查
                    time.sleep(5)
                else:
                    # 文件为空，正常等待
                    time.sleep(self.service.config['check_interval'])
            except Exception as e:
                self.service.logger.error(f"❌ 文件检查异常: {e}")
                time.sleep(self.service.config['check_interval'])
    
    def stop_checking(self):
        """停止检查"""
        self.checking = False

def create_web_app(service):
    """创建Web界面"""
    app = Flask(__name__)
    
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NAS微信文章服务</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f7;
            }
            .container {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            h1 {
                color: #1d1d1f;
                margin-bottom: 30px;
                text-align: center;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }
            .stat-number {
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .status-section {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .current-status {
                background: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 6px;
                padding: 15px;
                margin: 15px 0;
                font-weight: 500;
            }
            .file-info {
                background: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 6px;
                padding: 15px;
                margin: 15px 0;
                font-family: monospace;
            }
            .instructions {
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 6px;
                padding: 20px;
                margin: 20px 0;
            }
            .log-section {
                max-height: 300px;
                overflow-y: auto;
                background: #f1f1f1;
                padding: 15px;
                border-radius: 6px;
                font-family: monospace;
                font-size: 12px;
                white-space: pre-line;
            }
        </style>
        <script>
            function updateStatus() {
                fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-processed').textContent = data.total_processed;
                    document.getElementById('success-count').textContent = data.success_count;
                    document.getElementById('current-status').textContent = data.current_status;
                    document.getElementById('last-processed').textContent = data.last_processed || '无';
                    document.getElementById('uptime').textContent = data.uptime;
                });
            }
            
            setInterval(updateStatus, 2000);
            updateStatus();
        </script>
    </head>
    <body>
        <div class="container">
            <h1>📱 NAS微信文章转换服务</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-processed">0</div>
                    <div class="stat-label">总处理数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="success-count">0</div>
                    <div class="stat-label">成功处理</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="uptime">0</div>
                    <div class="stat-label">运行时间</div>
                </div>
            </div>
            
            <div class="status-section">
                <h3>📊 当前状态</h3>
                <div class="current-status" id="current-status">
                    等待文件更新...
                </div>
                <p><strong>最后处理时间:</strong> <span id="last-processed">无</span></p>
            </div>
            
            <div class="instructions">
                <h3>📝 使用方法</h3>
                <ol>
                    <li><strong>在NAS上找到文件:</strong>
                        <div class="file-info">{{ urls_file_path }}</div>
                    </li>
                    <li><strong>添加URL:</strong> 将微信文章链接粘贴到文件中（每行一个）</li>
                    <li><strong>保存文件:</strong> 服务会自动检测文件变化并开始处理</li>
                    <li><strong>查看结果:</strong> 转换后的Markdown文件保存在：
                        <div class="file-info">{{ output_dir_path }}</div>
                    </li>
                </ol>
                
                <h4>💡 手机操作技巧</h4>
                <ul>
                    <li>通过NAS的文件管理App直接编辑urls.txt</li>
                    <li>通过Samba/FTP访问并编辑文件</li>
                    <li>通过云盘同步到NAS文件夹</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(
            HTML_TEMPLATE,
            urls_file_path=os.path.abspath(service.config['urls_file']),
            output_dir_path=os.path.abspath(service.config['output_dir'])
        )
    
    @app.route('/api/status')
    def get_status():
        uptime = datetime.now() - service.stats['service_start_time']
        uptime_str = f"{uptime.days}天{uptime.seconds//3600}时{(uptime.seconds%3600)//60}分"
        
        return jsonify({
            'total_processed': service.stats['total_processed'],
            'success_count': service.stats['success_count'],
            'current_status': service.current_status,
            'last_processed': service.stats['last_processed'].strftime('%Y-%m-%d %H:%M:%S') if service.stats['last_processed'] else None,
            'uptime': uptime_str
        })
    
    return app

def main():
    print("\n" + "="*50)
    print("🏠 NAS微信文章转换服务")
    print("="*50)
    
    try:
        # 创建服务
        service = SimpleNASService()
        
        print(f"\n📁 监听文件: {os.path.abspath(service.config['urls_file'])}")
        print(f"📁 输出目录: {os.path.abspath(service.config['output_dir'])}")
        print(f"🌐 Web端口: {service.config['web_port']}")
        
        # 设置文件定期检查
        file_checker = URLFileChecker(service)
        checker_thread = threading.Thread(target=file_checker.start_checking, daemon=True)
        checker_thread.start()
        service.logger.info("👀 文件定期检查已启动")
        
        # 启动Web界面
        app = create_web_app(service)
        web_thread = threading.Thread(
            target=lambda: app.run(
                host='0.0.0.0',
                port=service.config['web_port'],
                debug=False,
                use_reloader=False
            ),
            daemon=True
        )
        web_thread.start()
        service.logger.info(f"🌐 Web界面已启动")
        
        print(f"\n✅ 服务启动成功！")
        print(f"📱 Web访问: http://你的NAS的IP:{service.config['web_port']}")
        print(f"📝 编辑文件: {os.path.abspath(service.config['urls_file'])}")
        print(f"📊 日志文件: {service.config['log_file']}")
        print("\n使用方法: 将微信文章URL添加到urls.txt文件中，保存后自动处理")
        print("按 Ctrl+C 停止服务")
        print("="*50 + "\n")
        
        # 保持服务运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 正在停止服务...")
            file_checker.stop_checking()
            service.logger.info("服务已停止")
        
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        return 1

if __name__ == '__main__':
    main()