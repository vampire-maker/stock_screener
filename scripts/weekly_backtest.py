#!/usr/bin/env python3
"""
股票筛选回测系统 - 最近一周选股效果分析
"""

import json
import os
import glob
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class WeeklyBacktest:
    """一周回测分析器"""

    def __init__(self):
        self.results = []
        self.stock_performance = {}

    def load_result_files(self):
        """加载最近一周的结果文件"""
        print("🔍 加载最近一周的选股结果文件...")

        # 获取所有结果文件
        result_files = glob.glob("*result*.json")
        result_files.sort()

        # 按日期过滤最近一周的文件
        one_week_ago = datetime.now() - timedelta(days=7)

        for file in result_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 解析执行时间
                execution_time = datetime.strptime(data['execution_time'], '%Y-%m-%d %H:%M:%S')

                if execution_time >= one_week_ago:
                    print(f"📅 加载文件: {file} ({execution_time.strftime('%Y-%m-%d %H:%M')})")
                    self.results.append({
                        'file': file,
                        'execution_time': execution_time,
                        'data': data
                    })

            except Exception as e:
                print(f"⚠️  跳过文件 {file}: {e}")

        print(f"✅ 共加载 {len(self.results)} 个结果文件")

    def analyze_screening_performance(self):
        """分析选股表现"""
        print("\n📊 选股效果分析")
        print("=" * 60)

        total_days = len(self.results)
        total_stocks_selected = 0
        daily_stats = []

        for result in self.results:
            data = result['data']
            date = result['execution_time'].strftime('%Y-%m-%d')

            # 统计选股数量
            selected_count = 0
            if 'task_results' in data:
                for task in data['task_results']:
                    selected_count += task.get('count', 0)
            elif 'results_count' in data:
                selected_count = data['results_count']

            total_stocks_selected += selected_count

            daily_stats.append({
                'date': date,
                'time': result['execution_time'].strftime('%H:%M'),
                'count': selected_count,
                'file': result['file']
            })

        # 计算平均值
        avg_daily_selections = total_stocks_selected / total_days if total_days > 0 else 0

        print(f"📈 总体统计:")
        print(f"  • 分析天数: {total_days} 天")
        print(f"  • 总选股数: {total_stocks_selected} 只")
        print(f"  • 日均选股: {avg_daily_selections:.1f} 只")

        # 按日期分组统计
        print(f"\n📅 每日选股统计:")
        daily_stats.sort(key=lambda x: x['date'])

        for stat in daily_stats:
            status = "✅" if stat['count'] > 0 else "❌"
            print(f"  {status} {stat['date']} {stat['time']}: {stat['count']} 只 ({stat['file']})")

    def analyze_top_stocks(self):
        """分析TOP股票表现"""
        print("\n🏆 TOP 股票分析")
        print("=" * 60)

        all_stocks = []

        for result in self.results:
            data = result['data']
            date = result['execution_time'].strftime('%Y-%m-%d')

            # 收集所有选中的股票
            if 'task_results' in data:
                for task in data['task_results']:
                    for stock in task.get('stocks', []):
                        stock['screening_date'] = date
                        stock['screening_time'] = result['execution_time'].strftime('%H:%M')
                        stock['task_name'] = task.get('name', '未知')
                        all_stocks.append(stock)

            elif 'top_stocks' in data:
                for stock in data['top_stocks']:
                    stock['screening_date'] = date
                    stock['screening_time'] = result['execution_time'].strftime('%H:%M')
                    all_stocks.append(stock)

        if not all_stocks:
            print("❌ 未找到选股数据")
            return

        # 转换为DataFrame进行分析
        df = pd.DataFrame(all_stocks)

        print(f"📊 股票统计:")
        print(f"  • 总选股记录: {len(df)} 条")
        print(f"  • 独立股票数: {df['name'].nunique()} 只")

        # 重复入选的股票
        if 'name' in df.columns:
            repeated_stocks = df['name'].value_counts()
            print(f"\n🔄 重复入选股票 (≥2次):")
            for stock_name, count in repeated_stocks[repeated_stocks >= 2].items():
                stocks_df = df[df['name'] == stock_name]
                if 'code' in stocks_df.columns:
                    code = stocks_df['code'].iloc[0]
                    dates = ', '.join(stocks_df['screening_date'].tolist())
                    print(f"  • {stock_name} ({code}): {count} 次 - {dates}")

        # 按评分排序（如果有评分）
        if 'score' in df.columns:
            print(f"\n⭐ 高评分股票 (TOP 10):")
            top_scored = df.nlargest(10, 'score')
            for _, stock in top_scored.iterrows():
                name = stock.get('name', '未知')
                code = stock.get('code', '')
                price = stock.get('price', 0)
                score = stock.get('score', 0)
                date = stock.get('screening_date', '')
                print(f"  • {name} ({code}): {price:.2f}元 评分:{score:.1f} ({date})")

    def analyze_strategy_effectiveness(self):
        """分析策略有效性"""
        print("\n🎯 策略有效性分析")
        print("=" * 60)

        strategy_stats = {}

        for result in self.results:
            data = result['data']
            date = result['execution_time'].strftime('%Y-%m-%d')

            # 分析不同策略类型
            if 'task_results' in data:
                for task in data['task_results']:
                    task_name = task.get('name', '未知策略')
                    count = task.get('count', 0)

                    if task_name not in strategy_stats:
                        strategy_stats[task_name] = []
                    strategy_stats[task_name].append({
                        'date': date,
                        'count': count
                    })

            elif 'screening_type' in data:
                screening_type = data['screening_type']
                count = data.get('results_count', 0)

                if screening_type not in strategy_stats:
                    strategy_stats[screening_type] = []
                strategy_stats[screening_type].append({
                    'date': date,
                    'count': count
                })

        # 计算各策略的平均表现
        print(f"📈 各策略表现统计:")
        for strategy, records in strategy_stats.items():
            total_records = len(records)
            total_stocks = sum(r['count'] for r in records)
            avg_stocks = total_stocks / total_records if total_records > 0 else 0
            success_days = len([r for r in records if r['count'] > 0])
            success_rate = (success_days / total_records * 100) if total_records > 0 else 0

            print(f"  • {strategy}:")
            print(f"    - 执行次数: {total_records}")
            print(f"    - 总选股: {total_stocks} 只")
            print(f"    - 日均选股: {avg_stocks:.1f} 只")
            print(f"    - 成功率: {success_rate:.1f}% ({success_days}/{total_records})")

    def generate_summary_report(self):
        """生成总结报告"""
        print("\n📋 回测总结报告")
        print("=" * 60)

        if not self.results:
            print("❌ 没有找到符合条件的回测数据")
            return

        # 计算时间范围
        dates = [r['execution_time'] for r in self.results]
        start_date = min(dates).strftime('%Y-%m-%d')
        end_date = max(dates).strftime('%Y-%m-%d')

        print(f"⏰ 回测时间范围: {start_date} 至 {end_date}")
        print(f"📁 分析文件数量: {len(self.results)} 个")

        # 总体表现
        total_selections = 0
        successful_days = 0

        for result in self.results:
            data = result['data']
            day_selections = 0

            if 'task_results' in data:
                for task in data['task_results']:
                    day_selections += task.get('count', 0)
            elif 'results_count' in data:
                day_selections = data['results_count']

            total_selections += day_selections
            if day_selections > 0:
                successful_days += 1

        success_rate = (successful_days / len(self.results) * 100) if self.results else 0
        avg_selections = total_selections / len(self.results) if self.results else 0

        print(f"\n📊 核心指标:")
        print(f"  • 选股成功率: {success_rate:.1f}%")
        print(f"  • 日均选股数: {avg_selections:.1f} 只")
        print(f"  • 总选股数量: {total_selections} 只")

        # 投资建议
        print(f"\n💡 投资建议:")
        if success_rate >= 80:
            print(f"  ✅ 策略表现优秀，选股成功率 {success_rate:.1f}%")
        elif success_rate >= 60:
            print(f"  ⚠️  策略表现良好，选股成功率 {success_rate:.1f}%")
        else:
            print(f"  ❌ 策略需要优化，选股成功率仅 {success_rate:.1f}%")

        if avg_selections >= 5:
            print(f"  ✅ 选股数量充足，日均 {avg_selections:.1f} 只")
        elif avg_selections >= 2:
            print(f"  ⚠️  选股数量适中，日均 {avg_selections:.1f} 只")
        else:
            print(f"  ❌ 选股数量偏少，日均仅 {avg_selections:.1f} 只")

        print(f"\n🎯 后续优化方向:")
        print(f"  • 关注重复入选的优质股票")
        print(f"  • 结合市场环境调整筛选条件")
        print(f"  • 加强风险控制和仓位管理")
        print(f"  • 定期回测验证策略有效性")

    def run_backtest(self):
        """运行完整的回测分析"""
        print("🚀 股票筛选系统 - 最近一周回测分析")
        print("=" * 60)

        self.load_result_files()
        self.analyze_screening_performance()
        self.analyze_top_stocks()
        self.analyze_strategy_effectiveness()
        self.generate_summary_report()

        print(f"\n✅ 回测分析完成！")
        print(f"📊 建议定期运行回测以监控策略表现")

if __name__ == "__main__":
    backtest = WeeklyBacktest()
    backtest.run_backtest()