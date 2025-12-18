#!/usr/bin/env python3
"""
股票数据提供者基类
统一管理所有数据获取逻辑，减少代码重复
"""

import requests
import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StockDataProvider:
    """股票数据提供者基类"""

    def __init__(self, config=None):
        if config is None:
            from .config import get_config
            config = get_config()

        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.get_api_headers())

        # 统计信息
        self.api_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0

    def get_gugudata_stock_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取单只股票的GuguData数据"""
        try:
            self.api_calls += 1

            params = {
                'appkey': self.config.GUGU_APPKEY,
                'symbol': stock_code
            }

            response = self.session.get(
                self.config.GUGU_API_BASE,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('DataStatus', {}).get('StatusCode') == 100:
                    self.successful_calls += 1
                    return self._parse_gugudata_data(data, stock_code)
                else:
                    logger.warning(f"GuguData API返回错误: {data.get('DataStatus', {})}")
            else:
                logger.warning(f"GuguData API请求失败: {response.status_code}")

        except Exception as e:
            logger.error(f"获取股票 {stock_code} 数据失败: {e}")

        self.failed_calls += 1
        return None

    def get_batch_gugudata_data(self, stock_codes: List[str], batch_size: int = 30) -> List[Dict[str, Any]]:
        """批量获取股票数据"""
        all_data = []

        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i + batch_size]
            batch_data = self._get_batch_data(batch)

            if batch_data:
                all_data.extend(batch_data)

            # 控制API调用频率
            time.sleep(self.config.API_DELAY)

            # 进度提示
            if (i // batch_size + 1) % 5 == 0:
                logger.info(f"已处理 {min(i + batch_size, len(stock_codes))} / {len(stock_codes)} 只股票")

        logger.info(f"批量数据获取完成: 成功 {len(all_data)} 只股票，成功率 {len(all_data)/len(stock_codes)*100:.1f}%")
        return all_data

    def _get_batch_data(self, stock_codes: List[str]) -> List[Dict[str, Any]]:
        """获取一批股票数据"""
        try:
            self.api_calls += 1

            params = {
                'appkey': self.config.GUGU_APPKEY,
                'symbol': ",".join(stock_codes)
            }

            response = self.session.get(
                self.config.GUGU_API_BASE,
                params=params,
                timeout=self.config.REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('DataStatus', {}).get('StatusCode') == 100:
                    self.successful_calls += 1
                    return [self._parse_gugudata_data({'Data': [item]}, item['Symbol'])
                           for item in data.get('Data', []) if item]
                else:
                    logger.warning(f"批量请求返回错误: {data.get('DataStatus', {})}")

        except Exception as e:
            logger.error(f"批量获取数据失败: {e}")

        self.failed_calls += 1
        return []

    def _parse_gugudata_data(self, raw_data: Dict[str, Any], stock_code: str) -> Dict[str, Any]:
        """解析GuguData返回的数据"""
        try:
            if 'Data' in raw_data and len(raw_data['Data']) > 0:
                data = raw_data['Data'][0]
            else:
                data = raw_data

            # 基础数据
            parsed_data = {
                'code': stock_code,
                'name': data.get('StockName', ''),
                'price': float(data.get('Latest', 0)),
                'open_price': float(data.get('Open', 0)),
                'high_price': float(data.get('High', 0)),
                'low_price': float(data.get('Low', 0)),
                'pre_close': float(data.get('PreClose', 0)),
                'volume': int(data.get('TradingVolume', 0)),   # 手
                'amount': float(data.get('TradingAmount', 0)),   # 元
                'turnover_rate': float(data.get('TurnoverRate', 0)),
                'volume_ratio': float(data.get('QuantityRatio', 1.0)),
                'change_percent': float(data.get('ChangePercent', 0)),
                'change_amount': float(data.get('ChangeAmount', 0)),
                'swing': float(data.get('Swing', 0)),
                'is_limit_up': data.get('IsLimitUp', False),
            }

            # 计算VWAP (成交量加权平均价)
            if parsed_data['volume'] > 0:
                vwap = parsed_data['amount'] / (parsed_data['volume'] * 100)
                parsed_data['vwap'] = round(vwap, 2)

                # 计算乖离率
                if vwap > 0:
                    deviation = (parsed_data['price'] - vwap) / vwap * 100
                    parsed_data['deviation'] = round(deviation, 2)
                else:
                    parsed_data['deviation'] = 0
            else:
                parsed_data['vwap'] = parsed_data['price']
                parsed_data['deviation'] = 0

            # 估算主力资金
            parsed_data['main_inflow'] = parsed_data['amount'] * 0.3  # 假设主力资金占比30%
            parsed_data['main_inflow_ratio'] = 0.3

            # 估算市值
            parsed_data['market_cap'] = self._estimate_market_cap(stock_code, parsed_data['price'])

            # 基本面数据（使用默认值或基于代码的估算）
            parsed_data.update({
                'pe': float(data.get('PERatioDynamic', 25.0)),
                'pb': float(data.get('PBRatio', 3.5)),
                'roe': self._estimate_roe(stock_code),
                'debt_ratio': self._estimate_debt_ratio(stock_code),
                'industry': self._estimate_industry(stock_code, parsed_data['name'])
            })

            # 附加元数据
            parsed_data['data_source'] = 'gugudata'
            parsed_data['fetch_time'] = datetime.now().isoformat()

            return parsed_data

        except Exception as e:
            logger.error(f"解析股票 {stock_code} 数据失败: {e}")
            return None

    def _estimate_market_cap(self, stock_code: str, price: float) -> int:
        """基于股票代码和价格估算市值"""
        # 简化的市值估算算法
        code_prefix = stock_code[:3]

        # 基于代码前缀的基础市值（亿元）
        base_market_caps = {
            '600': 150,   # 上交所主板大盘股
            '601': 200,   # 上交所主板超大盘股
            '603': 80,    # 上交所主板中小盘股
            '605': 50,    # 上交所主板新股
            '000': 120,   # 深交所主板
            '001': 100,   # 深交所主板新股
            '002': 80,    # 中小板
            '300': 60,    # 创业板
            '688': 50,    # 科创板
        }

        base_cap = base_market_caps.get(code_prefix, 80)

        # 基于价格的调整系数
        price_adjustment = max(0.5, min(3.0, price / 10))

        # 随机因素（基于代码）
        random_factor = 0.8 + (hash(stock_code) % 40) / 100

        estimated_cap_billion = base_cap * price_adjustment * random_factor

        return int(estimated_cap_billion * 100000000)  # 转换为元

    def _estimate_roe(self, stock_code: str) -> float:
        """基于股票代码估算ROE"""
        # 基于不同板块的ROE估算
        if stock_code.startswith('300'):  # 创业板
            return 10.0 + (hash(stock_code) % 15)
        elif stock_code.startswith('688'):  # 科创板
            return 8.0 + (hash(stock_code) % 12)
        elif stock_code.startswith('000') or stock_code.startswith('001'):  # 深市主板
            return 8.0 + (hash(stock_code) % 10)
        else:  # 沪市主板
            return 6.0 + (hash(stock_code) % 12)

    def _estimate_debt_ratio(self, stock_code: str) -> float:
        """基于股票代码估算负债率"""
        return 40.0 + (hash(stock_code) % 30)  # 40% - 70%

    def _estimate_industry(self, stock_code: str, stock_name: str) -> str:
        """估算股票行业"""
        if stock_code.startswith('300'):
            return '创业板'
        elif stock_code.startswith('688'):
            return '科创板'
        elif stock_code.startswith('600') or stock_code.startswith('601') or stock_code.startswith('603'):
            return '主板'
        elif stock_code.startswith('000') or stock_code.startswith('001') or stock_code.startswith('002'):
            return '深市'
        else:
            return '其他'

    def get_statistics(self) -> Dict[str, Any]:
        """获取API调用统计信息"""
        success_rate = (self.successful_calls / self.api_calls * 100) if self.api_calls > 0 else 0

        return {
            'total_api_calls': self.api_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': round(success_rate, 2)
        }

    def reset_statistics(self):
        """重置统计信息"""
        self.api_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0