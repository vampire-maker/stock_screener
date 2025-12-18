#!/usr/bin/env python3
"""
股票筛选回测分析
分析最近一周的选股表现和收益情况
"""

import json
import glob
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter

def load_recent_results(days=7):
    """加载最近几天的选股结果"""
    cutoff_date = datetime.now() - timedelta(days=days)
    results = []

    # 查找所有结果文件
    result_files = glob.glob("enhanced_1130_result_*.json")
    result_files.extend(glob.glob("archive/results/enhanced_1130_result_*.json"))

    for file_path in sorted(result_files):
        try:
            # 从文件名提取日期
            filename = os.path.basename(file_path)
            date_part = filename.split('_')[3]
            file_date = datetime.strptime(date_part, '%Y%m%d')

            if file_date >= cutoff_date:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['source_file'] = file_path
                    results.append(data)

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            print(f"跳过文件 {file_path}: {e}")
            continue

    return results

def analyze_stock_performance(results):
    """分析股票表现"""
    all_stocks = []
    stock_appearances = Counter()
    stock_scores = defaultdict(list)
    screening_times = []

    for result in results:
        screening_time = datetime.strptime(result['screening_time'], '%Y-%m-%d %H:%M:%S')
        screening_times.append(screening_time)

        for stock in result.get('top_stocks', []):
            stock_code = stock['code']
            stock_name = stock['name']
            score = stock['screening_score']

            all_stocks.append({
                'code': stock_code,
                'name': stock_name,
                'screening_time': screening_time,
                'price': stock['price'],
                'change_percent': stock['change_percent'],
                'turnover_rate': stock['turnover_rate'],
                'volume_ratio': stock['volume_ratio'],
                'main_inflow': stock['main_inflow'],
                'main_inflow_ratio': stock['main_inflow_ratio'],
                'pe': stock['pe'],
                'pb': stock['pb'],
                'roe': stock['roe'],
                'score': score,
                'industry': stock.get('industry', '未知')
            })

            stock_appearances[stock_code] += 1
            stock_scores[stock_code].append(score)

    return all_stocks, stock_appearances, stock_scores, screening_times

def generate_backtest_report(results, all_stocks, stock_appearances, stock_scores, screening_times):
    """生成回测报告"""

    print("=" * 80)
    print("📈 股票筛选系统 - 最近一周回测分析报告")
    print("=" * 80)

    # 基础统计
    print(f"\n📊 基础统计")
    print("-" * 40)
    print(f"分析时间范围: {min(screening_times).strftime('%Y-%m-%d %H:%M')} 至 {max(screening_times).strftime('%Y-%m-%d %H:%M')}")
    print(f"总筛选次数: {len(results)} 次")
    print(f"总推荐股票: {len(all_stocks)} 只")
    print(f"平均每次推荐: {len(all_stocks)/len(results):.1f} 只")

    # 最频繁出现的股票
    print(f"\n🔥 热门推荐股票 (出现次数)")
    print("-" * 40)
    top_stocks = stock_appearances.most_common(10)
    for i, (code, count) in enumerate(top_stocks, 1):
        avg_score = sum(stock_scores[code]) / len(stock_scores[code])
        stock_info = next((s for s in all_stocks if s['code'] == code), None)
        if stock_info:
            print(f"{i:2d}. {code} {stock_info['name']:<8} - {count}次, 平均评分:{avg_score:.1f}")

    # 行业分布
    print(f"\n🏭 行业分布")
    print("-" * 40)
    industry_count = Counter([s['industry'] for s in all_stocks])
    for industry, count in industry_count.most_common():
        percentage = (count / len(all_stocks)) * 100
        print(f"{industry:<12} - {count:2d}只 ({percentage:.1f}%)")

    # 评分分析
    scores = [s['score'] for s in all_stocks]
    print(f"\n⭐ 评分分析")
    print("-" * 40)
    print(f"最高评分: {max(scores):.1f}")
    print(f"最低评分: {min(scores):.1f}")
    print(f"平均评分: {sum(scores)/len(scores):.1f}")

    # 技术指标分析
    print(f"\n📊 技术指标分析 (平均值)")
    print("-" * 40)
    print(f"涨幅: {sum(s['change_percent'] for s in all_stocks)/len(all_stocks):.2f}%")
    print(f"换手率: {sum(s['turnover_rate'] for s in all_stocks)/len(all_stocks):.2f}%")
    print(f"量比: {sum(s['volume_ratio'] for s in all_stocks)/len(all_stocks):.2f}")
    print(f"主力资金占比: {sum(s['main_inflow_ratio'] for s in all_stocks)/len(all_stocks):.2f}")
    print(f"PE: {sum(s['pe'] for s in all_stocks)/len(all_stocks):.1f}")
    print(f"PB: {sum(s['pb'] for s in all_stocks)/len(all_stocks):.1f}")
    print(f"ROE: {sum(s['roe'] for s in all_stocks)/len(all_stocks):.1f}%")

    # 高评分股票特征
    high_score_stocks = [s for s in all_stocks if s['score'] >= 85]
    if high_score_stocks:
        print(f"\n🏆 高评分股票特征 (评分≥85, 共{len(high_score_stocks)}只)")
        print("-" * 40)
        print(f"平均涨幅: {sum(s['change_percent'] for s in high_score_stocks)/len(high_score_stocks):.2f}%")
        print(f"平均换手率: {sum(s['turnover_rate'] for s in high_score_stocks)/len(high_score_stocks):.2f}%")
        print(f"平均量比: {sum(s['volume_ratio'] for s in high_score_stocks)/len(high_score_stocks):.2f}")
        print(f"平均主力资金: {sum(s['main_inflow'] for s in high_score_stocks)/len(high_score_stocks)/100000000:.1f}亿")

        print(f"\n高评分股票列表:")
        for stock in sorted(high_score_stocks, key=lambda x: x['score'], reverse=True):
            print(f"  {stock['code']} {stock['name']:<8} - 评分:{stock['score']:3.0f}, 涨幅:{stock['change_percent']:+5.2f}%, 换手:{stock['turnover_rate']:5.1f}%")

    return {
        'total_screenings': len(results),
        'total_stocks': len(all_stocks),
        'avg_stocks_per_screening': len(all_stocks)/len(results),
        'top_stocks': top_stocks,
        'industry_distribution': industry_count,
        'avg_score': sum(scores)/len(scores),
        'high_score_count': len(high_score_stocks)
    }

def analyze_strategy_performance(results):
    """分析策略表现"""
    print(f"\n🎯 策略表现分析")
    print("-" * 40)

    strategy_performance = defaultdict(list)
    for result in results:
        strategy_version = result.get('strategy_version', 'unknown')
        stocks_count = len(result.get('top_stocks', []))
        avg_score = sum(s['screening_score'] for s in result.get('top_stocks', [])) / stocks_count if stocks_count > 0 else 0

        strategy_performance[strategy_version].append({
            'date': result['screening_time'],
            'stocks_count': stocks_count,
            'avg_score': avg_score
        })

    for strategy, performances in strategy_performance.items():
        print(f"\n策略: {strategy}")
        print(f"执行次数: {len(performances)}")
        print(f"平均推荐股票数: {sum(p['stocks_count'] for p in performances)/len(performances):.1f}")
        print(f"平均评分: {sum(p['avg_score'] for p in performances)/len(performances):.1f}")

def generate_optimization_suggestions(analysis_results):
    """生成优化建议"""
    print(f"\n💡 优化建议")
    print("-" * 40)

    if analysis_results['high_score_count'] == 0:
        print("⚠️  当前策略筛选过于严格，建议适当放宽筛选条件")
    elif analysis_results['avg_score'] < 80:
        print("⚠️  平均评分偏低，建议优化筛选参数")
    else:
        print("✅ 策略表现良好，当前参数设置合理")

    print("\n建议检查以下指标:")
    print("• 换手率范围是否合适")
    print("• 量比要求是否过高")
    print("• 主力资金门槛是否需要调整")
    print("• PE/PB/ROE 等基本面指标设置")

def save_backtest_report(analysis_results, all_stocks):
    """保存回测报告到文件"""
    report_data = {
        'backtest_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'analysis_period': 'last_7_days',
        'summary': analysis_results,
        'all_stocks': all_stocks
    }

    filename = f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n💾 详细回测数据已保存至: {filename}")

def main():
    """主函数"""
    print("🔄 正在分析最近一周的选股结果...")

    # 加载结果数据
    results = load_recent_results(days=7)

    if not results:
        print("❌ 未找到最近一周的选股结果数据")
        return

    # 分析股票表现
    all_stocks, stock_appearances, stock_scores, screening_times = analyze_stock_performance(results)

    # 生成回测报告
    analysis_results = generate_backtest_report(results, all_stocks, stock_appearances, stock_scores, screening_times)

    # 分析策略表现
    analyze_strategy_performance(results)

    # 生成优化建议
    generate_optimization_suggestions(analysis_results)

    # 保存详细报告
    save_backtest_report(analysis_results, all_stocks)

    print("\n" + "=" * 80)
    print("✅ 回测分析完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()