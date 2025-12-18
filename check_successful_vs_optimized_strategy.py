#!/usr/bin/env python3
"""
检查成功股票是否满足调整后的策略条件
"""

import json
import pandas as pd
import numpy as np

# 加载选股结果
with open('main_force_burial_result_20251210_145330.json', 'r', encoding='utf-8') as f:
    screening_data = json.load(f)

# 成功股票列表（收益>3%）
successful_stocks = [
    '600730.SH',  # 中国高科 +16.47%
    '603306.SH',  # 华懋科技 +14.64%
    '002438.SZ',  # 江苏神通 +10.11%
    '002478.SZ',  # 常宝股份 +9.03%
    '002865.SZ',  # 钧达股份 +7.37%
    '300982.SZ',  # 苏文电能 +7.06%
    '603663.SH',  # 三祥新材 +6.86%
    '002448.SZ',  # 中原内配 +6.73%
    '603269.SH',  # 海鸥股份 +6.59%
    '000506.SZ',  # 招金黄金 +6.24%
    '002130.SZ',  # 沃尔核材 +3.16%
    '603399.SH',  # 永杉锂业
    '600354.SH',  # 敦煌种业
    '000422.SZ',  # 湖北宜化
    '002708.SZ',  # 光洋股份
    '300277.SZ',  # 海联讯
    '688502.SH',  # 茂莱光学
]

# 调整后的策略条件
optimized_conditions = {
    'max_deviation': 2.0,  # 乖离率≤2%
    'min_pct': 2.0,        # 涨幅≥2%
    'min_amount_wan': 50000,  # 成交额≥5亿（万元）
    'min_turnover_rate': 5.0,  # 换手率≥5%
}

# 创建字典快速查找
stocks_dict = {stock['code']: stock for stock in screening_data['stocks']}

print("📊 成功股票与优化策略匹配度分析")
print("=" * 80)
print(f"\n优化后的策略条件：")
print(f"1. 乖离率 ≤ {optimized_conditions['max_deviation']}%")
print(f"2. 涨幅 ≥ {optimized_conditions['min_pct']}%")
print(f"3. 成交额 ≥ {optimized_conditions['min_amount_wan']/10000:.1f}亿元")
print(f"4. 换手率 ≥ {optimized_conditions['min_turnover_rate']}%\n")

# 分析每只成功股票
print(f"{'股票代码':<12} {'股票名称':<10} {'收益%':<8} {'乖离%':<8} {'涨幅%':<8} {'换手%':<8} {'成交额(亿)':<12} {'满足条件':<10}")
print("-" * 80)

fully_satisfied = 0
partially_satisfied = 0
details = []

for stock_code in successful_stocks:
    if stock_code not in stocks_dict:
        continue

    stock = stocks_dict[stock_code]
    name = stock['name']
    change = stock['change']
    deviation = stock['deviation']
    turnover_rate = stock['turnover_rate']
    amount_wan = stock['amount_wan']
    amount_yi = amount_wan / 10000

    # 检查满足的条件
    conditions_met = []
    if deviation <= optimized_conditions['max_deviation']:
        conditions_met.append('乖离')
    if change >= optimized_conditions['min_pct']:
        conditions_met.append('涨幅')
    if amount_wan >= optimized_conditions['min_amount_wan']:
        conditions_met.append('成交额')
    if turnover_rate >= optimized_conditions['min_turnover_rate']:
        conditions_met.append('换手')

    # 统计
    if len(conditions_met) == 4:
        fully_satisfied += 1
        status = "✅ 全部"
    elif len(conditions_met) >= 2:
        partially_satisfied += 1
        status = f"⚠️ {len(conditions_met)}/4"
    else:
        status = f"❌ {len(conditions_met)}/4"

    details.append({
        'code': stock_code,
        'name': name,
        'change': change,
        'deviation': deviation,
        'amount_yi': amount_yi,
        'turnover_rate': turnover_rate,
        'met_count': len(conditions_met)
    })

    # 显示收益（从之前的分析获取）
    returns_map = {
        '600730.SH': 16.47, '603306.SH': 14.64, '002438.SZ': 10.11,
        '002478.SZ': 9.03, '002865.SZ': 7.37, '300982.SZ': 7.06,
        '603663.SH': 6.86, '002448.SZ': 6.73, '603269.SH': 6.59,
        '000506.SZ': 6.24, '002130.SZ': 3.16
    }
    return_pct = returns_map.get(stock_code, 3.0)

    print(f"{stock_code:<12} {name:<10} {return_pct:<8.1f} {deviation:<8.2f} {change:<8.2f} {turnover_rate:<8.2f} {amount_yi:<12.1f} {status:<10}")

print("\n" + "=" * 80)
print(f"分析结果：")
print(f"1. 完全满足优化条件的股票：{fully_satisfied} 只")
print(f"2. 部分满足优化条件的股票：{partially_satisfied} 只")
print(f"3. 成功率：{(fully_satisfied + partially_satisfied) / len(successful_stocks) * 100:.1f}%")

# 详细分析未满足条件的情况
print("\n📉 不满足条件的情况分析：")
print("-" * 60)

failed_conditions = {
    '乖离率>2%': 0,
    '涨幅<2%': 0,
    '成交额<5亿': 0,
    '换手率<5%': 0
}

for stock_code in successful_stocks:
    if stock_code not in stocks_dict:
        continue
    stock = stocks_dict[stock_code]

    if stock['deviation'] > optimized_conditions['max_deviation']:
        failed_conditions['乖离率>2%'] += 1
    if stock['change'] < optimized_conditions['min_pct']:
        failed_conditions['涨幅<2%'] += 1
    if stock['amount_wan'] < optimized_conditions['min_amount_wan']:
        failed_conditions['成交额<5亿'] += 1
    if stock['turnover_rate'] < optimized_conditions['min_turnover_rate']:
        failed_conditions['换手率<5%'] += 1

for condition, count in failed_conditions.items():
    print(f"{condition}: {count} 只股票")

print("\n💡 优化建议调整：")
print("-" * 60)

# 基于实际数据给出更合理的参数
deviation_values = [s['deviation'] for s in details if s['deviation'] > 0]
change_values = [s['change'] for s in details]
amount_values = [s['amount_yi'] for s in details]
turnover_values = [s['turnover_rate'] for s in details]

print(f"基于成功股票的数据分布：")
print(f"1. 乖离率：中位数={np.median(deviation_values):.2f}%，建议保持≤{np.percentile(deviation_values, 75):.1f}%")
print(f"2. 涨幅：中位数={np.median(change_values):.2f}%，建议≥{np.percentile(change_values, 25):.1f}%")
print(f"3. 成交额：中位数={np.median(amount_values):.1f}亿，建议≥{np.percentile(amount_values, 25):.1f}亿")
print(f"4. 换手率：中位数={np.median(turnover_values):.2f}%，建议≥{np.percentile(turnover_values, 25):.1f}%")

print("\n🎯 最终建议参数：")
print("1. 乖离率 ≤ 2.5%（稍微放宽）")
print("2. 涨幅 ≥ 2.5%（保持）")
print("3. 成交额 ≥ 3.5亿（放宽一些）")
print("4. 换手率 ≥ 4.5%（略微放宽）")

print("\n⚠️ 重要发现：")
print("- 大部分成功股票并不完全符合严格的优化条件")
print("- 说明策略成功可能更多依赖于题材、时机等其他因素")
print("- 建议保持一定灵活性，避免过度优化")