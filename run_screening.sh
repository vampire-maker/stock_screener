#!/bin/bash

# 股票筛选系统运行脚本

echo "🚀 股票筛选系统 - 优化版"
echo "===================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建："
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "❌ .env文件不存在，请先配置环境变量"
    cp .env.example .env
    echo "已创建.env模板，请编辑后重新运行"
    exit 1
fi

# 运行选股程序
echo "📡 开始执行股票筛选..."
echo "📅 执行时间: $(date)"
echo "🎯 策略: 放开市值要求 + 换手率8-10% + ROE8-12%"
echo ""

python main.py

echo ""
echo "✅ 选股完成！"
echo "📋 结果已保存到JSON文件"
echo "📧 如邮件发送失败，请检查邮箱配置"