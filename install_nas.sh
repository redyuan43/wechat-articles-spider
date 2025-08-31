#!/bin/bash
# NAS微信文章服务安装脚本 (Debian系统)

set -e

echo "=================================================="
echo "🏠 NAS微信文章转换服务 - 安装脚本"  
echo "=================================================="

# 检查权限
if [ "$EUID" -eq 0 ]; then
    echo "⚠️ 请不要使用root权限运行此脚本"
    echo "正确用法: ./install_nas.sh"
    exit 1
fi

# 获取当前目录
INSTALL_DIR=$(pwd)
SERVICE_NAME="wechat-crawler"
USER=$(whoami)

echo "📁 安装目录: $INSTALL_DIR"
echo "👤 运行用户: $USER"

# 检查系统
if ! command -v apt &> /dev/null; then
    echo "❌ 此脚本仅支持Debian/Ubuntu系统"
    exit 1
fi

echo "✅ 检测到Debian/Ubuntu系统"

# 更新软件包列表
echo "📦 更新软件包列表..."
sudo apt update

# 安装Python和pip
echo "🐍 安装Python依赖..."
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 创建虚拟环境
echo "🔧 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "📚 安装Python包..."
source venv/bin/activate
pip3 install --upgrade pip
pip3 install watchdog flask requests beautifulsoup4 html2text jieba

# 检查必要文件
echo "🔍 检查服务文件..."
required_files=("simple_nas_service.py" "wechat_crawler.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少必要文件: $file"
        exit 1
    fi
done

# 设置文件权限
chmod +x simple_nas_service.py
chmod +x wechat_crawler.py

# 创建systemd服务文件
echo "⚙️ 创建系统服务..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=NAS微信文章转换服务
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/simple_nas_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable $SERVICE_NAME

# 创建urls.txt文件
if [ ! -f "urls.txt" ]; then
    touch urls.txt
    echo "📝 创建了urls.txt文件"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "📋 接下来的操作："
echo "1. 启动服务:  sudo systemctl start $SERVICE_NAME"
echo "2. 查看状态:  sudo systemctl status $SERVICE_NAME"
echo "3. 查看日志:  sudo journalctl -f -u $SERVICE_NAME"
echo "4. 停止服务:  sudo systemctl stop $SERVICE_NAME"
echo ""
echo "🌐 Web界面: http://$(hostname -I | awk '{print $1}'):8080"
echo "📁 编辑文件: $INSTALL_DIR/urls.txt"
echo "📁 输出目录: $INSTALL_DIR/wechat_articles"
echo ""
echo "💡 使用方法:"
echo "   将微信文章URL粘贴到 urls.txt 文件中，保存后自动处理"
echo ""

# 询问是否立即启动
read -p "是否现在启动服务? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start $SERVICE_NAME
    echo "🚀 服务已启动！"
    sleep 2
    sudo systemctl status $SERVICE_NAME --no-pager
    echo ""
    echo "📱 现在可以访问: http://$(hostname -I | awk '{print $1}'):8080"
fi

echo ""
echo "=================================================="
echo "🎉 安装完成！享受自动化的微信文章转换服务吧！"
echo "=================================================="