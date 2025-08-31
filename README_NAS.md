# 🏠 NAS微信文章转换服务部署指南

专为 Debian NAS 系统设计的微信公众号文章爬虫服务

## 📋 功能特点

- ✅ **单文件监听**: 只需编辑一个 `urls.txt` 文件
- ✅ **自动清空**: 处理完成后自动清空URL文件
- ✅ **完整数据提取**: 提取标题、作者、发布时间、关键词等
- ✅ **图片下载**: 自动下载并本地化图片
- ✅ **Web界面**: 实时查看处理状态和统计
- ✅ **系统服务**: 开机自启动，崩溃自动重启
- ✅ **低资源占用**: 专为NAS环境优化

## 🚀 快速安装

### 1. 准备环境
```bash
# SSH登录到你的NAS
ssh username@你的NAS的IP

# 下载项目文件到NAS
# (将项目文件上传到NAS，或使用git clone)
```

### 2. 一键安装
```bash
# 进入项目目录
cd wechat-articles-spider

# 给安装脚本执行权限
chmod +x install_nas.sh service_control.sh

# 运行安装脚本
./install_nas.sh
```

### 3. 启动服务
```bash
# 使用控制脚本启动
./service_control.sh start

# 或直接使用systemctl
sudo systemctl start wechat-crawler
```

## 📱 使用方法

### 方式1: 通过NAS文件管理器
1. 使用NAS的File Station或文件管理App
2. 找到 `urls.txt` 文件
3. 编辑文件，粘贴微信文章URL
4. 保存文件，服务自动开始处理

### 方式2: 通过Samba/FTP
1. 通过网络访问NAS共享文件夹
2. 找到 `urls.txt` 文件
3. 用记事本编辑，添加URL
4. 保存后自动处理

### 方式3: 通过SSH
```bash
# SSH登录NAS
echo "https://mp.weixin.qq.com/s/xxxxxx" >> urls.txt
```

### 方式4: 通过云盘同步
1. 在NAS上设置云盘同步(OneDrive/Google Drive等)
2. 将urls.txt同步到云盘
3. 手机编辑云盘中的文件
4. 自动同步并处理

## 🌐 Web界面访问

打开浏览器访问: `http://你的NAS的IP:8080`

### Web界面功能
- 📊 实时统计: 处理总数、成功数、运行时间
- 📋 当前状态: 显示正在处理的任务
- 📖 使用说明: 详细的操作指南
- 📁 文件路径: 显示关键文件的绝对路径

## 🔧 服务管理

### 使用控制脚本 (推荐)
```bash
./service_control.sh start     # 启动服务
./service_control.sh stop      # 停止服务
./service_control.sh restart   # 重启服务
./service_control.sh status    # 查看状态
./service_control.sh logs      # 查看日志
./service_control.sh web       # 显示Web地址
```

### 使用systemctl命令
```bash
sudo systemctl start wechat-crawler     # 启动
sudo systemctl stop wechat-crawler      # 停止
sudo systemctl restart wechat-crawler   # 重启
sudo systemctl status wechat-crawler    # 状态
sudo systemctl enable wechat-crawler    # 开机启动
sudo systemctl disable wechat-crawler   # 取消开机启动
```

### 查看日志
```bash
# 查看实时日志
sudo journalctl -f -u wechat-crawler

# 查看最近日志
sudo journalctl -u wechat-crawler --since "1 hour ago"

# 查看文件日志
tail -f service.log
```

## 📁 文件结构

```
wechat-articles-spider/
├── simple_nas_service.py      # 主服务程序
├── wechat_crawler.py          # 爬虫核心
├── install_nas.sh             # 安装脚本
├── service_control.sh         # 服务控制脚本
├── urls.txt                   # URL输入文件
├── service.log               # 服务日志
├── venv/                     # Python虚拟环境
└── wechat_articles/          # 输出目录
    ├── 文章1/
    │   ├── 文章1.md          # Markdown文档
    │   ├── 文章1_content.txt  # 纯文本
    │   ├── 文章1_metadata.json # 元数据
    │   ├── 文章1_keywords.json # 关键词分析
    │   └── images/           # 文章图片
    └── summary_report.md     # 汇总报告
```

## ⚙️ 高级配置

### 修改端口号
编辑 `simple_nas_service.py` 中的配置:
```python
self.config = {
    "web_port": 8080,  # 修改为其他端口
    # ...其他配置
}
```

### 修改输出目录
```python
self.config = {
    "output_dir": "/path/to/custom/output",  # 自定义输出路径
    # ...
}
```

### 开启调试模式
在服务文件末尾修改:
```python
logging.basicConfig(level=logging.DEBUG)  # 启用调试日志
```

## 🛠️ 故障排除

### 服务无法启动
```bash
# 检查服务状态
sudo systemctl status wechat-crawler

# 查看详细错误
sudo journalctl -u wechat-crawler

# 检查Python环境
cd /path/to/project
source venv/bin/activate
python3 simple_nas_service.py  # 手动运行测试
```

### Web界面无法访问
1. 检查防火墙设置
2. 确认端口8080未被占用
3. 检查NAS网络设置

### 文件权限问题
```bash
# 确保用户有读写权限
chmod 755 /path/to/project
chmod 644 urls.txt
chown -R username:username /path/to/project
```

### 依赖包安装失败
```bash
# 手动安装依赖
source venv/bin/activate
pip3 install --upgrade pip
pip3 install watchdog flask requests beautifulsoup4 html2text jieba
```

### URL处理失败
1. 检查网络连接
2. 确认URL格式正确
3. 查看日志了解具体错误

## 🔄 升级服务

```bash
# 停止服务
./service_control.sh stop

# 更新代码文件
# (上传新版本的.py文件)

# 重新安装依赖(如果需要)
source venv/bin/activate
pip3 install --upgrade -r requirements.txt

# 启动服务
./service_control.sh start
```

## 📱 手机操作技巧

### iPhone用户
1. **Files应用**: 连接NAS共享，直接编辑文件
2. **Working Copy**: Git管理，同步代码
3. **Terminus**: SSH终端，远程管理

### Android用户
1. **ES文件浏览器**: 访问网络共享
2. **JuiceSSH**: SSH终端
3. **FTP客户端**: 文件传输

### 通用方案
1. **云盘同步**: 文件自动同步到NAS
2. **NAS厂商App**: 使用官方文件管理器
3. **Web界面**: 浏览器直接访问

## 📊 性能优化

### 资源占用
- **内存**: 约50-100MB
- **CPU**: 处理时占用较高，空闲时极低
- **存储**: 根据文章和图片数量增长

### 优化建议
1. 定期清理旧文章和图片
2. 设置合理的处理间隔
3. 避免同时处理大量URL
4. 监控磁盘空间使用

## 🎯 最佳实践

### URL管理
- 一次添加3-5个URL，避免过多
- 使用短链接或清理参数
- 定期检查处理结果

### 文件组织
- 定期归档旧文章
- 使用有意义的文件夹名称
- 备份重要的转换结果

### 监控服务
- 定期查看服务状态
- 监控日志文件大小
- 关注处理成功率

## 🆘 技术支持

### 常见问题
1. **服务频繁重启**: 检查内存使用和网络连接
2. **处理速度慢**: 调整并发数量和请求间隔
3. **图片下载失败**: 检查网络和存储空间

### 联系支持
- 查看项目GitHub Issues
- 检查日志文件获取错误信息
- 提供系统环境和错误日志

---

🎉 **恭喜！你的NAS微信文章转换服务已经配置完成！**

现在你可以轻松地将微信文章转换为Markdown格式，享受自动化的便利吧！