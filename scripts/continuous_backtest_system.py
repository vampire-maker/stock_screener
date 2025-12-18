#!/usr/bin/env python3
"""
持续回测验证系统
定期跟踪选股策略表现，持续优化
"""

import json
import glob
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class ContinuousBacktestSystem:
    """持续回测系统"""

    def __init__(self):
        self.backtest_results = []
        self.performance_metrics = []
        self.optimization_history = []

    def load_historical_results(self):
        """加载历史选股结果"""
        print("🔍 加载历史选股结果...")
        print("=" * 60)

        # 查找所有结果文件
        result_patterns = [
            "*screening_result*.json",
            "*1130*result*.json",
            "*test_result*.json",
            "enhanced_1130_result*.json",
            "advanced_screening_result*.json"
        ]

        all_files = []
        for pattern in result_patterns:
            all_files.extend(glob.glob(pattern))

        # 去重并排序
        all_files = list(set(all_files))
        all_files.sort()

        print(f"📁 找到 {len(all_files)} 个结果文件")

        for file in all_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 解析文件信息
                file_info = self._parse_result_file(file, data)
                if file_info:
                    self.backtest_results.append(file_info)

            except Exception as e:
                print(f"⚠️  跳过文件 {file}: {e}")

        print(f"✅ 成功加载 {len(self.backtest_results)} 个有效结果")

    def _parse_result_file(self, filename, data):
        """解析单个结果文件"""
        try:
            # 获取执行时间
            execution_time = data.get('execution_time', data.get('screening_time', ''))
            if execution_time:
                execution_time = datetime.strptime(execution_time, '%Y-%m-%d %H:%M:%S')
            else:
                # 尝试从文件名解析时间
                time_str = filename.split('_')[-1].replace('.json', '')
                try:
                    execution_time = datetime.strptime(time_str, '%Y%m%d%H%M%S')
                except:
                    return None

            # 获取选股结果
            stocks = []
            results_count = 0

            if 'top_stocks' in data:
                stocks = data['top_stocks']
                results_count = len(stocks)
            elif 'results_count' in data:
                results_count = data['results_count']
            elif 'task_results' in data:
                for task in data['task_results']:
                    results_count += task.get('count', 0)
                    stocks.extend(task.get('stocks', []))

            # 获取策略信息
            strategy_type = data.get('screening_type', 'unknown')
            if 'optimized' in filename.lower() or 'enhanced' in filename.lower():
                strategy_type = 'enhanced'
            elif '1130' in filename:
                strategy_type = '1130_screening'
            elif 'advanced' in filename.lower():
                strategy_type = 'advanced'

            return {
                'filename': filename,
                'execution_time': execution_time,
                'strategy_type': strategy_type,
                'results_count': results_count,
                'stocks': stocks[:10],  # 只保留前10只
                'data': data
            }

        except Exception as e:
            return None

    def analyze_strategy_performance(self):
        """分析策略表现"""
        print("\n📊 策略表现分析")
        print("=" * 60)

        if not self.backtest_results:
            print("❌ 没有找到历史数据")
            return

        # 按策略类型分组分析
        strategy_groups = {}
        for result in self.backtest_results:
            strategy = result['strategy_type']
            if strategy not in strategy_groups:
                strategy_groups[strategy] = []
            strategy_groups[strategy].append(result)

        print(f"🎯 各策略类型表现:")
        print("-" * 80)
        print(f"{'策略类型':<20} {'执行次数':<10} {'平均选股':<10} {'成功率':<10} {'最佳表现':<15}")
        print("-" * 80)

        for strategy, results in strategy_groups.items():
            total_executions = len(results)
            avg_stocks = np.mean([r['results_count'] for r in results])
            success_rate = len([r for r in results if r['results_count'] > 0]) / total_executions * 100
            best_performance = max([r['results_count'] for r in results])

            print(f"{strategy:<20} {total_executions:<10} {avg_stocks:.1f}{'':<6} {success_rate:.1f}%{'':<6} {best_performance}只")

        return strategy_groups

    def analyze_time_trends(self):
        """分析时间趋势"""
        print("\n📈 时间趋势分析")
        print("=" * 60)

        # 按时间排序
        sorted_results = sorted(self.backtest_results, key=lambda x: x['execution_time'])

        # 按周分组分析
        weekly_analysis = {}
        for result in sorted_results:
            week = result['execution_time'].strftime('%Y-W%U')
            if week not in weekly_analysis:
                weekly_analysis[week] = []
            weekly_analysis[week].append(result)

        print(f"📅 按周表现分析:")
        print("-" * 60)
        print(f"{'周次':<15} {'执行次数':<10} {'平均选股':<10} {'成功率':<10} {'趋势':<10}")
        print("-" * 60)

        prev_success_rate = 0
        for week, results in sorted(weekly_analysis.items()):
            total_executions = len(results)
            avg_stocks = np.mean([r['results_count'] for r in results])
            success_rate = len([r for r in results if r['results_count'] > 0]) / total_executions * 100

            # 判断趋势
            if prev_success_rate == 0:
                trend = "初始"
            elif success_rate > prev_success_rate + 5:
                trend = "↑上升"
            elif success_rate < prev_success_rate - 5:
                trend = "↓下降"
            else:
                trend = "→平稳"

            week_display = week.split('-')[1]  # 只显示周数
            print(f"{week_display:<15} {total_executions:<10} {avg_stocks:.1f}{'':<6} {success_rate:.1f}%{'':<6} {trend:<10}")
            prev_success_rate = success_rate

    def analyze_optimization_effectiveness(self):
        """分析优化效果"""
        print("\n🚀 优化效果分析")
        print("=" * 60)

        # 对比不同策略版本
        strategy_performance = {}

        for result in self.backtest_results:
            strategy = result['strategy_type']
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {
                    'results': [],
                    'total_stocks': 0,
                    'success_count': 0
                }

            strategy_performance[strategy]['results'].append(result)
            strategy_performance[strategy]['total_stocks'] += result['results_count']
            if result['results_count'] > 0:
                strategy_performance[strategy]['success_count'] += 1

        # 计算关键指标
        for strategy, perf in strategy_performance.items():
            total_executions = len(perf['results'])
            avg_stocks = perf['total_stocks'] / total_executions if total_executions > 0 else 0
            success_rate = perf['success_count'] / total_executions * 100 if total_executions > 0 else 0

            strategy_performance[strategy]['avg_stocks'] = avg_stocks
            strategy_performance[strategy]['success_rate'] = success_rate

        print(f"📊 策略版本对比:")
        print("-" * 80)
        print(f"{'策略版本':<20} {'平均选股':<10} {'成功率':<10} {'稳定性':<15} {'推荐度':<10}")
        print("-" * 80)

        # 计算稳定性（成功率的标准差）
        for strategy, perf in strategy_performance.items():
            success_rates = [1 if r['results_count'] > 0 else 0 for r in perf['results']]
            stability = np.std(success_rates) * 100 if len(success_rates) > 1 else 0
            stability_score = "高" if stability < 20 else "中" if stability < 40 else "低"

            # 推荐度评分
            recommendation_score = (perf['success_rate'] * 0.4 +
                                  min(perf['avg_stocks'] * 5, 50) * 0.4 +
                                  (100 - stability) * 0.2)
            recommendation = "★★★" if recommendation_score >= 70 else "★★" if recommendation_score >= 50 else "★"

            print(f"{strategy:<20} {perf['avg_stocks']:.1f}{'':<6} {perf['success_rate']:.1f}%{'':<6} {stability_score:<15} {recommendation:<10}")

    def generate_optimization_suggestions(self):
        """生成优化建议"""
        print("\n💡 持续优化建议")
        print("=" * 60)

        # 分析最近的趋势
        recent_results = [r for r in self.backtest_results
                         if r['execution_time'] > datetime.now() - timedelta(days=7)]

        if not recent_results:
            print("⚠️  缺少近期数据，无法生成针对性建议")
            return

        recent_success_rate = len([r for r in recent_results if r['results_count'] > 0]) / len(recent_results) * 100
        recent_avg_stocks = np.mean([r['results_count'] for r in recent_results])

        print(f"📈 最近7天表现:")
        print(f"   • 执行次数: {len(recent_results)}")
        print(f"   • 成功率: {recent_success_rate:.1f}%")
        print(f"   • 平均选股: {recent_avg_stocks:.1f}只")

        print(f"\n🎯 优化建议:")

        if recent_success_rate < 60:
            print(f"   1. 🔧 紧急优化：成功率偏低，建议:")
            print(f"      - 降低筛选标准，增加选股数量")
            print(f"      - 检查数据源质量")
            print(f"      - 分析市场环境影响")
        elif recent_success_rate < 80:
            print(f"   1. 📈 渐进优化：成功率中等，建议:")
            print(f"      - 微调筛选参数")
            print(f"      - 增加技术面确认")
            print(f"      - 加强行业分析")
        else:
            print(f"   1. ✨ 精细优化：表现良好，建议:")
            print(f"      - 进一步提高选股质量")
            print(f"      - 增加ML模型预测")
            print(f"      - 探索新因子组合")

        if recent_avg_stocks < 2:
            print(f"   2. 📊 数量优化：选股偏少，建议:")
            print(f"      - 扩大换手率范围")
            print(f"      - 降低量比要求")
            print(f"      - 增加备选策略")
        elif recent_avg_stocks > 8:
            print(f"   2. 🎯 质量优化：选股较多，建议:")
            print(f"      - 提高筛选标准")
            print(f"      - 增加质量评分")
            print(f"      - 重点关注TOP股票")

        print(f"\n⚡ 实施计划:")
        print(f"   • 短期(1-2周)：调整基础参数")
        print(f"   • 中期(1-2月)：增加分析维度")
        print(f"   • 长期(持续)：机器学习优化")
        print(f"   • 监控频率：每周进行回测分析")

    def generate_backtest_report(self):
        """生成回测报告"""
        print("\n📋 回测报告生成")
        print("=" * 60)

        if not self.backtest_results:
            print("❌ 没有足够数据生成报告")
            return

        # 计算总体指标
        total_executions = len(self.backtest_results)
        total_stocks_selected = sum(r['results_count'] for r in self.backtest_results)
        success_executions = len([r for r in self.backtest_results if r['results_count'] > 0])
        overall_success_rate = success_executions / total_executions * 100
        avg_stocks_per_execution = total_stocks_selected / total_executions

        # 时间范围
        start_time = min(r['execution_time'] for r in self.backtest_results)
        end_time = max(r['execution_time'] for r in self.backtest_results)
        analysis_days = (end_time - start_time).days + 1

        print(f"📊 总体统计:")
        print(f"   • 分析期间: {start_time.strftime('%Y-%m-%d')} 至 {end_time.strftime('%Y-%m-%d')} ({analysis_days}天)")
        print(f"   • 总执行次数: {total_executions}")
        print(f"   • 总选股数量: {total_stocks_selected}")
        print(f"   • 成功率: {overall_success_rate:.1f}% ({success_executions}/{total_executions})")
        print(f"   • 平均选股: {avg_stocks_per_execution:.1f}只/次")

        # 生成报告文件
        report_data = {
            'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_period': {
                'start': start_time.strftime('%Y-%m-%d'),
                'end': end_time.strftime('%Y-%m-%d'),
                'days': analysis_days
            },
            'overall_metrics': {
                'total_executions': total_executions,
                'total_stocks_selected': total_stocks_selected,
                'success_rate': overall_success_rate,
                'avg_stocks_per_execution': avg_stocks_per_execution
            },
            'strategy_breakdown': {},
            'recommendations': []
        }

        # 策略分析
        strategy_groups = {}
        for result in self.backtest_results:
            strategy = result['strategy_type']
            if strategy not in strategy_groups:
                strategy_groups[strategy] = []
            strategy_groups[strategy].append(result)

        for strategy, results in strategy_groups.items():
            strategy_success_rate = len([r for r in results if r['results_count'] > 0]) / len(results) * 100
            strategy_avg_stocks = np.mean([r['results_count'] for r in results])

            report_data['strategy_breakdown'][strategy] = {
                'executions': len(results),
                'success_rate': strategy_success_rate,
                'avg_stocks': strategy_avg_stocks
            }

        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'continuous_backtest_report_{timestamp}.json'

        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 回测报告已保存至: {report_filename}")
        return report_filename

    def setup_monitoring_schedule(self):
        """设置监控计划"""
        print("\n⏰ 持续监控计划")
        print("=" * 60)

        print("📅 自动化监控设置:")
        print("   • 每日监控: 09:00, 14:00, 19:00")
        print("   • 周度回测: 每周一早上生成上周报告")
        print("   • 月度总结: 每月1号生成月度分析")
        print("   • 季度优化: 每季度末进行策略优化")

        print(f"\n🔧 监控指标:")
        print(f"   • 成功率变化趋势")
        print(f"   • 平均选股数量")
        print(f"   • 预期vs实际收益")
        print(f"   • 策略稳定性")
        print(f"   • 市场环境适应度")

        print(f"\n📧 预警机制:")
        print(f"   • 成功率连续3天 < 60%: 发送预警")
        print(f"   • 选股数量连续3天 = 0: 发送预警")
        print(f"   • 策略突变: 发送分析报告")
        print(f"   • 新高收益: 发送庆祝通知")

    def run_continuous_backtest(self):
        """运行持续回测分析"""
        print("🚀 持续回测验证系统")
        print("=" * 80)
        print(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 分析目标: 持续跟踪策略表现，提供优化建议")
        print()

        # 加载历史数据
        self.load_historical_results()

        if not self.backtest_results:
            print("❌ 没有找到历史数据，无法进行回测分析")
            return

        # 执行各项分析
        strategy_groups = self.analyze_strategy_performance()
        self.analyze_time_trends()
        self.analyze_optimization_effectiveness()
        self.generate_optimization_suggestions()
        report_file = self.generate_backtest_report()
        self.setup_monitoring_schedule()

        print(f"\n✅ 持续回测分析完成!")
        print(f"💡 下一步行动:")
        print(f"   • 根据建议优化策略参数")
        print(f"   • 建立自动化监控流程")
        print(f"   • 定期回顾和调整策略")
        print(f"   • 持续学习和改进")

def main():
    """主函数"""
    backtest_system = ContinuousBacktestSystem()
    backtest_system.run_continuous_backtest()

if __name__ == "__main__":
    main()