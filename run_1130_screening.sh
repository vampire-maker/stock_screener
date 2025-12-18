#!/bin/bash

# 11:30自动选股手动运行脚本
echo "🚀 手动执行11:30自动选股..."
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"

cd "/Users/zhanghuifeng/Documents/hf_project/stock_screener"

# 激活虚拟环境并运行
source venv/bin/activate
python scripts/auto_1130_system.py

echo "✅ 执行完成！时间: $(date '+%Y-%m-%d %H:%M:%S')"
