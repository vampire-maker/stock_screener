#!/usr/bin/env python3
"""
股票筛选系统统一配置管理模块
管理所有API密钥、策略参数和系统配置
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载.env文件（本地开发）
load_dotenv()

# Streamlit Cloud兼容：尝试导入streamlit
try:
    import streamlit as st
    STREAMLIT_CLOUD = hasattr(st, 'secrets')
except ImportError:
    STREAMLIT_CLOUD = False

def get_env_var(key: str, default: str = '') -> str:
    """获取环境变量（兼容本地和Streamlit Cloud）"""
    # 首先尝试从环境变量读取（本地开发优先）
    env_value = os.getenv(key, default)
    if env_value:
        return env_value

    # 如果环境变量为空，再尝试Streamlit secrets
    if STREAMLIT_CLOUD:
        try:
            return st.secrets[key]
        except (KeyError, FileNotFoundError):
            pass

    return default

class StockScreenerConfig:
    """股票筛选系统配置管理类"""

    def __init__(self):
        # API配置
        self.GUGU_APPKEY = get_env_var('GUGU_APPKEY', 'SQSM4ASGQT6UN363PWA9M6256764WYBS')
        self.TUSHARE_TOKEN = get_env_var('TUSHARE_TOKEN', 'fb8b11e0099681fc2e706351fa6ff0bb593053d1c9681800a72a0fcd')

        # API端点
        self.GUGU_API_BASE = "https://api.gugudata.com/stock/cn/realtime"
        self.REQUEST_TIMEOUT = 10  # 秒
        self.API_DELAY = 0.2  # API调用间隔（秒）

        # 通用筛选参数
        self.common_params = {
            'min_price': 3.0,
            'max_price': 200.0,
            'exclude_st': True,
            'min_market_cap': 3000000000,  # 30亿
            'max_market_cap': 200000000000,  # 200亿
        }

        # 11:30策略参数 - 重新调整更合理
        self.enhanced_1130_params = {
            'min_turnover_rate': 0.8,       # 换手率≥0.8% (降低)
            'max_turnover_rate': 8.0,       # 换手率≤8% (避免过度投机)
            'min_volume_ratio': 1.1,       # 量比≥1.1倍 (适度降低)
            'min_change_percent': -3.0,    # 涨幅-3%到8% (进一步扩大)
            'max_change_percent': 8.0,
            'min_main_inflow': 20000000,   # 主力资金≥2000万元 (进一步降低)
            'min_main_inflow_ratio': 0.12, # 主力资金占比≥12% (进一步降低)
            'min_roe': 3.0,                # ROE≥3% (进一步降低)
            'max_pe': 120.0,               # PE≤120倍 (进一步放宽)
            'max_pb': 20.0,                # PB≤20倍 (进一步放宽)
            'max_debt_ratio': 90.0,        # 负债率≤90% (进一步放宽)
            **self.common_params
        }

        # 14:30策略参数 - 与11:30保持一致
        self.enhanced_1430_params = {
            'min_turnover_rate': 5.0,       # 换手率≥5% (提高)
            'max_turnover_rate': 10.0,      # 换手率≤10% (适中)
            'min_volume_ratio': 1.2,       # 量比≥1.2倍 (降低)
            'min_change_percent': -2.0,    # 涨幅-2%到7% (略微扩大)
            'max_change_percent': 7.0,
            'min_main_inflow': 30000000,   # 主力资金≥3000万元 (降低)
            'min_main_inflow_ratio': 0.15, # 主力资金占比≥15% (降低)
            'min_roe': 4.0,                # ROE≥4% (降低)
            'max_pe': 100.0,               # PE≤100倍 (放宽)
            'max_pb': 15.0,                # PB≤15倍 (放宽)
            'max_debt_ratio': 85.0,        # 负债率≤85% (放宽)
            **self.common_params
        }

        # 14:50主力埋伏策略参数 - 优化版本v4.1 (基于历史数据优化)
        self.main_force_burial_params = {
            'MIN_MV': 200000,  # 最小流通市值 (20亿 - 适度放宽)
            'MAX_MV': 20000000,  # 最大流通市值 (200亿)
            'MIN_PCT': 0.5,  # 最小涨幅 (0.5% - 放宽)
            'MAX_PCT': 8.0,  # 最大涨幅 (8.0% - 放宽)
            'MAX_DEVIATION': 5.0,  # 最大均价乖离率 (5.0%)
            'INDEX_RISK_THR': -0.6,  # 大盘风控阈值 (-0.6%)
            'MIN_AMOUNT': 10000000,  # 最小成交额 (1亿 - 大幅降低)
            # 换手率区间分层设置 (适度放宽)
            'TURNOVER_RATE_SMALL_CAP_MIN': 3.0,   # 小盘股换手率下限 (30-100亿，3.0% - 放宽)
            'TURNOVER_RATE_SMALL_CAP_MAX': 12.0,  # 小盘股换手率上限 (30-100亿，12.0% - 放宽)
            'TURNOVER_RATE_MID_CAP_MIN': 2.0,     # 中盘股换手率下限 (100-300亿，2.0% - 放宽)
            'TURNOVER_RATE_MID_CAP_MAX': 10.0,     # 中盘股换手率上限 (100-300亿，10.0% - 放宽)
            'TURNOVER_RATE_LARGE_CAP_MIN': 1.5,   # 大盘股换手率下限 (300-500亿，1.5% - 放宽)
            'TURNOVER_RATE_LARGE_CAP_MAX': 8.0,   # 大盘股换手率上限 (300-500亿，8.0% - 放宽)
            **self.common_params
        }

        # 邮件配置
        self.email_config = {
            'enabled': get_env_var('EMAIL_ENABLED', 'true').lower() == 'true',
            'smtp_server': get_env_var('SMTP_SERVER', 'smtp.163.com'),
            'smtp_port': int(get_env_var('SMTP_PORT', '465')),
            'sender_email': get_env_var('SENDER_EMAIL', ''),
            'sender_password': get_env_var('SENDER_PASSWORD', ''),
            'recipients': get_env_var('RECIPIENTS', '').split(',') if get_env_var('RECIPIENTS', '') else [],
            'use_tls': get_env_var('SMTP_PORT', '587') == '587'  # 587端口使用STARTTLS
        }

        # 智能股票池配置
        self.smart_universe_config = {
            'cache_file': "smart_stock_universe.json",
            'min_turnover_rate': 1.0,  # 最小换手率
            'min_amount': 50000000,    # 最小成交额
            'update_interval_hours': 24,  # 更新间隔
        }

        # 快刀手晚进早出策略参数 v2.0 (基于326只股票回测优化)
        self.quick_knife_params = {
            'MIN_MV': 0,  # 无最小市值限制
            'MAX_MV': 20000000000,  # 最大200亿
            'MIN_PCT': 2.8,  # 最小涨幅2.8% (收窄下限，避开弱势)
            'MAX_PCT': 4.5,  # 最大涨幅4.5% (收窄上限，避免追高)
            'MAX_DEVIATION': 0,  # 价格在日均线上
            'INDEX_RISK_THR': -1.0,  # 指数风险阈值
            'MIN_AMOUNT': 50000000,  # 最小成交额5000万
            'MIN_VOLUME_RATIO': 1.0,  # 量比最小值
            'MAX_VOLUME_RATIO': 1.6,  # 量比最大值 (收窄，避开诱多)
            'PRICE_ABOVE_MA': True,  # 全天价格在日均线上
            'HAS_LIMIT_UP_20D': True,  # 近20日有过涨停 (胜率+8.6%)
            'BOARDS': ['主板', '创业板'],  # 只看主板和创业板
            # 换手率参数 (U型分布：两头优、中间差)
            'TURNOVER_MODE': 'U_SHAPE',
            'TURNOVER_LOW_MAX': 2.5,  # 低换手率区间上限 (主力控盘)
            'TURNOVER_HIGH_MIN': 18.0,  # 高换手率区间下限 (资金活跃)
            'TURNOVER_AVOID_MIN': 5.0,  # 避开区间下限
            'TURNOVER_AVOID_MAX': 10.0,  # 避开区间上限 (最差区间)
            **self.common_params
        }

    def get_strategy_params(self, strategy_name: str) -> Dict[str, Any]:
        """获取指定策略的参数"""
        strategy_map = {
            'enhanced_1130': self.enhanced_1130_params,
            'enhanced_1430': self.enhanced_1430_params,
            'main_force_burial': self.main_force_burial_params,
            'quick_knife': self.quick_knife_params,
        }
        return strategy_map.get(strategy_name, {})

    def get_api_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        }

    def validate_config(self) -> Dict[str, bool]:
        """验证配置完整性"""
        validation = {
            'gugu_api_key': bool(self.GUGU_APPKEY),
            'tushare_token': bool(self.TUSHARE_TOKEN),
            'email_config': all([
                self.email_config['sender_email'],
                self.email_config['sender_password'],
                self.email_config['recipients']
            ])
        }
        return validation

# 全局配置实例
config = StockScreenerConfig()

# 便捷函数
def get_config() -> StockScreenerConfig:
    """获取配置实例"""
    return config

def get_strategy_config(strategy_name: str) -> Dict[str, Any]:
    """获取策略配置的便捷函数"""
    return config.get_strategy_params(strategy_name)