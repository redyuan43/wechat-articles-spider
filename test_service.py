#!/usr/bin/env python3
"""
NAS服务测试脚本
用于测试服务的基本功能
"""

import sys
import os
import time

def test_dependencies():
    """测试依赖包"""
    print("🔍 测试Python依赖包...")
    
    required_packages = [
        ('requests', '网络请求'),
        ('bs4', 'HTML解析'),
        ('html2text', 'HTML转Markdown'),
        ('jieba', '中文分词'),
        ('watchdog', '文件监听'),
        ('flask', 'Web服务')
    ]
    
    missing = []
    for package, desc in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} ({desc})")
        except ImportError:
            print(f"❌ {package} ({desc}) - 缺失")
            missing.append(package)
    
    return len(missing) == 0

def test_file_access():
    """测试文件访问权限"""
    print("\n📁 测试文件访问权限...")
    
    test_files = [
        ('simple_nas_service.py', '主服务文件'),
        ('wechat_crawler.py', '爬虫核心文件')
    ]
    
    all_good = True
    for filename, desc in test_files:
        if os.path.exists(filename):
            if os.access(filename, os.R_OK):
                print(f"✅ {filename} ({desc}) - 可读")
            else:
                print(f"❌ {filename} ({desc}) - 权限不足")
                all_good = False
        else:
            print(f"❌ {filename} ({desc}) - 文件不存在")
            all_good = False
    
    return all_good

def test_url_extraction():
    """测试URL提取功能"""
    print("\n🔗 测试URL提取功能...")
    
    try:
        sys.path.append('.')
        from simple_nas_service import SimpleNASService
        
        service = SimpleNASService()
        
        test_content = """
        这是一些测试内容
        https://mp.weixin.qq.com/s/abcdefg123456
        还有其他内容
        https://mp.weixin.qq.com/s?__biz=xxx&mid=123&idx=1
        """
        
        urls = service.extract_urls(test_content)
        
        if len(urls) >= 2:
            print("✅ URL提取功能正常")
            for url in urls:
                print(f"   发现URL: {url}")
            return True
        else:
            print("❌ URL提取功能异常")
            return False
            
    except Exception as e:
        print(f"❌ URL提取测试失败: {e}")
        return False

def test_directories():
    """测试目录创建"""
    print("\n📂 测试目录创建...")
    
    test_dirs = ['wechat_articles', 'test_temp']
    
    try:
        for dirname in test_dirs:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
                print(f"✅ 创建目录: {dirname}")
            else:
                print(f"✅ 目录已存在: {dirname}")
        
        # 清理测试目录
        if os.path.exists('test_temp'):
            os.rmdir('test_temp')
            print("🧹 清理测试目录")
        
        return True
        
    except Exception as e:
        print(f"❌ 目录测试失败: {e}")
        return False

def test_network():
    """测试网络连接"""
    print("\n🌐 测试网络连接...")
    
    try:
        import requests
        
        # 测试访问微信公众号域名
        response = requests.head('https://mp.weixin.qq.com/', timeout=10)
        
        if response.status_code in [200, 301, 302, 403]:
            print("✅ 网络连接正常")
            return True
        else:
            print(f"⚠️ 网络连接异常，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 网络测试失败: {e}")
        return False

def main():
    print("="*50)
    print("🧪 NAS微信文章服务 - 功能测试")
    print("="*50)
    
    tests = [
        ("依赖包检查", test_dependencies),
        ("文件权限检查", test_file_access), 
        ("目录操作测试", test_directories),
        ("URL提取测试", test_url_extraction),
        ("网络连接测试", test_network)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 出现异常: {e}")
    
    print("\n" + "="*50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    print("="*50)
    
    if passed == total:
        print("🎉 所有测试通过！可以开始安装服务")
        print("\n下一步: 运行 ./install_nas.sh 进行安装")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查环境配置")
        print("\n建议:")
        if passed < 2:
            print("- 先安装Python依赖: pip3 install requests beautifulsoup4 html2text jieba watchdog flask")
        print("- 检查文件权限和网络连接")
        print("- 解决问题后重新运行测试")
        return 1

if __name__ == '__main__':
    sys.exit(main())