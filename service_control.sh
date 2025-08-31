#!/bin/bash
# NAS微信文章服务控制脚本

SERVICE_NAME="wechat-crawler"
SCRIPT_DIR=$(dirname "$0")

show_help() {
    echo "NAS微信文章服务控制脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看实时日志"
    echo "  install   安装/重新安装服务"
    echo "  web       显示Web界面地址"
    echo "  help      显示此帮助信息"
    echo ""
}

show_web_info() {
    IP=$(hostname -I | awk '{print $1}')
    echo "🌐 Web界面访问地址:"
    echo "   http://$IP:8080"
    echo ""
    echo "📱 手机访问:"
    echo "   在手机浏览器中输入上述地址"
    echo ""
    echo "📝 文件编辑:"
    echo "   编辑 $SCRIPT_DIR/urls.txt 文件"
    echo "   添加微信文章URL，每行一个"
    echo ""
}

case "$1" in
    start)
        echo "🚀 启动微信文章服务..."
        sudo systemctl start $SERVICE_NAME
        if systemctl is-active --quiet $SERVICE_NAME; then
            echo "✅ 服务启动成功！"
            show_web_info
        else
            echo "❌ 服务启动失败"
            sudo systemctl status $SERVICE_NAME --no-pager
        fi
        ;;
    
    stop)
        echo "🛑 停止微信文章服务..."
        sudo systemctl stop $SERVICE_NAME
        echo "✅ 服务已停止"
        ;;
    
    restart)
        echo "🔄 重启微信文章服务..."
        sudo systemctl restart $SERVICE_NAME
        if systemctl is-active --quiet $SERVICE_NAME; then
            echo "✅ 服务重启成功！"
            show_web_info
        else
            echo "❌ 服务重启失败"
            sudo systemctl status $SERVICE_NAME --no-pager
        fi
        ;;
    
    status)
        echo "📊 服务状态:"
        sudo systemctl status $SERVICE_NAME --no-pager
        echo ""
        if systemctl is-active --quiet $SERVICE_NAME; then
            show_web_info
        fi
        ;;
    
    logs)
        echo "📝 实时日志 (按Ctrl+C退出):"
        echo "=================================="
        sudo journalctl -f -u $SERVICE_NAME
        ;;
    
    install)
        echo "📦 安装/重新安装服务..."
        if [ -f "$SCRIPT_DIR/install_nas.sh" ]; then
            cd "$SCRIPT_DIR"
            ./install_nas.sh
        else
            echo "❌ 找不到安装脚本 install_nas.sh"
            exit 1
        fi
        ;;
    
    web)
        show_web_info
        ;;
    
    help|--help|-h|"")
        show_help
        ;;
    
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac