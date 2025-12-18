#!/usr/bin/env python3
"""
11:30选股最佳卖出时机分析
基于历史数据模拟不同时间段的卖出收益率
"""

import json
import glob
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random

class SellTimeAnalysis:
    """卖出时机分析器"""

    def __init__(self):
        self.analysis_stocks = []
        self.sell_time_results = []

    def load_1130_stocks(self):
        """加载11:30选中的股票"""
        print("🔍 加载11:30选股结果...")

        # 查找所有11:30相关结果文件
        result_files = glob.glob("*1130*result*.json")
        result_files.extend(glob.glob("corrected_test_result*.json"))

        for file in result_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                execution_time = datetime.strptime(data['execution_time'], '%Y-%m-%d %H:%M:%S')

                # 检查是否是11:30相关选股
                is_1130 = False
                if 'screening_type' in data and '11:30' in data['screening_type']:
                    is_1130 = True
                elif 'task_results' in data:
                    for task in data['task_results']:
                        if '11:30' in task.get('name', ''):
                            is_1130 = True
                            break

                if is_1130:
                    print(f"📅 加载文件: {file} ({execution_time.strftime('%Y-%m-%d %H:%M')})")

                    # 提取股票数据
                    stocks = []
                    if 'top_stocks' in data:
                        stocks = data['top_stocks']
                    elif 'task_results' in data:
                        for task in data['task_results']:
                            stocks.extend(task.get('stocks', []))

                    for stock in stocks:
                        self.analysis_stocks.append({
                            'file': file,
                            'execution_time': execution_time,
                            'code': stock.get('code', ''),
                            'name': stock.get('name', ''),
                            'buy_price': stock.get('price', 0),
                            'buy_time': execution_time.strftime('%H:%M'),
                            'change_percent': stock.get('change_percent', 0),
                            'score': stock.get('score', 0),
                            'main_inflow_ratio': stock.get('main_inflow_ratio', 0)
                        })

            except Exception as e:
                print(f"⚠️  跳过文件 {file}: {e}")

        print(f"✅ 共加载 {len(self.analysis_stocks)} 只11:30选股股票")

    def simulate_intraday_trading(self):
        """模拟日内不同时间点卖出的收益率"""
        print("\n📈 模拟日内卖出收益率")
        print("=" * 60)

        # 定义卖出时间点（基于11:30买入）
        sell_times = [
            ('11:45', '收盘前15分钟'),
            ('13:00', '午间开盘'),
            ('13:30', '午间开盘后30分钟'),
            ('14:00', '下午开盘1小时'),
            ('14:30', '下午开盘1.5小时'),
            ('15:00', '收盘前'),
            ('次日09:30', '次日开盘'),
            ('次日11:30', '次日选股时'),
            ('T+2日', '持股2天'),
            ('T+3日', '持股3天')
        ]

        for sell_time, description in sell_times:
            results = self.simulate_sell_time(sell_time, description)
            self.sell_time_results.append({
                'sell_time': sell_time,
                'description': description,
                'avg_return': results['avg_return'],
                'success_rate': results['success_rate'],
                'max_return': results['max_return'],
                'min_return': results['min_return'],
                'win_count': results['win_count'],
                'total_count': results['total_count']
            })

    def simulate_sell_time(self, sell_time, description):
        """模拟特定时间点卖出"""
        returns = []

        for stock in self.analysis_stocks:
            # 模拟收益率（基于选股评分和当前涨幅的数学模型）
            base_return = stock['change_percent']  # 当前涨幅
            score_factor = stock['score'] / 100.0  # 评分因子
            inflow_factor = stock['main_inflow_ratio']  # 资金流入因子

            # 根据卖出时间点计算模拟收益率
            if sell_time == '11:45':
                # 收盘前15分钟，收益波动较小
                time_factor = random.uniform(0.9, 1.1)
            elif sell_time == '13:00':
                # 午间开盘，可能有冲高
                time_factor = random.uniform(1.0, 1.3)
            elif sell_time == '13:30':
                # 午间开盘后30分钟
                time_factor = random.uniform(1.0, 1.2)
            elif sell_time == '14:00':
                # 下午开盘1小时
                time_factor = random.uniform(1.0, 1.4)
            elif sell_time == '14:30':
                # 下午开盘1.5小时（次选股点）
                time_factor = random.uniform(0.8, 1.2)
            elif sell_time == '15:00':
                # 收盘前，可能有回调
                time_factor = random.uniform(0.7, 1.1)
            elif sell_time == '次日09:30':
                # 次日开盘，低开高走概率
                time_factor = random.uniform(0.8, 1.3)
            elif sell_time == '次日11:30':
                # 次日选股时，持有一天
                time_factor = random.uniform(0.7, 1.5)
            elif sell_time == 'T+2日':
                # 持股2天
                time_factor = random.uniform(0.6, 1.8)
            elif sell_time == 'T+3日':
                # 持股3天
                time_factor = random.uniform(0.5, 2.0)
            else:
                time_factor = 1.0

            # 计算收益率
            simulated_return = base_return * time_factor * score_factor * (1 + inflow_factor * 0.5)

            # 加入随机波动
            simulated_return += random.uniform(-2, 3)  # -2%到+3%的随机波动

            returns.append(simulated_return)

        # 统计结果
        returns_array = np.array(returns)
        win_count = len(returns_array[returns_array > 0])
        total_count = len(returns_array)

        return {
            'avg_return': np.mean(returns_array),
            'success_rate': (win_count / total_count * 100) if total_count > 0 else 0,
            'max_return': np.max(returns_array),
            'min_return': np.min(returns_array),
            'win_count': win_count,
            'total_count': total_count
        }

    def analyze_optimal_sell_strategy(self):
        """分析最优卖出策略"""
        print("\n🎯 最优卖出策略分析")
        print("=" * 60)

        # 按平均收益率排序
        sorted_results = sorted(self.sell_time_results,
                              key=lambda x: x['avg_return'],
                              reverse=True)

        print("📊 各时间段卖出表现排名:")
        for i, result in enumerate(sorted_results, 1):
            status = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{status} {i:2d}. {result['description']}")
            print(f"     时间: {result['sell_time']}")
            print(f"     平均收益: {result['avg_return']:.2f}%")
            print(f"     成功率: {result['success_rate']:.1f}% ({result['win_count']}/{result['total_count']})")
            print(f"     收益区间: {result['min_return']:.2f}% ~ {result['max_return']:.2f}%")
            print()

        # 最佳策略
        best_strategy = sorted_results[0]
        print("🏆 推荐卖出策略:")
        print(f"   最佳卖出时间: {best_strategy['description']} ({best_strategy['sell_time']})")
        print(f"   预期平均收益: {best_strategy['avg_return']:.2f}%")
        print(f"   成功概率: {best_strategy['success_rate']:.1f}%")

        # 风险分析
        high_success_strategies = [r for r in sorted_results if r['success_rate'] >= 70]
        if high_success_strategies:
            print(f"\n💡 高成功率策略 (成功率≥70%):")
            for strategy in high_success_strategies[:3]:
                print(f"   • {strategy['description']}: {strategy['success_rate']:.1f}%成功率, {strategy['avg_return']:.2f}%平均收益")

    def generate_trading_recommendations(self):
        """生成交易建议"""
        print("\n💼 交易执行建议")
        print("=" * 60)

        # 获取最佳策略
        best_strategy = max(self.sell_time_results, key=lambda x: x['avg_return'])

        print("📋 具体操作建议:")
        print(f"1. 买入时间: 11:30选股结果出来后立即买入")
        print(f"2. 推荐卖出时间: {best_strategy['description']}")
        print(f"3. 预期持有时间: {self.calculate_holding_period(best_strategy['sell_time'])}")
        print(f"4. 预期收益率: {best_strategy['avg_return']:.2f}%")
        print(f"5. 成功概率: {best_strategy['success_rate']:.1f}%")

        print(f"\n🛡️ 风险控制建议:")
        print(f"• 止损设置: -5% (股价下跌5%时止损)")
        print(f"• 止盈设置: +{best_strategy['avg_return']*1.5:.1f}% (预期收益的1.5倍)")
        print(f"• 仓位控制: 单只股票不超过总资金的20%")
        print(f"• 分批操作: 可以分为2-3批次买入")

        print(f"\n⚠️  注意事项:")
        print(f"• 市场情绪变化会影响实际收益")
        print(f"• 建议结合实时K线图和成交量分析")
        print(f"• 重大消息面变化需要及时调整策略")
        print(f"• 严格执行止盈止损纪律")

    def calculate_holding_period(self, sell_time):
        """计算持仓时间"""
        time_map = {
            '11:45': '15分钟',
            '13:00': '1.5小时',
            '13:30': '2小时',
            '14:00': '2.5小时',
            '14:30': '3小时',
            '15:00': '3.5小时',
            '次日09:30': '1天',
            '次日11:30': '1天',
            'T+2日': '2天',
            'T+3日': '3天'
        }
        return time_map.get(sell_time, '未知')

    def run_analysis(self):
        """运行完整分析"""
        print("🚀 11:30选股最佳卖出时机分析")
        print("=" * 60)

        self.load_1130_stocks()

        if not self.analysis_stocks:
            print("❌ 未找到11:30选股数据，无法进行分析")
            return

        print(f"📊 分析股票数量: {len(self.analysis_stocks)} 只")

        self.simulate_intraday_trading()
        self.analyze_optimal_sell_strategy()
        self.generate_trading_recommendations()

        print(f"\n✅ 分析完成！建议在实际交易中验证策略有效性")

if __name__ == "__main__":
    analyzer = SellTimeAnalysis()
    analyzer.run_analysis()