#!/usr/bin/env python3
"""
快刀手晚进早出策略 v2.0
14:30选股，使用GuguData实时数据
次日早盘出局

支持邮件推送
"""

import requests
import pandas as pd
from datetime import datetime
import os
import sys
from pathlib import Path
import time

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.email_sender import EmailSender

# GuguData配置
GUGU_APPKEY = os.getenv('GUGU_APPKEY', 'SQSM4ASGQT6UN363PWA9M6256764WYBS')

# v2.0策略参数
CONFIG = {
    'MIN_PCT': 2.8,  # 最小涨幅
    'MAX_PCT': 4.5,  # 最大涨幅
    'MIN_VOLUME_RATIO': 1.0,  # 量比最小值
    'MAX_VOLUME_RATIO': 1.6,  # 量比最大值
    'MAX_MV': 20000000000,  # 最大市值200亿
    'TURNOVER_LOW_MAX': 2.5,  # 低换手率上限
    'TURNOVER_HIGH_MIN': 18.0,  # 高换手率下限
    'TURNOVER_AVOID_MIN': 5.0,  # 避开区间下限
    'TURNOVER_AVOID_MAX': 10.0,  # 避开区间上限
}

def get_gugudata_realtime(stock_codes):
    """从GuguData获取实时数据"""
    url = "https://api.gugudata.com/stock/cn/realtime"

    # GuguData要求代码格式：不带后缀，如 000001
    converted_codes = [code.split('.')[0] if '.' in code else code for code in stock_codes]

    params = {
        'appkey': GUGU_APPKEY,
        'symbol': ','.join(converted_codes)
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            status = data.get('DataStatus', {})
            if status.get('StatusCode') == 100:
                return data.get('Data', [])
    except Exception as e:
        print(f"获取GuguData数据出错: {e}")

    return []

def get_all_stocks_realtime():
    """获取所有股票的实时数据（分批）"""
    all_data = []

    # GuguData一次返回所有数据，不需要分批查询特定股票
    url = "https://api.gugudata.com/stock/cn/realtime"
    params = {'appkey': GUGU_APPKEY}

    try:
        print("正在获取GuguData实时数据...")
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            status = data.get('DataStatus', {})
            if status.get('StatusCode') == 100:
                all_data = data.get('Data', [])
                print(f"获取到 {len(all_data)} 只股票实时数据")
            else:
                print(f"API返回错误: {status.get('StatusDescription', 'Unknown')}")
    except Exception as e:
        print(f"获取数据出错: {e}")

    return all_data

def quick_knife_screening():
    """执行快刀手策略选股（使用GuguData实时数据）"""

    test_date = datetime.now().strftime('%Y%m%d')
    current_time = datetime.now().strftime('%H:%M')

    print("=" * 60)
    print("快刀手晚进早出策略 v2.0")
    print(f"选股时间: {test_date} {current_time}")
    print("=" * 60)

    # 获取所有股票实时数据
    print("\n[1/4] 获取实时数据...")
    all_stocks = get_all_stocks_realtime()

    if not all_stocks:
        print("未获取到数据!")
        return None

    # 转换为DataFrame
    df = pd.DataFrame(all_stocks)

    # 字段映射
    df['代码'] = df['Symbol'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df['名称'] = df['StockName']
    df['涨幅'] = pd.to_numeric(df['ChangePercent'], errors='coerce')
    df['现价'] = pd.to_numeric(df['Latest'], errors='coerce')
    df['量比'] = pd.to_numeric(df['QuantityRatio'], errors='coerce')
    df['换手率'] = pd.to_numeric(df['TurnoverRate'], errors='coerce')
    df['成交额'] = pd.to_numeric(df['TradingAmount'], errors='coerce')
    df['市值'] = pd.to_numeric(df['MarketCap'], errors='coerce')
    df['最高'] = pd.to_numeric(df['High'], errors='coerce')
    df['最低'] = pd.to_numeric(df['Low'], errors='coerce')
    df['开盘'] = pd.to_numeric(df['Open'], errors='coerce')

    # 计算均价 (用于判断是否在均线上)
    # 这里用 (最高+最低+现价)/3 作为均价的近似
    df['均价'] = (df['最高'] + df['最低'] + df['现价']) / 3

    print(f"原始数据: {len(df)} 只")

    # 基础筛选
    print("\n[2/4] 应用基础筛选...")

    # 涨幅筛选
    df = df[(df['涨幅'] >= CONFIG['MIN_PCT']) & (df['涨幅'] <= CONFIG['MAX_PCT'])]
    print(f"涨幅{CONFIG['MIN_PCT']}%-{CONFIG['MAX_PCT']}%: {len(df)} 只")

    # 量比筛选
    df = df[(df['量比'] >= CONFIG['MIN_VOLUME_RATIO']) & (df['量比'] <= CONFIG['MAX_VOLUME_RATIO'])]
    print(f"量比{CONFIG['MIN_VOLUME_RATIO']}-{CONFIG['MAX_VOLUME_RATIO']}: {len(df)} 只")

    # 市值筛选 (GuguData的市值单位是元，需要转换)
    df = df[df['市值'] <= CONFIG['MAX_MV']]
    print(f"市值≤200亿: {len(df)} 只")

    # 在均线上
    df = df[df['现价'] >= df['均价']]
    print(f"在均线上: {len(df)} 只")

    # 排除ST和科创板
    df = df[~df['名称'].str.contains('ST', na=False)]
    df = df[~df['代码'].str.startswith('688')]

    if len(df) == 0:
        print("\n没有符合条件的股票!")
        return None

    # 应用v2.0优化筛选
    print("\n[3/4] 应用v2.0优化筛选...")

    final_stocks = []
    s级_count = 0
    a级_count = 0
    b级_count = 0

    for idx, row in df.iterrows():
        turnover = row['换手率']
        turnover_ok = (turnover < CONFIG['TURNOVER_LOW_MAX']) or (turnover > CONFIG['TURNOVER_HIGH_MIN'])
        turnover_avoid = CONFIG['TURNOVER_AVOID_MIN'] <= turnover <= CONFIG['TURNOVER_AVOID_MAX']

        # 避开中间换手率区间
        if turnover_avoid:
            continue

        # 确定优先级
        priority = 'B'

        # 这里无法获取近20日涨停历史，因为GuguData只提供实时数据
        # 改用换手率和量比作为主要判断标准
        if turnover_ok:
            if turnover > CONFIG['TURNOVER_HIGH_MIN']:
                priority = 'S'  # 高换手率高活跃
                s级_count += 1
            else:
                priority = 'A'  # 低换手率主力控盘
                a级_count += 1
        else:
            b级_count += 1

        stock_info = {
            '代码': row['代码'],
            '名称': row['名称'],
            '现价': f"{row['现价']:.2f}",
            '涨幅': row['涨幅'],
            '量比': row['量比'],
            '换手率': turnover,
            '市值亿': row['市值'] / 100000000,
            '优先级': priority
        }
        final_stocks.append(stock_info)

    # 排序：S级 > A级 > B级
    priority_order = {'S': 0, 'A': 1, 'B': 2}
    final_stocks.sort(key=lambda x: priority_order.get(x['优先级'], 3))

    print(f"S级(高换手率>18%): {s级_count}只")
    print(f"A级(低换手率<2.5%): {a级_count}只")
    print(f"B级(其他): {b级_count}只")
    print(f"总计: {len(final_stocks)}只")

    return final_stocks

def send_email_notification(stocks, test_date):
    """发送邮件通知"""
    if not stocks:
        print("\n没有符合条件的股票，跳过邮件推送")
        return False

    try:
        with EmailSender() as emailer:
            subject = f"🔪 快刀手v2.0选股结果 {test_date} - {len(stocks)}只股票"

            message = f"""
快刀手晚进早出策略 v2.0 选股结果

选股时间: {test_date} 14:30 (实时数据)
选股数量: {len(stocks)} 只

策略说明:
• 涨幅区间: 2.8%-4.5%
• 量比: 1.0-1.6
• 换手率: <2.5% 或 >18% (U型分布)
• 在均线上: 是
• 数据源: GuguData实时数据

优先级说明:
• S级: 高换手率>18% (资金活跃)
• A级: 低换手率<2.5% (主力控盘)
• B级: 其他满足条件

次日操作建议:
• 高开>2%: 持有，冲高卖出
• 平开/低开: 立即止损

⚠️ 风险提示: 本选股结果仅供学习参考，不构成投资建议。股市有风险，投资需谨慎。
"""

            df_stocks = pd.DataFrame([{
                '代码': s['代码'],
                '名称': s['名称'],
                '涨跌幅': s['涨幅'],
                '换手率': s['换手率'],
                '量比': s['量比'],
                '总市值': s['市值亿'],
                '优先级': s['优先级']
            } for s in stocks])

            success = emailer.send_email(subject, message, df_stocks)

            if success:
                print(f"\n✅ 邮件推送成功!")
                return True
            else:
                print(f"\n❌ 邮件推送失败!")
                return False

    except Exception as e:
        print(f"\n❌ 邮件发送异常: {e}")
        return False

def main():
    """主函数"""
    # 执行选股
    stocks = quick_knife_screening()

    if stocks is None or len(stocks) == 0:
        print("\n未找到符合条件的股票")
        return

    # 输出结果
    print("\n" + "=" * 60)
    print("【选股结果】")
    print("=" * 60)

    df_result = pd.DataFrame(stocks)
    display_cols = ['代码', '名称', '现价', '涨幅', '量比', '换手率', '市值亿', '优先级']
    print(df_result[display_cols].to_string(index=False))

    # 保存结果
    test_date = datetime.now().strftime('%Y%m%d')
    df_save = pd.DataFrame([{
        '代码': s['代码'],
        '名称': s['名称'],
        '现价': s['现价'],
        '涨幅(%)': f"{s['涨幅']:.2f}",
        '量比': f"{s['量比']:.2f}",
        '换手率(%)': f"{s['换手率']:.2f}",
        '市值(亿)': f"{s['市值亿']:.1f}",
        '优先级': s['优先级']
    } for s in stocks])

    Path('results').mkdir(exist_ok=True)
    result_file = f"results/quick_knife_v2_{test_date}.csv"
    df_save.to_csv(result_file, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: {result_file}")

    # 发送邮件
    print("\n[4/4] 发送邮件通知...")
    send_email_notification(stocks, test_date)

    print("\n" + "=" * 60)
    print("快刀手策略执行完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
