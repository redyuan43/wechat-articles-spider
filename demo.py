#!/usr/bin/env python3
"""
NAS服务功能演示
展示核心功能如何工作
"""

import sys
import os
import time
from datetime import datetime

# 确保可以导入我们的模块
sys.path.append('.')

try:
    from simple_nas_service import SimpleNASService
    print("✅ 成功导入NAS服务模块")
except Exception as e:
    print(f"❌ 导入服务模块失败: {e}")
    sys.exit(1)

def demo_url_extraction():
    """演示URL提取功能"""
    print("\n" + "="*50)
    print("🔗 演示URL提取功能")
    print("="*50)
    
    service = SimpleNASService()
    
    # 测试不同格式的URL
    test_content = """
    这里是一些测试内容：
    
    标准URL：https://mp.weixin.qq.com/s/bkktSW8A6Tpp1rAZ4P60Jg
    带参数的URL：https://mp.weixin.qq.com/s?__biz=MzA3MDMwOTcwMg==&mid=2649004894&idx=1&sn=abc123
    
    还有其他内容...
    
    另一个URL：https://mp.weixin.qq.com/s/xyz789
    """
    
    print("📝 输入内容:")
    print(test_content)
    
    urls = service.extract_urls(test_content)
    
    print(f"\n🎯 提取结果: 发现 {len(urls)} 个URL")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")

def demo_file_monitoring():
    """演示文件监听功能"""
    print("\n" + "="*50)
    print("📁 演示文件监听功能")
    print("="*50)
    
    # 创建测试文件
    test_file = "demo_urls.txt"
    
    print(f"📝 创建测试文件: {test_file}")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("https://mp.weixin.qq.com/s/demo123456\n")
        f.write("https://mp.weixin.qq.com/s/demo789012\n")
    
    print("✅ 文件已创建，内容:")
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    # 模拟处理过程
    service = SimpleNASService()
    service.config['urls_file'] = test_file
    
    print("🔄 模拟处理过程...")
    
    # 读取和提取URL
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    urls = service.extract_urls(content)
    print(f"🔗 提取到 {len(urls)} 个URL:")
    for url in urls:
        print(f"   - {url}")
    
    # 模拟清空文件
    print("🧹 处理完成，清空文件...")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("")
    
    print("✅ 文件已清空")
    
    # 清理测试文件
    os.remove(test_file)
    print("🗑️ 清理测试文件")

def demo_stats():
    """演示统计功能"""
    print("\n" + "="*50)
    print("📊 演示统计功能")  
    print("="*50)
    
    service = SimpleNASService()
    
    # 模拟一些统计数据
    service.stats['total_processed'] = 15
    service.stats['success_count'] = 12
    service.stats['last_processed'] = datetime.now()
    service.stats['service_start_time'] = datetime.now()
    
    print("📈 当前统计:")
    print(f"   总处理数: {service.stats['total_processed']}")
    print(f"   成功数: {service.stats['success_count']}")
    print(f"   成功率: {service.stats['success_count']/service.stats['total_processed']*100:.1f}%")
    print(f"   最后处理: {service.stats['last_processed'].strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    print("🎬 NAS微信文章服务功能演示")
    print("="*60)
    
    try:
        # 演示各项功能
        demo_url_extraction()
        demo_file_monitoring() 
        demo_stats()
        
        print("\n" + "="*60)
        print("🎉 演示完成！")
        print("="*60)
        
        print("\n📋 部署步骤:")
        print("1. 运行测试: python3 test_service.py")
        print("2. 安装服务: ./install_nas.sh")
        print("3. 启动服务: ./service_control.sh start")
        print("4. 访问界面: http://你的NAS的IP:8080")
        print("5. 编辑文件: urls.txt")
        
        print("\n💡 使用提示:")
        print("- 将微信文章URL粘贴到urls.txt文件")
        print("- 保存文件后自动开始处理")
        print("- 处理完成后文件会自动清空")
        print("- 转换结果保存在wechat_articles目录")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 演示过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())