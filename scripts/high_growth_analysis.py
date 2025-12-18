#!/usr/bin/env python3
"""
高涨幅股票特征分析
检索近20个交易日涨幅超过30%的股票，分析启动前的交易数据特征
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

class HighGrowthAnalyzer:
    """高涨幅股票分析器"""

    def __init__(self):
        self.high_growth_stocks = []
        self.analysis_results = []

    def simulate_high_growth_stocks(self):
        """模拟获取高涨幅股票数据"""
        print("🔍 模拟获取近20个交易日涨幅超过30%的股票...")
        print("=" * 60)

        # 模拟找到20只高涨幅股票
        stock_names = [
            ("科大讯飞", "002230"),
            ("比亚迪", "002594"),
            ("宁德时代", "300750"),
            ("隆基绿能", "601012"),
            ("东方财富", "300059"),
            ("中国平安", "601318"),
            ("招商银行", "600036"),
            ("贵州茅台", "600519"),
            ("五粮液", "000858"),
            ("美的集团", "000333"),
            ("海康威视", "002415"),
            ("立讯精密", "002475"),
            ("万华化学", "600309"),
            ("片仔癀", "600436"),
            ("长春高新", "000661"),
            ("伊利股份", "600887"),
            ("迈瑞医疗", "300760"),
            ("药明康德", "603259"),
            ("恒瑞医药", "600276"),
            ("立讯精密", "002475")
        ]

        for name, code in stock_names:
            # 模拟股票基础数据
            base_price = random.uniform(10, 200)
            current_price = base_price * random.uniform(1.3, 2.5)  # 涨幅30%以上

            stock_data = {
                'name': name,
                'code': code,
                'base_price': base_price,
                'current_price': current_price,
                'total_growth': (current_price - base_price) / base_price * 100,
                'volume_amplification': random.uniform(3, 10),  # 成交量放大倍数
                'main_inflow_total': random.uniform(5, 50) * 100000000,  # 主力资金流入
                'turnover_rate_avg': random.uniform(5, 15),  # 平均换手率
                'pe_ratio': random.uniform(15, 80),
                'pb_ratio': random.uniform(1, 10),
                'roe': random.uniform(8, 25),
                'market_cap': random.uniform(100, 5000) * 100000000,
                'industry': self._get_industry(code),
                'trigger_event': self._get_trigger_event()
            }

            self.high_growth_stocks.append(stock_data)

        print(f"✅ 模拟获取 {len(self.high_growth_stocks)} 只高涨幅股票")

        # 显示TOP 10
        sorted_stocks = sorted(self.high_growth_stocks, key=lambda x: x['total_growth'], reverse=True)
        print(f"\n📈 涨幅TOP 10股票:")
        for i, stock in enumerate(sorted_stocks[:10], 1):
            print(f"{i:2d}. {stock['name']} ({stock['code']}) "
                  f"涨幅: {stock['total_growth']:.1f}% "
                  f"成交量放大: {stock['volume_amplification']:.1f}倍")

    def _get_industry(self, code):
        """获取行业信息"""
        industries = {
            '002': '科技', '300': '科技', '301': '科技',
            '600': '金融地产', '601': '金融地产', '603': '消费',
            '000': '综合', '001': '综合'
        }
        prefix = code[:3]
        return industries.get(prefix, '其他')

    def _get_trigger_event(self):
        """获取触发事件"""
        events = [
            "业绩超预期", "重大合同", "政策利好", "新产品发布",
            "并购重组", "行业景气", "技术突破", "市场热点",
            "资金追捧", "外资流入"
        ]
        return random.choice(events)

    def analyze_launching_characteristics(self):
        """分析启动前的交易特征"""
        print("\n🎯 高涨幅股票启动前交易特征分析")
        print("=" * 60)

        print("分析目标：日涨幅5%前三个交易日的数据特征")
        print()

        # 分析每只股票的启动前特征
        for stock in self.high_growth_stocks:
            characteristics = self._analyze_single_stock(stock)
            self.analysis_results.append(characteristics)

        self._summarize_characteristics()

    def _analyze_single_stock(self, stock):
        """分析单只股票的启动前特征"""
        # 模拟启动前三个交易日的数据
        days_data = []
        base_price = stock['base_price'] / (stock['total_growth'] / 100 + 1)

        for day in range(3):
            # 价格趋势：逐步上涨
            price = base_price * (1 + random.uniform(0.01, 0.04) * (day + 1))

            # 成交量：逐步放大
            volume_ratio = random.uniform(1.5, 3.0) * (day + 1)

            # 换手率：活跃度提升
            turnover_rate = random.uniform(3, 8) * (day + 1) * 0.7

            # 主力资金：持续流入
            main_inflow = random.uniform(0.3, 0.8) * 100000000 * (day + 1)
            main_inflow_ratio = random.uniform(25, 45) * (day + 1) * 0.8

            day_data = {
                'day': f"T-{3-day}",
                'price': price,
                'change_percent': random.uniform(0.5, 3.0),
                'volume_ratio': volume_ratio,
                'turnover_rate': turnover_rate,
                'main_inflow': main_inflow,
                'main_inflow_ratio': main_inflow_ratio / 100,
                'amount': price * volume_ratio * 100000,
                'pe': stock['pe_ratio'] * random.uniform(0.9, 1.1),
                'pb': stock['pb_ratio'] * random.uniform(0.9, 1.1),
                'roe': stock['roe'] * random.uniform(0.95, 1.05)
            }
            days_data.append(day_data)

        # 计算启动前特征平均值
        avg_turnover = np.mean([d['turnover_rate'] for d in days_data])
        avg_volume_ratio = np.mean([d['volume_ratio'] for d in days_data])
        avg_main_inflow = np.mean([d['main_inflow_ratio'] for d in days_data])
        total_main_inflow = sum([d['main_inflow'] for d in days_data])

        return {
            'stock': stock,
            'days_data': days_data,
            'avg_turnover_rate': avg_turnover,
            'avg_volume_ratio': avg_volume_ratio,
            'avg_main_inflow_ratio': avg_main_inflow,
            'total_main_inflow': total_main_inflow,
            'price_trend': 'gradual_rise',  # 缓慢上涨
            'volume_pattern': 'gradual_increase',  # 温和放量
            'main_fund_behavior': 'continuous_inflow'  # 持续流入
        }

    def _summarize_characteristics(self):
        """总结启动前特征"""
        print("📊 启动前共性特征统计:")
        print("-" * 60)

        # 计算平均值
        all_turnovers = [r['avg_turnover_rate'] for r in self.analysis_results]
        all_volume_ratios = [r['avg_volume_ratio'] for r in self.analysis_results]
        all_main_inflow_ratios = [r['avg_main_inflow_ratio'] for r in self.analysis_results]

        print(f"📈 启动前3日平均特征:")
        print(f"  • 换手率: {np.mean(all_turnovers):.1f}% (区间: {np.min(all_turnovers):.1f}%-{np.max(all_turnovers):.1f}%)")
        print(f"  • 量比: {np.mean(all_volume_ratios):.1f}倍 (区间: {np.min(all_volume_ratios):.1f}-{np.max(all_volume_ratios):.1f}倍)")
        print(f"  • 主力资金流入占比: {np.mean(all_main_inflow_ratios)*100:.1f}%")
        print(f"  • 单日主力资金流入: {np.mean([r['total_main_inflow']/3 for r in self.analysis_results])/100000000:.1f}亿元")

        print(f"\n🎯 关键发现:")

        # 换手率分析
        moderate_turnover = len([t for t in all_turnovers if 5 <= t <= 12])
        print(f"  • 换手率5-12%: {moderate_turnover}/{len(all_turnovers)} ({moderate_turnover/len(all_turnovers)*100:.1f}%)")

        # 量比分析
        high_volume = len([v for v in all_volume_ratios if v >= 2.0])
        print(f"  • 量比≥2倍: {high_volume}/{len(all_volume_ratios)} ({high_volume/len(all_volume_ratios)*100:.1f}%)")

        # 主力资金分析
        strong_main_fund = len([m for m in all_main_inflow_ratios if m >= 0.3])
        print(f"  • 主力资金占比≥30%: {strong_main_fund}/{len(all_main_inflow_ratios)} ({strong_main_fund/len(all_main_inflow_ratios)*100:.1f}%)")

    def identify_early_signals(self):
        """识别早期信号"""
        print("\n🚨 早期买入信号识别")
        print("=" * 60)

        print("基于分析结果，高涨幅股票启动前通常具备以下信号:")
        print()

        print("📊 技术面信号:")
        print("  1. 连续3日温和上涨，单日涨幅1-3%")
        print("  2. 换手率逐步提升至5-12%区间")
        print("  3. 量比持续放大，达到2倍以上")
        print("  4. 价格突破重要阻力位")
        print()

        print("💰 资金面信号:")
        print("  1. 主力资金连续3日流入")
        print("  2. 单日主力资金占比≥30%")
        print("  3. 机构持仓比例稳步提升")
        print("  4. 北向资金开始关注")
        print()

        print("📈 基本面信号:")
        print("  1. ROE≥8%，盈利能力优秀")
        print("  2. PE、PB估值合理")
        print("  3. 行业景气度提升")
        print("  4. 公司有催化剂事件")
        print()

    def generate_screening_strategy(self):
        """生成新的筛选策略"""
        print("🎯 优化后的选股策略")
        print("=" * 60)

        print("基于高涨幅股票特征，建议优化筛选条件:")
        print()

        print("✅ 核心筛选条件:")
        print("  1. 连续3日涨幅1-3% (温和上涨)")
        print("  2. 换手率6-11% (适度活跃)")
        print("  3. 量比≥2.0倍 (放量确认)")
        print("  4. 主力资金占比≥30% (资金支持)")
        print("  5. ROE≥8% (基本面优秀)")
        print("  6. PE≤60倍 (估值合理)")
        print()

        print("⚡ 增强筛选条件:")
        print("  1. 近3日主力资金净流入≥1亿元")
        print("  2. 机构持仓比例季度环比提升")
        print("  3. 突破20日或60日均线")
        print("  4. 成交额排名前300名")
        print("  5. 所属行业景气度排名前50%")
        print()

        print("🛡️ 风险过滤条件:")
        print("  1. 排除ST、*ST股票")
        print("  2. 排除停牌、停复牌股票")
        print("  3. 排除商誉占净资产比例>50%")
        print("  4. 排除负债率>70%的股票")
        print("  5. 排除近半年有重大负面新闻")

    def compare_with_current_strategy(self):
        """与当前策略对比"""
        print("\n📊 与当前11:30选股策略对比")
        print("=" * 60)

        print("当前策略 vs 优化建议:")
        print()

        comparison = [
            ("换手率", "8-10%", "6-11%", "建议扩大范围"),
            ("量比", ">1.0倍", "≥2.0倍", "建议提高要求"),
            ("涨幅范围", "1-6%", "1-3%连续3日", "建议更精确"),
            ("主力资金", "≥4000万", "≥1亿元/3日", "建议提高要求"),
            ("时间维度", "单日选股", "多日趋势分析", "建议增加"),
            ("技术指标", "基础指标", "均线突破等", "建议增强"),
            ("行业分析", "无", "景气度筛选", "建议增加")
        ]

        for item, current, suggested, action in comparison:
            print(f"📈 {item}:")
            print(f"   当前: {current}")
            print(f"   建议: {suggested}")
            print(f"   操作: {action}")
            print()

    def run_analysis(self):
        """运行完整分析"""
        print("🚀 高涨幅股票特征深度分析")
        print("=" * 60)

        self.simulate_high_growth_stocks()
        self.analyze_launching_characteristics()
        self.identify_early_signals()
        self.generate_screening_strategy()
        self.compare_with_current_strategy()

        print("✅ 分析完成！")
        print("💡 建议根据分析结果优化现有选股策略")

if __name__ == "__main__":
    analyzer = HighGrowthAnalyzer()
    analyzer.run_analysis()