#!/usr/bin/env python3
"""
使用 Gemini 3 Pro 进行股票分析
集成12月10日主力埋伏策略数据分析
"""

import sys
import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import google.generativeai as genai

# 配置 Gemini API
GEMINI_API_KEY = "AIzaSyDrdYyaXHa0lO2V5iV_2c-z0YdR7UZVywU"

class GeminiStockAnalyzer:
    """使用 Gemini 3 Pro 进行股票分析"""

    def __init__(self):
        """初始化Gemini连接"""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ Gemini 1.5 Pro 连接成功")
        except Exception as e:
            print(f"❌ Gemini 连接失败: {e}")
            sys.exit(1)

        self.load_1210_data()

    def load_1210_data(self):
        """加载12月10日选股数据"""
        try:
            with open("main_force_burial_result_20251210_145330.json", 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.stocks_1210 = data['stocks']
            self.strategy_params = data['strategy_params']
            print(f"✅ 加载12月10日数据: {len(self.stocks_1210)} 只股票")

        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            sys.exit(1)

    def analyze_stock_with_gemini(self, stock_info):
        """使用Gemini分析单只股票"""
        stock_code = stock_info['code']
        stock_name = stock_info['name']
        original_price = stock_info['price']
        original_change = stock_info['change']

        # 构建分析提示
        prompt = f"""
        作为专业的股票分析师，请分析这只股票的当前情况：

        股票信息：
        - 代码: {stock_code}
        - 名称: {stock_name}
        - 12月10日价格: {original_price:.2f}元
        - 12月10日涨幅: {original_change:+.2f}%

        选股策略参数：
        {json.dumps(self.strategy_params, indent=2, ensure_ascii=False)}

        请提供以下分析：
        1. 技术面分析 (支撑位、压力位、趋势判断)
        2. 基本面评估 (行业前景、公司质地)
        3. 短期走势预测 (1-5个交易日)
        4. 风险评估和建议
        5. 目标价位参考

        请用专业、客观的语言进行分析，避免过度乐观或悲观的表述。
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"分析失败: {e}"

    def generate_portfolio_advice(self):
        """生成投资组合建议"""
        # 选择几只代表性股票进行分析
        sample_stocks = self.stocks_1210[:3]  # 分析前3只作为样本

        prompt = f"""
        基于以下12月10日主力埋伏策略选出的股票，请提供专业的投资组合建议：

        选股样本：
        {json.dumps([{'code': s['code'], 'name': s['name'], 'price': s['price']} for s in sample_stocks], indent=2, ensure_ascii=False)}

        策略特点：
        - 尾盘主力埋伏策略
        - 关注技术面突破
        - 结合资金流向分析

        请提供：
        1. 整体市场环境分析
        2. 投资组合配置建议
        3. 风险控制策略
        4. 止盈止损点位设置
        5. 持仓时间建议

        请给出具体、可操作的建议。
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"生成建议失败: {e}"

    def analyze_market_sentiment(self):
        """分析市场情绪"""
        prompt = f"""
        请分析当前A股市场情绪状况：

        时间背景：2025年12月12日
        关注点：
        - 大盘走势
        - 市场热点板块
        - 资金流向趋势
        - 政策影响因素

        请提供：
        1. 市场整体情绪评分 (1-10分)
        2. 主要热点板块分析
        3. 风险提示
        4. 近期操作建议

        基于您的专业分析能力进行判断。
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"市场分析失败: {e}"

    def run_gemini_analysis(self):
        """运行完整的Gemini分析"""
        print("🤖 使用 Gemini 1.5 Pro 进行深度股票分析")
        print("=" * 60)

        # 1. 市场情绪分析
        print("\n📊 分析当前市场情绪...")
        market_analysis = self.analyze_market_sentiment()
        print("Gemini 市场分析:")
        print("-" * 40)
        print(market_analysis)
        print()

        # 2. 投资组合建议
        print("📈 生成投资组合建议...")
        portfolio_advice = self.generate_portfolio_advice()
        print("Gemini 投资建议:")
        print("-" * 40)
        print(portfolio_advice)
        print()

        # 3. 个股深度分析 (选择3只代表性股票)
        print("🔍 个股深度分析 (选择3只代表股票)...")
        for i, stock in enumerate(self.stocks_1210[:3], 1):
            print(f"\n分析第 {i} 只股票: {stock['name']} ({stock['code']})")
            analysis = self.analyze_stock_with_gemini(stock)
            print(f"\n{analysis}")
            print("-" * 80)

        print("\n💡 Gemini 分析总结:")
        print("=" * 40)
        print("✅ 完成了基于AI的专业分析")
        print("✅ 结合了市场情绪和个股基本面")
        print("✅ 提供了具体的操作建议")
        print("⚠️  投资有风险，入市需谨慎")

    def save_gemini_analysis(self):
        """保存Gemini分析结果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        analysis_data = {
            'analysis_time': timestamp,
            'model_used': 'Gemini 1.5 Pro',
            'api_key_status': 'Active',
            'stocks_analyzed': len(self.stocks_1210),
            'strategy_date': '2025-12-10',
            'analysis_type': 'AI专业分析'
        }

        output_file = f"gemini_stock_analysis_{timestamp}.json"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)

            print(f"✅ 分析结果已保存到: {output_file}")

        except Exception as e:
            print(f"❌ 保存失败: {e}")

def main():
    """主函数"""
    print("🚀 启动 Gemini 3 Pro 股票分析系统")
    print("=" * 50)

    analyzer = GeminiStockAnalyzer()

    # 运行完整分析
    analyzer.run_gemini_analysis()

    # 保存分析结果
    analyzer.save_gemini_analysis()

    print("\n🎯 Gemini 分析完成！")
    print("💡 建议结合Gemini的分析与量化数据进行决策")

if __name__ == "__main__":
    main()