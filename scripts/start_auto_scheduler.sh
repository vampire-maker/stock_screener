#!/bin/bash

echo "🚀 股票筛选自动调度器启动"
echo "================================"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误: 未找到虚拟环境 venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查Python是否可用
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 python (在虚拟环境中)"
    exit 1
fi

# 检查选股脚本是否存在
if [ ! -f "src/main_force_burial_strategy.py" ]; then
    echo "❌ 错误: 未找到 src/main_force_burial_strategy.py"
    exit 1
fi

if [ ! -f "adaptive_main_force_strategy.py" ]; then
    echo "❌ 错误: 未找到 adaptive_main_force_strategy.py"
    exit 1
fi

# 检查调度器脚本是否存在
if [ ! -f "core/auto_scheduler.py" ]; then
    echo "❌ 错误: 未找到 core/auto_scheduler.py"
    exit 1
fi

# 设置环境变量
export SMTP_SERVER=smtp.qq.com
export SMTP_PORT=587
export SENDER_EMAIL=361612558@qq.com
export SENDER_PASSWORD=eandpognegzacbda
export RECEIVER_EMAIL=hf.zhang512@outlook.com,gxs0710@hotmail.com

echo "⏰ 启动时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📡 调度器配置:"
echo "  • 11:30 - 自适应主力埋伏策略 (实时数据，如休盘则使用最新历史数据)"
echo "  • 14:30 - 已删除该时段策略"
echo "  • 14:40 - 主力埋伏策略v4.0 (30-200亿，涨幅1%-5%，换手率收紧，成交额≥3亿，技术评分≥20)"
echo
echo "📧 邮件推送: 已配置"
echo "📁 日志文件: auto_scheduler.log"
echo
echo "💡 调度器将持续运行，按 Ctrl+C 停止"
echo "================================"
echo

# 启动自动调度器
python core/auto_scheduler.py