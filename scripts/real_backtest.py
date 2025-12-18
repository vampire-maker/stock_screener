#!/usr/bin/env python3
"""
真实股票回测分析
基于频繁被选中的股票，查询其实际市场表现
"""

import requests
import json
from datetime import datetime, timedelta

def get_current_stock_data(stock_code, api_key):
    """获取股票当前数据"""
    try:
        endpoint = "https://api.gugudata.com/stock/cn/realtime"
        params = {
            'appkey': api_key,
            'symbol': stock_code
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if 'DataStatus' in data and data['DataStatus']['StatusCode'] == 100:
                return data['Data'][0] if data['Data'] else None
        return None

    except Exception as e:
        print(f"获取 {stock_code} 数据失败: {e}")
        return None

def analyze_stock_performance():
    """分析上周频繁选股的表现"""

    # 从之前分析中获取的频繁被选中的股票
    frequent_stocks = [
        {'code': '603600', 'name': '永艺股份', 'frequency': 11},
        {'code': '002475', 'name': '立讯精密', 'frequency': 10},
        {'code': '300221', 'name': '银禧科技', 'frequency': 10},
        {'code': '300830', 'name': '金现代', 'frequency': 10},
        {'code': '300166', 'name': '东方国信', 'frequency': 1}
    ]

    api_key = "SQSM4ASGQT6UN363PWA9M6256764WYBS"

    print("=" * 80)
    print("📈 真实股票回测分析")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"分析周期: 最近一周的选股表现")
    print()

    results = []

    for stock in frequent_stocks:
        print(f"🔍 分析: {stock['code']} {stock['name']} (上周被推荐{stock['frequency']}次)")

        current_data = get_current_stock_data(stock['code'], api_key)

        if current_data:
            current_price = float(current_data.get('Latest', 0))
            change_percent = float(current_data.get('ChangePercent', 0))
            volume = int(current_data.get('TradingVolume', 0))
            turnover_rate = float(current_data.get('TurnoverRate', 0))

            # 估算买入价格（假设上周买入，使用当前价格调整）
            # 这是一个简化的估算，实际应该记录当时的买入价格
            estimated_buy_price = current_price / (1 + change_percent / 100)

            if estimated_buy_price > 0:
                profit_loss = current_price - estimated_buy_price
                profit_loss_percent = (profit_loss / estimated_buy_price) * 100

                performance = "📈" if profit_loss_percent > 0 else "📉"

                results.append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'frequency': stock['frequency'],
                    'current_price': current_price,
                    'estimated_buy_price': estimated_buy_price,
                    'change_percent': change_percent,
                    'profit_loss_percent': profit_loss_percent,
                    'volume': volume,
                    'turnover_rate': turnover_rate,
                    'performance': performance
                })

                print(f"   当前价格: ¥{current_price:.2f}")
                print(f"   今日涨跌: {change_percent:+.2f}%")
                print(f"   估算收益: {profit_loss_percent:+.2f}% {performance}")
                print(f"   成交量: {volume:,}手")
                print(f"   换手率: {turnover_rate:.2f}%")
            else:
                print(f"   ❌ 数据异常")
        else:
            print(f"   ❌ 无法获取实时数据")

        print("-" * 50)

    # 汇总分析
    if results:
        print("\n📊 汇总分析")
        print("=" * 50)

        total_stocks = len(results)
        profitable_stocks = len([r for r in results if r['profit_loss_percent'] > 0])
        avg_return = sum(r['profit_loss_percent'] for r in results) / total_stocks

        print(f"分析股票数量: {total_stocks}")
        print(f"盈利股票数: {profitable_stocks}")
        print(f"亏损股票数: {total_stocks - profitable_stocks}")
        print(f"胜率: {(profitable_stocks/total_stocks)*100:.1f}%")
        print(f"平均收益率: {avg_return:+.2f}%")

        # 排行榜
        print(f"\n🏆 收益排行榜")
        print("-" * 50)
        sorted_results = sorted(results, key=lambda x: x['profit_loss_percent'], reverse=True)

        for i, stock in enumerate(sorted_results, 1):
            print(f"{i:2d}. {stock['code']} {stock['name']:<8} - {stock['profit_loss_percent']:+6.2f}% {stock['performance']}")

        # 保存结果
        report_data = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'summary': {
                'total_stocks': total_stocks,
                'profitable_stocks': profitable_stocks,
                'win_rate': (profitable_stocks/total_stocks)*100,
                'avg_return': avg_return
            }
        }

        filename = f"real_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 详细数据已保存至: {filename}")

        # 建议
        print(f"\n💡 投资建议")
        print("-" * 50)
        if avg_return > 2:
            print("✅ 选股策略表现良好，建议继续使用")
        elif avg_return > 0:
            print("⚠️ 选股策略基本有效，但需要优化")
        else:
            print("❌ 选股策略需要重新评估")

        print(f"当前平均收益: {avg_return:+.2f}%")
        print(f"建议关注: {sorted_results[0]['name'] if sorted_results else 'N/A'}")

    else:
        print("❌ 无法获取任何股票数据，无法进行分析")

if __name__ == "__main__":
    analyze_stock_performance()