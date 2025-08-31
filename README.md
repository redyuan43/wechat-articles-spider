# 🏠 微信文章转换服务 - NAS版

一键部署到NAS的微信公众号文章爬虫服务，支持自动转换为Markdown格式并提取完整数据。

## 📸 预览

![NAS服务概览](https://via.placeholder.com/800x400/4CAF50/white?text=NAS+WeChat+Article+Service)

## 🌟 功能特点

- 🎯 **极简操作**: 只需编辑一个`urls.txt`文件，粘贴URL即可
- 🔄 **自动处理**: 文件保存后立即开始转换，完成后自动清空
- 📊 **完整数据提取**: 
  - 公众号名称 (nickname)
  - 文章标题 (title)
  - 发布时间 (publish_time)
  - 文章内容分析 (content analysis)
  - 关键词统计和加权得分 (keyword analysis)
  - 图片自动下载和本地化
- 🌐 **Web监控界面**: 实时查看处理状态和统计信息
- 🖥️ **系统服务**: 开机自启动，崩溃自动重启
- 💾 **低资源占用**: 专为NAS环境优化，内存占用约50-100MB

## 🚀 快速开始

### 1️⃣ 环境要求
- Debian/Ubuntu NAS系统
- Python 3.6+
- 网络连接

### ⚡ 部署状态
```bash
✅ 核心功能已完成并测试
✅ NAS服务架构已优化  
✅ 安装脚本已验证
⚠️ 需要手动解决端口冲突 (端口8080)
✅ 虚拟环境配置完成
✅ Web界面功能正常
```

### 2️⃣ 一键安装
```bash
# 下载项目到NAS
git clone https://github.com/your-repo/wechat-articles-spider.git
cd wechat-articles-spider

# 运行安装脚本
chmod +x install_nas.sh
./install_nas.sh
```

### 3️⃣ 启动服务
```bash
# 启动服务
./service_control.sh start

# 查看状态
./service_control.sh status
```

### 4️⃣ 开始使用
1. 访问Web界面: `http://你的NAS的IP:8080`
2. 编辑 `urls.txt` 文件，粘贴微信文章URL
3. 保存文件，服务自动开始处理
4. 查看转换结果在 `wechat_articles/` 目录

## 📱 手机操作方式

### 方式1: NAS文件管理器
- 使用Synology File Station、QNAP File Manager等
- 直接编辑 `urls.txt` 文件

### 方式2: 网络共享 (推荐)
- 通过Samba/SMB访问NAS文件夹
- 手机文件管理器编辑文件

### 方式3: 云盘同步
- 设置OneDrive、Google Drive等同步到NAS
- 手机编辑云盘中的文件，自动同步

### 方式4: SSH终端
```bash
echo "https://mp.weixin.qq.com/s/文章ID" >> urls.txt
```

## 📁 文件结构

```
wechat-articles-spider/
├── 🔧 核心程序
│   ├── simple_nas_service.py      # 主服务程序
│   └── wechat_crawler.py          # 爬虫核心
├── 📋 管理脚本
│   ├── install_nas.sh             # 一键安装脚本
│   ├── service_control.sh         # 服务控制脚本
│   ├── test_service.py           # 功能测试脚本
│   └── demo.py                   # 功能演示脚本
├── 📝 配置文件
│   ├── urls.txt                  # URL输入文件
│   └── service.log              # 服务日志
├── 📚 文档
│   ├── README.md                # 项目总览 (本文件)
│   └── README_NAS.md            # 详细部署文档
└── 📂 输出目录
    └── wechat_articles/         # 转换结果
        ├── 文章标题1/
        │   ├── 文章标题1.md          # 完整Markdown文档
        │   ├── 文章标题1_content.txt # 纯文本内容
        │   ├── 文章标题1_metadata.json # 完整元数据
        │   ├── 文章标题1_keywords.json # 关键词分析
        │   └── images/              # 文章图片
        └── summary_report.md        # 批量处理汇总报告
```

## 🎮 服务管理

### 快速命令
```bash
# 启动服务
./service_control.sh start

# 停止服务  
./service_control.sh stop

# 重启服务
./service_control.sh restart

# 查看状态
./service_control.sh status

# 查看日志
./service_control.sh logs

# 显示Web地址
./service_control.sh web
```

### 系统服务命令
```bash
sudo systemctl start wechat-crawler      # 启动
sudo systemctl stop wechat-crawler       # 停止
sudo systemctl status wechat-crawler     # 状态
sudo systemctl enable wechat-crawler     # 开机启动
```

## 📊 数据提取示例

### 提取的元数据
```json
{
  "nickname": "AI小小将",
  "title": "谷歌给nano-banana出了官方提示词指南！",
  "publish_time": "2025-08-31 15:30:25",
  "publish_date": "2025-08-31",
  "link": "https://mp.weixin.qq.com/s/xxxxxx",
  "content_length": 4073,
  "image_count": 22
}
```

### 关键词分析
```json
{
  "keyword_counts": {
    "AI": 72,
    "图像": 35,
    "生成": 29
  },
  "keyword_scores": {
    "AI": 75.00,
    "图像": 38.00,
    "生成": 29.00
  },
  "tfidf_keywords": {
    "AI": 0.8151,
    "图像": 0.2792,
    "生成": 0.1227
  }
}
```

## 🌐 Web界面功能

访问 `http://你的NAS的IP:8080` 查看：

- 📈 **实时统计**: 处理总数、成功率、运行时间
- 📊 **当前状态**: 正在处理的任务进度
- 📋 **使用指南**: 详细的操作说明
- 📁 **文件路径**: 显示关键文件位置
- 🔄 **自动更新**: 每2秒刷新状态

## 🔧 高级配置

### 修改配置
编辑 `simple_nas_service.py` 中的配置：

```python
self.config = {
    "urls_file": "urls.txt",           # URL文件名
    "output_dir": "wechat_articles",   # 输出目录
    "web_port": 8080,                  # Web端口
    "check_interval": 2                # 检查间隔(秒)
}
```

### 自定义输出路径
```python
self.config["output_dir"] = "/volume1/documents/articles"  # Synology示例
```

## 🛠️ 故障排除

### 常见问题

**Q: 服务无法启动**
```bash
# 检查日志
sudo journalctl -u wechat-crawler -f

# 手动测试
python3 simple_nas_service.py
```

**Q: Web界面无法访问**
- 检查防火墙设置
- 确认端口8080未被占用
- 验证NAS网络配置

**Q: URL处理失败**
- 检查网络连接
- 确认URL格式正确 (必须是mp.weixin.qq.com域名)
- 查看service.log日志文件

**Q: 文件权限问题**
```bash
chmod 755 /path/to/project
chmod 644 urls.txt
chown -R username:username /path/to/project
```

### 测试工具
```bash
# 运行功能测试
python3 test_service.py

# 运行功能演示
python3 demo.py
```

## 📈 性能说明

### 资源占用
- **内存**: 50-100MB (空闲时) / 200-300MB (处理时)
- **CPU**: 空闲时极低 / 处理时中等
- **磁盘**: 每篇文章约1-10MB (含图片)
- **网络**: 下载文章和图片时占用带宽

### 处理能力
- **单篇处理时间**: 10-30秒 (取决于文章长度和图片数量)
- **并发处理**: 顺序处理，避免被封IP
- **处理间隔**: 每篇文章间隔1秒
- **稳定性**: 24/7运行，自动重启

## 🎯 最佳实践

### 使用建议
1. **批量处理**: 一次添加3-5个URL，避免过多
2. **定期清理**: 清理旧的文章和图片文件
3. **监控空间**: 关注磁盘空间使用情况
4. **备份重要**: 备份有价值的转换结果

### URL管理技巧
```bash
# 好的URL格式
https://mp.weixin.qq.com/s/bkktSW8A6Tpp1rAZ4P60Jg

# 会自动清理的格式 
https://mp.weixin.qq.com/s?__biz=xxx&mid=123&idx=1&sn=abc
# 👆 自动简化为 👇
https://mp.weixin.qq.com/s/abc
```

## 📞 技术支持

### 获取帮助
- 📖 详细文档: [README_NAS.md](README_NAS.md)
- 🐛 问题反馈: GitHub Issues  
- 💬 交流讨论: 项目Discussions

### 贡献代码
欢迎提交Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📜 更新日志

### v2.0 (当前版本) - 2025-09-01
**🏠 全新NAS专版发布**

#### 🚀 核心功能升级
- ✅ **完全重写服务架构**: 专为NAS环境优化，资源占用降低70%
- ✅ **单文件监听模式**: 只需编辑`urls.txt`文件，自动清空处理
- ✅ **智能URL去重**: 自动识别并跳过已处理的文章
- ✅ **完整数据提取**: 新增公众号名称、发布时间、关键词分析等

#### 🌐 Web界面全新升级
- ✅ **实时监控面板**: 处理状态、统计数据、运行时间
- ✅ **响应式设计**: 完美支持手机、平板访问
- ✅ **自动刷新**: 2秒间隔实时更新状态

#### 🔧 部署和管理优化
- ✅ **一键安装脚本**: `./install_nas.sh` 自动配置环境
- ✅ **系统服务集成**: 开机自启动，崩溃自动重启
- ✅ **便捷管理工具**: `./service_control.sh` 统一管理命令
- ✅ **虚拟环境隔离**: 避免Python包冲突

#### 📱 移动端体验优化
- ✅ **多种操作方式**: NAS文件管理器、Samba共享、云盘同步、SSH
- ✅ **即时处理**: 文件保存后立即开始转换
- ✅ **状态可视**: Web界面实时查看处理进度

#### 🔍 数据分析增强
- ✅ **关键词提取**: TF-IDF算法 + 位置加权得分
- ✅ **内容统计**: 字数统计、图片数量、处理时间
- ✅ **元数据保存**: JSON格式完整保存文章信息
- ✅ **批量报告**: 自动生成处理汇总报告

#### 🛠️ 技术栈更新
- ✅ **文件监听**: Watchdog实时监听文件变化
- ✅ **Web框架**: Flask轻量级Web服务
- ✅ **中文分词**: Jieba分词 + 自定义词典
- ✅ **HTML解析**: BeautifulSoup4最新版

#### 📊 性能提升
- **启动时间**: 3秒内完成初始化
- **内存占用**: 空闲50MB，处理时200MB
- **处理速度**: 单篇文章10-30秒
- **并发能力**: 队列处理，支持批量任务

#### 🐛 问题修复
- ✅ 修复图片路径问题，支持相对路径显示
- ✅ 修复中文文件名处理
- ✅ 修复重复URL检测逻辑
- ✅ 修复依赖包安装问题

### v1.0 (原版本)
- ✅ 基础爬虫功能
- ✅ Markdown转换
- ✅ 图片下载

## 📄 许可证

本项目基于 MIT 许可证开源。

## 🙏 致谢

感谢以下开源项目：
- [Watchdog](https://github.com/gorakhargosh/watchdog) - 文件系统监听
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [Jieba](https://github.com/fxsjy/jieba) - 中文分词

---

<div align="center">

**🎉 享受自动化的微信文章收集体验！**

Made with ❤️ for NAS Users

</div>