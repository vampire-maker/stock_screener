#!/bin/bash

# 股票筛选调度器启动脚本

echo "🚀 股票筛选调度器启动脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 检查是否存在虚拟环境
if [ -d "venv" ]; then
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
else
    echo "⚠️  警告: 未找到虚拟环境，使用系统Python"
fi

# 检查是否安装了依赖
if ! python3 -c "import apscheduler" 2>/dev/null; then
    echo "📦 安装 APScheduler..."
    pip3 install apscheduler
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 配置文件"
    echo "请复制 .env.example 并配置邮件参数"
    echo ""
    echo "示例命令:"
    echo "  cp .env.example .env"
    echo "  # 编辑 .env 文件设置邮件配置"
    echo ""
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建日志目录
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "📁 创建日志目录: logs/"
fi

echo ""
echo "选择运行模式:"
echo "1. 启动定时任务调度器 (需要安装 APScheduler)"
echo "2. 手动测试模式 (无需额外依赖)"
echo "3. 退出"
echo ""

read -p "请输入选项 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🕐 启动定时任务调度器..."
        echo "任务时间:"
        echo "  09:30 - GuguData基础选股"
        echo "  14:30 - GuguData基础选股"
        echo "  19:30 - Tushare Pro增强选股"
        echo ""
        echo "按 Ctrl+C 停止调度器"
        echo "=================================="
        python3 stock_screening_scheduler.py
        ;;
    2)
        echo ""
        echo "🧪 启动手动测试模式..."
        echo "=================================="
        python3 test_scheduler_simple.py
        ;;
    3)
        echo "退出程序"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac