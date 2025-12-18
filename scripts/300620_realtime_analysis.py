#!/usr/bin/env python3
"""
300620光库科技实时数据分析报告
基于东方财富API获取的真实数据进行走势分析
"""

import requests
import json
from datetime import datetime
import sys

class RealtimeDataAnalyzer:
    """实时数据分析器"""

    def __init__(self):
        self.stock_code = "300620"
        self.stock_name = "光库科技"
        self.secid = "0.300620"  # 东方财富市场代码

    def get_realtime_data(self):
        """获取实时行情数据"""
        try:
            url = f"https://8.push2.eastmoney.com/api/qt/stock/get"
            params = {
                'secid': self.secid,
                'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f59,f60,f61,f62,f63,f64,f65,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f78,f79,f80,f81,f82,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f116,f117,f148,f152'
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('rc') == 0 and data.get('data'):
                    return self.parse_eastmoney_data(data['data'])

            return None

        except Exception as e:
            print(f"❌ 获取实时数据失败: {e}")
            return None

    def parse_eastmoney_data(self, raw_data):
        """解析东方财富数据格式"""
        try:
            # 根据东方财富API字段映射解析数据
            parsed_data = {
                'stock_name': raw_data.get('f58', '光库科技'),
                'stock_code': raw_data.get('f57', '300620'),
                'current_price': raw_data.get('f43', 0) / 100,  # 最新价，分转元
                'open_price': raw_data.get('f46', 0) / 100,     # 开盘价
                'high_price': raw_data.get('f44', 0) / 100,     # 最高价
                'low_price': raw_data.get('f45', 0) / 100,      # 最低价
                'pre_close': raw_data.get('f60', 0) / 100,      # 昨收价
                'volume': raw_data.get('f47', 0),               # 成交量(手)
                'amount': raw_data.get('f48', 0),               # 成交额(元)
                'turnover_rate': raw_data.get('f168', 0) if 'f168' in raw_data else 0,  # 换手率
                'pe_ratio': raw_data.get('f92', 0),             # 市盈率
                'market_cap': raw_data.get('f116', 0),          # 总市值
                'circulating_cap': raw_data.get('f117', 0),     # 流通市值
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 计算涨跌额和涨跌幅
            if parsed_data['pre_close'] > 0:
                parsed_data['change'] = parsed_data['current_price'] - parsed_data['pre_close']
                parsed_data['change_percent'] = (parsed_data['change'] / parsed_data['pre_close']) * 100

            # 格式化成交量和成交额
            parsed_data['volume_shares'] = parsed_data['volume'] * 100  # 手转股
            parsed_data['amount_yuan'] = parsed_data['amount']

            return parsed_data

        except Exception as e:
            print(f"❌ 数据解析失败: {e}")
            return None

    def get_intraday_trend(self):
        """获取分时走势数据"""
        try:
            url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
            params = {
                'secid': self.secid,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65',
                'klt': '1',  # 1分钟
                'lmt': '30'  # 获取30条数据
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('rc') == 0 and data.get('data'):
                    return data['data']

            return None

        except Exception as e:
            print(f"❌ 获取分时数据失败: {e}")
            return None

    def analyze_technical_indicators(self, data):
        """分析技术指标"""
        if not data:
            return None

        indicators = {}

        # 价格位置分析
        current = data['current_price']
        high = data['high_price']
        low = data['low_price']
        pre_close = data['pre_close']

        if high > low:
            indicators['price_position'] = (current - low) / (high - low) * 100

        # 涨跌强度分析
        indicators['change_strength'] = abs(data['change_percent'])
        indicators['trend_direction'] = '上涨' if data['change_percent'] > 0 else '下跌' if data['change_percent'] < 0 else '平盘'

        # 成交量分析
        volume = data.get('volume_shares', 0)
        amount = data.get('amount_yuan', 0)

        if volume > 0:
            indicators['avg_price'] = amount / volume
            indicators['volume_intensity'] = '高' if volume > 10000000 else '中' if volume > 5000000 else '低'

        # 振幅分析
        if pre_close > 0:
            indicators['amplitude'] = (high - low) / pre_close * 100

        return indicators

    def generate_trading_signals(self, data, indicators):
        """生成交易信号"""
        signals = []

        if not data or not indicators:
            return signals

        change_percent = data['change_percent']
        price_position = indicators.get('price_position', 50)
        amplitude = indicators.get('amplitude', 0)

        # 趋势信号
        if change_percent > 3:
            signals.append("📈 强势上涨，关注持续动能")
        elif change_percent > 1:
            signals.append("🟢 温和上涨，趋势向好")
        elif change_percent < -3:
            signals.append("📉 大幅下跌，谨慎观望")
        elif change_percent < -1:
            signals.append("🔻 温和下跌，关注支撑")
        else:
            signals.append("➡️ 震荡整理，等待方向")

        # 价格位置信号
        if price_position > 80:
            signals.append("⚠️ 价格处于高位，注意风险")
        elif price_position < 20:
            signals.append("💡 价格处于低位，存在机会")

        # 振幅信号
        if amplitude > 5:
            signals.append("🌊 波动较大，操作需谨慎")
        elif amplitude < 2:
            signals.append("📊 波动较小，可能即将选择方向")

        # 时间信号（当前11:30左右）
        current_hour = datetime.now().hour
        if current_hour == 11:
            signals.append("⏰ 午前收盘，关注午后走势")

        return signals

    def predict_afternoon_trend(self, data, indicators):
        """预测下午走势"""
        if not data or not indicators:
            return "无法预测"

        current_price = data['current_price']
        change_percent = data['change_percent']
        high_price = data['high_price']
        low_price = data['low_price']

        # 基于上午表现预测下午
        predictions = []

        # 强势分析
        if change_percent > 2 and current_price > (high_price + low_price) / 2:
            predictions.append("下午有望继续冲高，但需关注量能配合")
        elif change_percent > 0 and current_price > (high_price + low_price) / 2:
            predictions.append("下午可能震荡上行，建议逢低关注")
        elif change_percent < -2 and current_price < (high_price + low_price) / 2:
            predictions.append("下午可能继续探底，关注支撑位")
        elif change_percent < 0 and current_price < (high_price + low_price) / 2:
            predictions.append("下午可能低位震荡，关注反弹机会")
        else:
            predictions.append("下午可能延续震荡格局，等待方向选择")

        # 关键价位分析
        predictions.append(f"关键支撑: {low_price:.2f}元")
        predictions.append(f"关键压力: {high_price:.2f}元")

        return "; ".join(predictions)

    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("🚀 300620光库科技实时数据分析报告")
        print("=" * 60)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据来源: 东方财富API")
        print()

        # 获取实时数据
        data = self.get_realtime_data()
        if not data:
            print("❌ 无法获取实时数据，请检查网络连接")
            return None

        # 显示实时行情
        print("📊 实时行情数据")
        print("-" * 40)
        print(f"股票名称: {data['stock_name']} ({data['stock_code']})")
        print(f"最新价格: {data['current_price']:.2f}元")
        print(f"涨跌情况: {data['change']:+.2f} ({data['change_percent']:+.2f}%)")
        print(f"开盘价格: {data['open_price']:.2f}元")
        print(f"最高价格: {data['high_price']:.2f}元")
        print(f"最低价格: {data['low_price']:.2f}元")
        print(f"昨收价格: {data['pre_close']:.2f}元")
        print(f"成交量: {data['volume']:,}手")
        print(f"成交额: {data['amount']:,.0f}元")

        if data.get('pe_ratio', 0) > 0:
            print(f"市盈率: {data['pe_ratio']:.2f}")
        if data.get('market_cap', 0) > 0:
            print(f"总市值: {data['market_cap']:.0f}元")

        print(f"更新时间: {data['update_time']}")

        # 技术分析
        print(f"\n📈 技术分析")
        print("-" * 40)
        indicators = self.analyze_technical_indicators(data)

        if indicators:
            print(f"价格位置: {indicators.get('price_position', 0):.1f}% (当日高低点区间)")
            print(f"趋势方向: {indicators.get('trend_direction', '未知')}")
            print(f"涨跌强度: {indicators.get('change_strength', 0):.2f}%")
            print(f"波动幅度: {indicators.get('amplitude', 0):.2f}%")
            print(f"成交量级: {indicators.get('volume_intensity', '未知')}")

        # 交易信号
        print(f"\n🎯 交易信号")
        print("-" * 40)
        signals = self.generate_trading_signals(data, indicators)

        for signal in signals:
            print(f"• {signal}")

        # 下午走势预测
        print(f"\n🔮 下午走势预测")
        print("-" * 40)
        prediction = self.predict_afternoon_trend(data, indicators)
        print(f"💡 {prediction}")

        # 操作建议
        print(f"\n💰 操作建议")
        print("-" * 40)

        change_percent = data['change_percent']

        if change_percent > 3:
            print("⚠️ 涨幅较大，不建议追高")
            print("🎯 关注回调机会，支撑位可适量参与")
            print("🛡️ 严格止损，控制风险")
        elif change_percent > 0:
            print("🟢 趋势向好，可择机参与")
            print("📊 关注成交量配合情况")
            print("💡 建议分批建仓，不宜重仓")
        elif change_percent < -3:
            print("📉 跌幅较大，谨慎观望")
            print("🔍 关注支撑位表现")
            print("⏰ 等待企稳信号")
        else:
            print("➡️ 震荡整理，等待方向")
            print("📈 关注突破信号")
            print("⏳ 保持耐心，不宜急于操作")

        # 风险提示
        print(f"\n⚠️ 风险提示")
        print("-" * 40)
        print("• 股市有风险，投资需谨慎")
        print("• 本分析仅供参考，不构成投资建议")
        print("• 建议结合更多技术指标和基本面分析")
        print("• 请根据自身风险承受能力做出投资决策")
        print("• 注意仓位管理，分散投资风险")

        return data, indicators, signals

def main():
    """主函数"""
    analyzer = RealtimeDataAnalyzer()
    result = analyzer.generate_comprehensive_report()

    if result:
        data, indicators, signals = result
        print(f"\n✅ 分析完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ 分析失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()