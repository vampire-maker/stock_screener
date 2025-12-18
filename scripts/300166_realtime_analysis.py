#!/usr/bin/env python3
"""
东方国信(300166)实时数据分析报告
基于东方财富API获取的真实数据进行走势分析
"""

import requests
import json
from datetime import datetime

class EastGuoxinAnalyzer:
    """东方国信实时数据分析器"""

    def __init__(self):
        self.stock_code = "300166"
        self.stock_name = "东方国信"
        self.secid = "0.300166"  # 东方财富市场代码
        self.industry = "软件和信息技术服务业"

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
            parsed_data = {
                'stock_name': raw_data.get('f58', '东方国信'),
                'stock_code': raw_data.get('f57', '300166'),
                'current_price': raw_data.get('f43', 0) / 100,  # 最新价，分转元
                'open_price': raw_data.get('f46', 0) / 100,     # 开盘价
                'high_price': raw_data.get('f44', 0) / 100,     # 最高价
                'low_price': raw_data.get('f45', 0) / 100,      # 最低价
                'pre_close': raw_data.get('f60', 0) / 100,      # 昨收价
                'volume': raw_data.get('f47', 0),               # 成交量(手)
                'amount': raw_data.get('f48', 0),               # 成交额(元)
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

            return parsed_data

        except Exception as e:
            print(f"❌ 数据解析失败: {e}")
            return None

    def get_industry_analysis(self):
        """获取行业分析"""
        return {
            '行业名称': '软件和信息技术服务业',
            '行业前景': [
                '数字化转型加速，企业IT需求持续增长',
                '云计算、大数据、人工智能技术快速发展',
                '工业互联网、智能制造政策支持力度加大',
                '5G建设带来新的应用场景和需求'
            ],
            '公司优势': [
                '在企业级大数据平台领域有较强技术实力',
                '客户资源丰富，包括电信、金融、政府等多个行业',
                '在工业互联网领域有较好的布局',
                '技术研发投入占比较高，创新能力强'
            ],
            '风险因素': [
                '行业竞争激烈，技术更新迭代快',
                '客户集中度较高，依赖大客户订单',
                '研发投入大，短期盈利压力',
                '宏观经济波动影响企业IT支出'
            ]
        }

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

        if volume > 0:
            indicators['volume_intensity'] = '高' if volume > 10000000 else '中' if volume > 5000000 else '低'

        # 振幅分析
        if pre_close > 0:
            indicators['amplitude'] = (high - low) / pre_close * 100

        # 相对强度分析
        indicators['relative_strength'] = '强' if data['change_percent'] > 1 else '中' if data['change_percent'] > -1 else '弱'

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
            signals.append("📈 强势上涨，动能充足")
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
            signals.append("⚠️ 价格处于高位，注意回调风险")
        elif price_position < 20:
            signals.append("💡 价格处于低位，存在反弹机会")
        else:
            signals.append("📊 价格处于中位，方向待定")

        # 振幅信号
        if amplitude > 5:
            signals.append("🌊 波动较大，操作需谨慎")
        elif amplitude < 2:
            signals.append("📊 波动较小，可能即将选择方向")

        # 估值信号
        pe_ratio = data.get('pe_ratio', 0)
        if 0 < pe_ratio < 15:
            signals.append("💰 估值相对合理")
        elif 15 <= pe_ratio < 30:
            signals.append("📈 估值适中偏高")
        elif pe_ratio >= 30:
            signals.append("⚠️ 估值偏高，注意风险")

        return signals

    def predict_afternoon_trend(self, data, indicators):
        """预测下午走势"""
        if not data or not indicators:
            return "无法预测"

        current_price = data['current_price']
        change_percent = data['change_percent']
        high_price = data['high_price']
        low_price = data['low_price']
        volume_intensity = indicators.get('volume_intensity', '中')

        # 基于上午表现预测下午
        predictions = []

        # 综合分析预测
        if change_percent > 2 and volume_intensity == '高':
            predictions.append("强势突破，下午有望继续上行，但需关注量能持续性")
        elif change_percent > 0 and current_price > (high_price + low_price) / 2:
            predictions.append("上涨趋势，下午可能震荡上行，建议逢回调关注")
        elif change_percent < -2 and volume_intensity == '高':
            predictions.append("放量下跌，下午可能继续探底，关注关键支撑位")
        elif -2 <= change_percent <= 2:
            predictions.append("震荡格局，下午可能延续整理，等待方向选择")
        else:
            predictions.append("单边走势，下午可能延续当前趋势")

        # 关键价位分析
        predictions.append(f"关键支撑: {low_price:.2f}元")
        predictions.append(f"关键压力: {high_price:.2f}元")

        return "; ".join(predictions)

    def generate_company_profile(self):
        """生成公司概况"""
        return {
            '公司简介': '东方国信是中国领先的企业级大数据平台及行业应用解决方案提供商',
            '主营业务': [
                '企业级大数据平台建设与运营',
                '云计算、人工智能相关技术服务',
                '工业互联网平台建设',
                '电信、金融、政府等行业解决方案'
            ],
            '核心竞争优势': [
                '大数据平台技术实力雄厚',
                '多行业客户资源丰富',
                '研发创新能力突出',
                '工业互联网布局领先'
            ],
            '财务概况': {
                '市值规模': '约132亿',
                '估值水平': 'PE约5.14倍，相对合理',
                '行业地位': '大数据领域领先企业'
            }
        }

    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("🚀 东方国信(300166)实时数据分析报告")
        print("=" * 60)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据来源: 东方财富API")
        print(f"所属行业: {self.industry}")
        print()

        # 获取实时数据
        data = self.get_realtime_data()
        if not data:
            print("❌ 无法获取实时数据，请检查网络连接")
            return None

        # 显示公司概况
        print("🏢 公司概况")
        print("-" * 40)
        profile = self.generate_company_profile()
        print(f"公司名称: {data['stock_name']} ({data['stock_code']})")
        print(f"公司简介: {profile['公司简介']}")
        print(f"市值规模: {profile['财务概况']['市值规模']}")
        print(f"估值水平: PE约{data.get('pe_ratio', 0):.2f}倍，{profile['财务概况']['估值水平']}")
        print()

        # 显示实时行情
        print("📊 实时行情数据")
        print("-" * 40)
        print(f"最新价格: {data['current_price']:.2f}元")
        print(f"涨跌情况: {data['change']:+.2f} ({data['change_percent']:+.2f}%)")
        print(f"开盘价格: {data['open_price']:.2f}元")
        print(f"最高价格: {data['high_price']:.2f}元")
        print(f"最低价格: {data['low_price']:.2f}元")
        print(f"昨收价格: {data['pre_close']:.2f}元")
        print(f"成交量: {data['volume']:,}手")
        print(f"成交额: {data['amount']:,.0f}元")
        print(f"总市值: {data['market_cap']:.0f}元")
        print(f"更新时间: {data['update_time']}")

        # 行业分析
        print(f"\n🌍 行业分析")
        print("-" * 40)
        industry = self.get_industry_analysis()
        print(f"行业前景:")
        for item in industry['行业前景'][:2]:
            print(f"  • {item}")
        print(f"公司优势:")
        for item in industry['公司优势'][:2]:
            print(f"  • {item}")

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
            print(f"相对强度: {indicators.get('relative_strength', '未知')}")

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
        pe_ratio = data.get('pe_ratio', 0)

        # 基于估值和走势给出建议
        if pe_ratio < 10 and change_percent > 0:
            print("🟢 估值合理+趋势向好，值得关注")
            print("📊 可考虑逢低分批建仓")
            print("🎯 中长线投资价值显现")
        elif pe_ratio < 10 and change_percent < -1:
            print("💡 估值合理+短期调整，存在机会")
            print("🔍 关注支撑位表现")
            print("⏰ 企稳后可考虑参与")
        elif change_percent > 3:
            print("⚠️ 短期涨幅较大，谨慎追高")
            print("📈 关注成交量配合")
            print("🛡️ 建议等待回调机会")
        elif change_percent < -3:
            print("📉 短期调整幅度较大，关注风险")
            print("🔍 观察支撑位有效性")
            print("⏳ 不宜急于抄底")
        else:
            print("➡️ 震荡整理，耐心观望")
            print("📈 等待方向选择信号")
            print("⏳ 保持谨慎，控制仓位")

        # 投资建议
        print(f"\n📋 投资建议")
        print("-" * 40)
        print(f"投资周期: 中长线投资价值较好")
        print(f"仓位建议: 不超过总资金的15%")
        print(f"止盈位: 可关注{data['high_price'] * 1.1:.2f}元")
        print(f"止损位: 关注{data['low_price'] * 0.95:.2f}元")

        # 风险提示
        print(f"\n⚠️ 风险提示")
        print("-" * 40)
        print("• 股市有风险，投资需谨慎")
        print("• 本分析仅供参考，不构成投资建议")
        print("• 关注公司业绩变化和行业政策")
        print("• 注意控制仓位，分散投资风险")
        print("• 大盘波动可能影响个股表现")

        return data, indicators, signals

def main():
    """主函数"""
    analyzer = EastGuoxinAnalyzer()
    result = analyzer.generate_comprehensive_report()

    if result:
        data, indicators, signals = result
        print(f"\n✅ 分析完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"\n❌ 分析失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()