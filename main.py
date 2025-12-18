#!/usr/bin/env python3
"""
股票筛选系统主入口
优化版选股策略 - 基于放开市值要求实验结果
"""

import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from optimized_screening import CorrectedScreeningLogic

def main():
    """主函数"""
    print("🚀 股票筛选系统 - 优化版")
    print("=" * 50)
    print(f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 策略特点: 放开市值要求 + 换手率8-10% + ROE8-12%")
    print()

    # 创建优化版选股器
    screener = CorrectedScreeningLogic()

    # 执行时段选股
    screener.run_time_based_screening()

if __name__ == "__main__":
    main()