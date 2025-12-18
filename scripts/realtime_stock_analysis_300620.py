#!/usr/bin/env python3
"""
使用GuguData API获取300620光库科技实时数据
基于真实数据进行走势分析
"""

import sys
import os
import requests
import json
from datetime import datetime
import pandas as pd

class RealtimeStockAnalyzer:
    """实时股票数据分析器"""

    def __init__(self):
        self.api_key = "SQSM4ASGQT6UN363PWA9M6256764WYBS"
        # 尝试多个基础URL
        self.base_urls = [
            "https://api.gugudata.com",
            "https://www.gugudata.com/api",
            "https://gugudata.com/api"
        ]
        self.stock_code = "300620"
        self.stock_name = "光库科技"

    def get_realtime_quote(self):
        """获取实时行情数据"""
        print(f"🔍 获取{self.stock_name}({self.stock_code})实时数据...")
        print("-" * 50)

        try:
            # 尝试多个可能的API端点
            api_endpoints = []
            for base_url in self.base_urls:
                api_endpoints.append(f"{base_url}/stockcnrealtime")
                api_endpoints.append(f"{base_url}/api/stockcnrealtime")

            # 去重
            api_endpoints = list(set(api_endpoints))

            for url in api_endpoints:
                try:
                    print(f"尝试API端点: {url}")
                    params = {
                        'symbol': self.stock_code,
                        'apikey': self.api_key,  # 尝试不同的参数名
                        'fields': 'all'  # 获取所有字段
                    }

                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Content-Type': 'application/json'
                    }

                    response = requests.get(url, params=params, headers=headers, timeout=10)

                    print(f"响应状态码: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print("✅ 成功获取实时数据")
                        return data
                    else:
                        print(f"当前端点失败: {response.status_code}")
                        if response.status_code != 404:
                            print(f"响应内容: {response.text[:200]}")

                except requests.exceptions.RequestException as e:
                    print(f"端点 {url} 请求异常: {e}")
                    continue

            print("❌ 所有API端点都尝试失败")
            return None

        except Exception as e:
            print(f"❌ 获取数据异常: {e}")
            return None

    def get_technical_indicators(self):
        """获取技术指标数据"""
        print(f"\n📈 获取技术指标数据...")
        print("-" * 50)

        try:
            # 使用第一个base_url获取技术指标
            base_url = self.base_urls[0] if self.base_urls else "https://api.gugudata.com"
            url = f"{base_url}/stock/technical"
            params = {
                'symbol': self.stock_code,
                'api_key': self.api_key,
                'indicators': 'ma,macd,rsi,kdj,boll'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print("✅ 成功获取技术指标")
                return data
            else:
                print(f"⚠️ 技术指标获取失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️ 技术指标获取异常: {e}")
            return None

    def get_kline_data(self, period='1d', count=30):
        """获取K线数据"""
        print(f"\n📊 获取K线数据 ({period}周期)...")
        print("-" * 50)

        try:
            # 使用第一个base_url获取K线数据
            base_url = self.base_urls[0] if self.base_urls else "https://api.gugudata.com"
            url = f"{base_url}/stock/kline"
            params = {
                'symbol': self.stock_code,
                'period': period,
                'count': count,
                'api_key': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取{count}条K线数据")
                return data
            else:
                print(f"⚠️ K线数据获取失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"⚠️ K线数据获取异常: {e}")
            return None

    def parse_realtime_data(self, quote_data):
        """解析实时行情数据"""
        if not quote_data:
            return None

        try:
            # 根据GuguData API响应格式解析数据
            # 这里需要根据实际API响应格式进行调整
            parsed_data = {
                'current_price': quote_data.get('price', 0),
                'change': quote_data.get('change', 0),
                'change_percent': quote_data.get('change_percent', 0),
                'volume': quote_data.get('volume', 0),
                'amount': quote_data.get('amount', 0),
                'turnover_rate': quote_data.get('turnover_rate', 0),
                'open_price': quote_data.get('open', 0),
                'high_price': quote_data.get('high', 0),
                'low_price': quote_data.get('low', 0),
                'pre_close': quote_data.get('pre_close', 0),
                'pe': quote_data.get('pe', 0),
                'pb': quote_data.get('pb', 0),
                'market_cap': quote_data.get('market_cap', 0)
            }

            return parsed_data

        except Exception as e:
            print(f"❌ 数据解析失败: {e}")
            return None

    def display_realtime_analysis(self, quote_data, technical_data, kline_data):
        """显示实时分析结果"""
        print(f"\n🚀 {self.stock_name}({self.stock_code}) 实时分析报告")
        print("=" * 60)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if quote_data:
            self.display_quote_info(quote_data)

        if technical_data:
            self.display_technical_analysis(technical_data)

        if kline_data:
            self.display_kline_analysis(kline_data)

        self.generate_trading_recommendations(quote_data, technical_data, kline_data)

    def display_quote_info(self, data):
        """显示行情信息"""
        print("📊 实时行情")
        print("-" * 40)

        price = data.get('current_price', 0)
        change = data.get('change', 0)
        change_percent = data.get('change_percent', 0)

        change_symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"

        print(f"{change_symbol} 当前价格: {price:.2f}元")
        print(f"🔄 涨跌: {change:+.2f} ({change_percent:+.2f}%)")

        if data.get('high_price') and data.get('low_price'):
            print(f"🔺 今高: {data['high_price']:.2f}元")
            print(f"🔻 今低: {data['low_price']:.2f}元")
            print(f"🟢 开盘: {data.get('open_price', 0):.2f}元")
            print(f"🔴 昨收: {data.get('pre_close', 0):.2f}元")

        if data.get('volume'):
            volume = data['volume']
            amount = data.get('amount', 0)
            turnover = data.get('turnover_rate', 0)

            print(f"📊 成交量: {volume:,}")
            print(f"💰 成交额: {amount:,.0f}元")
            print(f"🔄 换手率: {turnover:.2f}%")

        if data.get('pe') and data.get('pe') > 0:
            print(f"📈 市盈率: {data['pe']:.2f}")
        if data.get('pb') and data.get('pb') > 0:
            print(f"📊 市净率: {data['pb']:.2f}")

    def display_technical_analysis(self, data):
        """显示技术分析"""
        print(f"\n📈 技术指标分析")
        print("-" * 40)

        # 这里需要根据实际API返回的技术指标格式进行解析
        # 由于无法确定具体的API响应格式，先显示框架

        indicators = data.get('indicators', {})

        if 'ma' in indicators:
            ma_data = indicators['ma']
            print(f"📊 移动平均线:")
            for period, value in ma_data.items():
                print(f"  MA{period}: {value:.2f}")

        if 'macd' in indicators:
            macd_data = indicators['macd']
            print(f"\n📊 MACD:")
            print(f"  DIF: {macd_data.get('dif', 0):.4f}")
            print(f"  DEA: {macd_data.get('dea', 0):.4f}")
            print(f"  MACD: {macd_data.get('macd', 0):.4f}")

        if 'rsi' in indicators:
            rsi_data = indicators['rsi']
            rsi_value = rsi_data.get('value', 0)
            rsi_status = "超买" if rsi_value > 70 else "超卖" if rsi_value < 30 else "正常"
            print(f"\n📊 RSI: {rsi_value:.2f} ({rsi_status})")

    def display_kline_analysis(self, data):
        """显示K线分析"""
        print(f"\n📊 K线分析")
        print("-" * 40)

        klines = data.get('klines', [])
        if not klines:
            print("暂无K线数据")
            return

        print(f"📈 最近{len(klines)}个交易日走势:")

        # 显示最近5根K线
        recent_klines = klines[-5:]
        for kline in recent_klines:
            date = kline.get('date', '')
            open_price = kline.get('open', 0)
            high_price = kline.get('high', 0)
            low_price = kline.get('low', 0)
            close_price = kline.get('close', 0)
            change = close_price - open_price
            change_percent = (change / open_price) * 100 if open_price > 0 else 0

            symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            print(f"  {date} {symbol} {close_price:.2f} ({change:+.2f}, {change_percent:+.2f}%)")

    def get_fallback_data(self):
        """获取备用数据源"""
        print(f"\n🔄 使用备用数据源...")
        print("-" * 50)

        # 使用新浪财经作为备用数据源
        try:
            # 新浪财经API
            sina_url = f"https://hq.sinajs.cn/list={self.stock_code}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.sina.com.cn/'
            }

            response = requests.get(sina_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 解析新浪财经数据格式
                content = response.text
                if f"var hq_str_{self.stock_code}" in content:
                    start = content.find('"') + 1
                    end = content.rfind('"')
                    data_str = content[start:end]
                    data_parts = data_str.split(',')

                    if len(data_parts) >= 32:
                        fallback_data = {
                            'current_price': float(data_parts[3]) if data_parts[3] else 0,
                            'open_price': float(data_parts[1]) if data_parts[1] else 0,
                            'pre_close': float(data_parts[2]) if data_parts[2] else 0,
                            'high_price': float(data_parts[4]) if data_parts[4] else 0,
                            'low_price': float(data_parts[5]) if data_parts[5] else 0,
                            'volume': int(float(data_parts[8])) if data_parts[8] else 0,
                            'amount': float(data_parts[9]) if data_parts[9] else 0,
                            'change': 0,
                            'change_percent': 0,
                            'data_source': 'sina',
                            'update_time': data_parts[30] + ' ' + data_parts[31] if len(data_parts) > 31 else ''
                        }

                        # 计算涨跌幅
                        if fallback_data['pre_close'] > 0:
                            fallback_data['change'] = fallback_data['current_price'] - fallback_data['pre_close']
                            fallback_data['change_percent'] = (fallback_data['change'] / fallback_data['pre_close']) * 100

                        print("✅ 成功从新浪财经获取数据")
                        return fallback_data

        except Exception as e:
            print(f"⚠️ 备用数据源也失败: {e}")

        return None

    def generate_trading_recommendations(self, quote_data, technical_data, kline_data):
        """生成交易建议"""
        print(f"\n💡 操作建议")
        print("-" * 40)

        if not quote_data:
            print("⚠️ 无法生成建议，数据获取失败")
            print("💡 建议通过以下方式获取实时数据：")
            print("   1. 查看股票交易软件")
            print("   2. 访问新浪财经、东方财富等网站")
            print("   3. 使用专业的股票行情软件")
            return

        price = quote_data.get('current_price', 0)
        change_percent = quote_data.get('change_percent', 0)
        data_source = quote_data.get('data_source', 'unknown')

        print(f"📊 数据来源: {data_source}")
        print(f"💰 当前价格: {price:.2f}元")
        print(f"📈 涨跌幅: {change_percent:+.2f}%")

        # 基于当前走势生成建议
        if change_percent > 5:
            recommendation = "⚠️ 涨幅过大，风险较高"
            action = "不建议追高，观望为主"
        elif change_percent > 2:
            recommendation = "📈 涨幅较大，谨慎操作"
            action = "可考虑逢高减仓"
        elif change_percent > 0:
            recommendation = "🟢 小幅上涨，趋势向好"
            action = "关注回调机会，适量买入"
        elif change_percent > -2:
            recommendation = "➡️ 平盘震荡，等待方向"
            action = "暂时观望，等待明确信号"
        else:
            recommendation = "📉 出现下跌，关注支撑"
            action = "支撑位附近可考虑买入"

        print(f"\n🎯 策略建议: {recommendation}")
        print(f"💰 操作策略: {action}")

        # 基于技术分析的一般建议
        print(f"\n📊 技术分析建议:")
        print(f"  • 关注成交量变化")
        print(f"  • 注意支撑位和压力位")
        print(f"  • 结合大盘走势判断")
        print(f"  • 控制好仓位比例")

        # 风险提示
        print(f"\n⚠️ 风险提示:")
        print(f"  • 股市有风险，投资需谨慎")
        print(f"  • 建议设置止盈止损")
        print(f"  • 控制仓位，分散投资")
        print(f"  • 本分析仅供参考，不构成投资建议")
        print(f"  • 投资决策需基于全面分析和个人判断")

    def run_realtime_analysis(self):
        """运行实时分析"""
        print("🚀 启动实时股票分析")
        print("=" * 60)
        print(f"目标股票: {self.stock_name}({self.stock_code})")
        print(f"主要数据源: GuguData API")
        print(f"备用数据源: 新浪财经")
        print(f"API密钥: {self.api_key[:10]}...")
        print()

        # 首先尝试获取GuguData数据
        print("🔍 尝试获取GuguData数据...")
        quote_data = self.get_realtime_quote()
        technical_data = self.get_technical_indicators()
        kline_data = self.get_kline_data()

        # 如果GuguData失败，使用备用数据源
        if not quote_data:
            print("\n" + "="*60)
            print("⚠️ GuguData API访问失败，切换到备用数据源")
            quote_data = self.get_fallback_data()

        # 显示分析结果
        self.display_realtime_analysis(quote_data, technical_data, kline_data)

        return quote_data, technical_data, kline_data

def main():
    """主函数"""
    analyzer = RealtimeStockAnalyzer()
    analyzer.run_realtime_analysis()

if __name__ == "__main__":
    main()