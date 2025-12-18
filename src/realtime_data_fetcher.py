#!/usr/bin/env python3
"""
实时交易数据获取器
优先使用GuguData API，其次使用Tushare Pro API
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
import logging
import pandas as pd

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import get_config

class RealtimeDataFetcher:
    """实时数据获取器 - GuguData优先，Tushare备用"""

    def __init__(self):
        self.config = get_config()
        self.gugu_appkey = self.config.GUGU_APPKEY
        self.tushare_token = self.config.TUSHARE_TOKEN

        # 初始化Tushare Pro
        try:
            import tushare as ts
            self.pro = ts.pro_api(self.tushare_token)
        except Exception as e:
            self.pro = None

        self.logger = logging.getLogger(__name__)

    def get_gugu_data(self, symbol):
        """使用GuguData API获取实时数据"""
        try:
            url = "https://api.gugudata.com/stock/cn/realtime"
            params = {
                'appkey': self.gugu_appkey,
                'symbol': symbol
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('Data') and len(data['Data']) > 0:
                    return data['Data'][0]
        except Exception as e:
            self.logger.warning(f"GuguData API获取{symbol}失败: {e}")

        return None

    def get_tushare_data(self, ts_code):
        """使用Tushare Pro API获取最新数据（作为备用）"""
        try:
            if not self.pro:
                return None

            # 获取最新交易日数据
            today = datetime.now().strftime('%Y%m%d')
            df = self.pro.daily(ts_code=ts_code, trade_date=today)

            if df.empty:
                # 尝试获取最近一个交易日
                df = self.pro.daily(ts_code=ts_code, limit=1)

            if not df.empty:
                row = df.iloc[0]
                # 转换为类似GuguData的格式
                return {
                    'Symbol': ts_code.split('.')[0],
                    'StockName': '',  # Tushare日线不包含名称
                    'Latest': row['close'],
                    'Open': row['open'],
                    'High': row['high'],
                    'Low': row['low'],
                    'LastClose': row['pre_close'],
                    'TradingVolume': row['vol'],
                    'TradingAmount': row['amount'],
                    'TurnoverRate': 0,  # Tushare日线不包含换手率
                    'ChangePercent': row['pct_chg']
                }
        except Exception as e:
            self.logger.warning(f"Tushare API获取{ts_code}失败: {e}")

        return None

    def get_stock_realtime_data(self, stock_code):
        """获取单只股票的实时数据 - 优先GuguData，备用Tushare"""

        # 构造不同格式的代码
        ts_code = None
        gugu_symbol = stock_code  # GuguData使用纯数字代码

        # 转换为Tushare格式
        if stock_code.startswith('60') or stock_code.startswith('68'):
            ts_code = f"{stock_code}.SH"
        elif stock_code.startswith('00') or stock_code.startswith('30'):
            ts_code = f"{stock_code}.SZ"
        else:
            # 默认处理
            if '.' not in stock_code:
                ts_code = f"{stock_code}.SZ" if stock_code.startswith(('000', '001', '002', '300')) else f"{stock_code}.SH"
            else:
                ts_code = stock_code
                gugu_symbol = stock_code.split('.')[0]

        # 优先使用GuguData
        data = self.get_gugu_data(gugu_symbol)
        data_source = 'gugudata'

        # 如果GuguData失败，使用Tushare Pro
        if not data and ts_code:
            data = self.get_tushare_data(ts_code)
            data_source = 'tushare'

        if not data:
            self.logger.error(f"无法获取股票{stock_code}的数据")
            return None

        # 解析数据
        parsed_data = self.parse_stock_data(data, stock_code, data_source)

        # 如果数据不完整，记录日志
        if parsed_data and (not parsed_data.get('name') or parsed_data.get('turnover_rate') == 0):
            self.logger.warning(f"股票{stock_code}数据不完整，源：{data_source}")

        return parsed_data

    def parse_stock_data(self, raw_data, stock_code, data_source):
        """解析股票数据"""
        try:
            # 基础价格数据
            current = raw_data.get('Latest', 0)
            open_px = raw_data.get('Open', 0)
            high = raw_data.get('High', 0)
            low = raw_data.get('Low', 0)
            pre_close = raw_data.get('LastClose', 0)

            # 成交量和金额数据
            vol = raw_data.get('TradingVolume', 0)  # 手
            amt = raw_data.get('TradingAmount', 0)  # 元
            turnover_rate = raw_data.get('TurnoverRate', 0)

            # 涨跌幅
            change_pct = raw_data.get('ChangePercent', 0)
            if change_pct == 0 and pre_close > 0:
                pct_chg = (current - pre_close) / pre_close * 100
            else:
                pct_chg = change_pct

            # 基础数据校验
            if current == 0 or vol == 0 or pre_close == 0:
                return None

            parsed_data = {
                'code': stock_code,
                'name': raw_data.get('StockName', ''),
                'price': current,
                'open_price': open_px,
                'high_price': high,
                'low_price': low,
                'pre_close': pre_close,
                'volume': vol,
                'amount': amt,
                'turnover_rate': turnover_rate,
                'change_percent': pct_chg,
                'data_source': data_source,

                # 估算数据
                'volume_ratio': max(1.0, vol / 50000),  # 简化量比
                'main_inflow': amt * 0.3 if amt > 0 else 0,  # 估算主力资金
                'main_inflow_ratio': 0.45,

                # 基本面数据（模拟）
                'pe': 25.0,
                'pb': 3.5,
                'roe': 12.0,
                'debt_ratio': 45.0,
                'market_cap': max(5000000000, current * vol * 100),  # 估算市值

                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 估算换手率（如果没有直接提供）
            if turnover_rate == 0 and parsed_data['market_cap'] > 0:
                parsed_data['turnover_rate'] = (vol * 100 / parsed_data['market_cap']) * 100

            # 估算行业信息
            parsed_data['industry'] = self.estimate_industry(stock_code, parsed_data['name'])

            return parsed_data

        except Exception as e:
            self.logger.error(f"解析股票数据失败: {e}")
            return None

    def estimate_industry(self, stock_code, stock_name):
        """估算股票行业"""
        if any(keyword in stock_name for keyword in ['科技', '软件', '信息', '网络', '数据', '智能', '电子']):
            return '科技信息'
        elif any(keyword in stock_name for keyword in ['医药', '生物', '健康', '医疗']):
            return '医药生物'
        elif any(keyword in stock_name for keyword in ['制造', '机械', '设备', '材料']):
            return '制造材料'
        elif any(keyword in stock_name for keyword in ['能源', '电力', '化工']):
            return '能源化工'
        elif any(keyword in stock_name for keyword in ['银行', '保险', '证券', '金融']):
            return '金融服务'
        else:
            return '其他'

    def get_market_stocks_snapshot(self, stock_codes=None):
        """获取市场股票快照"""
        if stock_codes is None:
            # 默认监控的股票列表
            stock_codes = [
                '300830', '301311', '603600', '300221', '002475',
                '300166', '300620', '000001', '000002', '600036',
                '300015', '002415', '300750', '002594', '600276'
            ]

        stocks_data = []
        gugu_success = 0
        tushare_success = 0
        failed = 0

        for stock_code in stock_codes:
            data = self.get_stock_realtime_data(stock_code)
            if data:
                stocks_data.append(data)
                if data.get('data_source') == 'gugudata':
                    gugu_success += 1
                else:
                    tushare_success += 1
            else:
                failed += 1

            time.sleep(0.1)  # 避免请求过快

        self.logger.info(f"数据获取统计 - GuguData: {gugu_success}, Tushare: {tushare_success}, 失败: {failed}")

        if failed > 0:
            self.logger.warning(f"有{failed}只股票数据获取失败，请检查API配置")

        return stocks_data

    def check_api_status(self):
        """检查API状态"""
        status = {
            'gugudata': False,
            'tushare': False,
            'message': ''
        }

        # 测试GuguData
        test_data = self.get_gugu_data('000001')
        if test_data:
            status['gugudata'] = True
            status['message'] += "GuguData API正常；"
        else:
            status['message'] += "GuguData API异常；"

        # 测试Tushare
        if self.pro:
            try:
                test_df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
                if not test_df.empty:
                    status['tushare'] = True
                    status['message'] += "Tushare Pro API正常；"
                else:
                    status['message'] += "Tushare Pro API无数据；"
            except Exception as e:
                status['message'] += f"Tushare Pro API异常：{str(e)}；"
        else:
            status['message'] += "Tushare Pro未初始化；"

        return status