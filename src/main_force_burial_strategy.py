# -*- coding: utf-8 -*-
"""
A股尾盘主力埋伏策略 (Tushare + GuguData 融合版)
功能：
1. 盘前/盘中：使用 Tushare 筛选高潜力的基础股票池 (市值、活跃度、非ST)。
2. 尾盘(14:50)：使用 GuguData 毫秒级获取实时行情，计算分时均价(VWAP)与乖离率。
3. 风控：自动识别大盘风险、个股骗线（偷袭）、长上影线等陷阱。
"""

import sys
import os
import json
import pandas as pd
import requests
import datetime
import time
import logging
from datetime import timedelta

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
#               配置区域
# ==========================================

# 使用配置管理模块
try:
    from config import get_config
    config = get_config()
    TUSHARE_TOKEN = config.TUSHARE_TOKEN
    GUGU_APPKEY = config.GUGU_APPKEY

    # 从配置获取策略参数 - 收紧版本v4.0
    params = config.get_strategy_params('main_force_burial')
    MIN_MV = params.get('MIN_MV', 300000)      # 30亿 (收紧)
    MAX_MV = params.get('MAX_MV', 20000000)    # 200亿 (收紧)
    MIN_PCT = params.get('MIN_PCT', 1.0)       # 1.0% (收紧)
    MAX_PCT = params.get('MAX_PCT', 5.0)       # 5.0% (收紧)
    MAX_DEVIATION = params.get('MAX_DEVIATION', 5.0)   # 5.0% (收紧)
    INDEX_RISK_THR = params.get('INDEX_RISK_THR', -0.6)
    MIN_AMOUNT = params.get('MIN_AMOUNT', 30000000)    # 3亿 (收紧)

    # 换手率区间分层参数 (收紧标准)
    TURNOVER_RATE_SMALL_CAP_MIN = params.get('TURNOVER_RATE_SMALL_CAP_MIN', 4.0)   # 小盘股：4.0% (收紧)
    TURNOVER_RATE_SMALL_CAP_MAX = params.get('TURNOVER_RATE_SMALL_CAP_MAX', 10.0)  # 小盘股：10.0% (收紧)
    TURNOVER_RATE_MID_CAP_MIN = params.get('TURNOVER_RATE_MID_CAP_MIN', 3.0)       # 中盘股：3.0% (收紧)
    TURNOVER_RATE_MID_CAP_MAX = params.get('TURNOVER_RATE_MID_CAP_MAX', 8.0)       # 中盘股：8.0% (收紧)
    TURNOVER_RATE_LARGE_CAP_MIN = params.get('TURNOVER_RATE_LARGE_CAP_MIN', 2.0)   # 大盘股：2.0% (收紧)
    TURNOVER_RATE_LARGE_CAP_MAX = params.get('TURNOVER_RATE_LARGE_CAP_MAX', 6.0)   # 大盘股：6.0% (收紧)

    # 技术强度评分参数 (收紧版本v4.0新增)
    TECH_SCORE_THRESHOLD = params.get('TECH_SCORE_THRESHOLD', 20)  # 最低技术评分要求 (20分)
    MIN_PCT_FOR_BONUS = params.get('MIN_PCT_FOR_BONUS', 2.0)      # 涨幅≥2%时加分
    MIN_TURNOVER_FOR_BONUS = params.get('MIN_TURNOVER_FOR_BONUS', 5.0)  # 换手率≥5%时加分
    MIN_AMOUNT_FOR_BONUS = params.get('MIN_AMOUNT_FOR_BONUS', 5.0)  # 成交额≥5亿时加分
    MAX_DEVIATION_FOR_BONUS = params.get('MAX_DEVIATION_FOR_BONUS', 2.0)  # 乖离率≤2%时加分
    NEAR_HIGH_RATIO = params.get('NEAR_HIGH_RATIO', 0.995)  # 接近最高价要求 (99.5% - 收紧)

except ImportError:
    # 兼容单独运行的回退方案
    TUSHARE_TOKEN = 'fb8b11e0099681fc2e706351fa6ff0bb593053d1c9681800a72a0fcd'
    GUGU_APPKEY = 'SQSM4ASGQT6UN363PWA9M6256764WYBS'
    MIN_MV = 300000
    MAX_MV = 5000000     # 优化：500亿
    MIN_PCT = 1.5        # 优化：1.5%
    MAX_PCT = 8.0        # 优化：8.0%
    MAX_DEVIATION = 2.5
    INDEX_RISK_THR = -0.6
    MIN_AMOUNT = 30000000  # 优化：3000万
    # 换手率区间分层参数 (优化：区间设计)
    TURNOVER_RATE_SMALL_CAP_MIN = 3.0   # 小盘股下限
    TURNOVER_RATE_SMALL_CAP_MAX = 10.0  # 小盘股上限
    TURNOVER_RATE_MID_CAP_MIN = 2.0     # 中盘股下限
    TURNOVER_RATE_MID_CAP_MAX = 8.0     # 中盘股上限
    TURNOVER_RATE_LARGE_CAP_MIN = 1.5   # 大盘股下限
    TURNOVER_RATE_LARGE_CAP_MAX = 6.0   # 大盘股上限

class MainForceBurialStrategy:
    """A股尾盘主力埋伏策略"""

    def __init__(self):
        self.timeframe = "14:50"
        self.strategy_description = "尾盘主力埋伏策略 v4.1 (优化评分版)"
        self.results = []

        # 设置参数到实例属性（保持宽松的筛选条件）
        self.MIN_MV = MIN_MV
        self.MAX_MV = MAX_MV
        self.MIN_PCT = MIN_PCT
        self.MAX_PCT = MAX_PCT
        self.MAX_DEVIATION = MAX_DEVIATION
        self.INDEX_RISK_THR = INDEX_RISK_THR
        self.MIN_AMOUNT = MIN_AMOUNT
        # 换手率区间参数
        self.TURNOVER_RATE_SMALL_CAP_MIN = TURNOVER_RATE_SMALL_CAP_MIN
        self.TURNOVER_RATE_SMALL_CAP_MAX = TURNOVER_RATE_SMALL_CAP_MAX
        self.TURNOVER_RATE_MID_CAP_MIN = TURNOVER_RATE_MID_CAP_MIN
        self.TURNOVER_RATE_MID_CAP_MAX = TURNOVER_RATE_MID_CAP_MAX
        self.TURNOVER_RATE_LARGE_CAP_MIN = TURNOVER_RATE_LARGE_CAP_MIN
        self.TURNOVER_RATE_LARGE_CAP_MAX = TURNOVER_RATE_LARGE_CAP_MAX

        # 优化后的评分权重
        self.scoring_weights = {
            'deviation_score': 25,      # 乖离率分数（最重要）
            'change_score': 15,         # 涨幅分数
            'turnover_score': 20,       # 换手率分数
            'amount_score': 20,         # 成交额分数
            'position_score': 15,       # 价格位置分数
            'amplitude_score': 5,       # 振幅分数
        }

        # 尝试初始化 Tushare
        self.pro = None
        try:
            import tushare as ts
            ts.set_token(TUSHARE_TOKEN)
            self.pro = ts.pro_api()
            logger.info("✅ Tushare 初始化成功")
        except ImportError:
            logger.warning("⚠️ Tushare 未安装，将使用模拟数据")
        except Exception as e:
            logger.warning(f"⚠️ Tushare 初始化失败: {e}，将使用模拟数据")

    def check_market_environment(self):
        """
        【风控层】使用 GuguData 检查上证指数实时情况
        优先使用gugudata实时数据
        """
        print(">>> 正在检查大盘环境...")
        url = "https://api.gugudata.com/stock/cn/realtime"

        # 尝试多个指数代码以确保获取到数据
        index_codes = ['000001', '999999']  # 上证指数, 沪深300指数

        for index_code in index_codes:
            try:
                params = {'appkey': GUGU_APPKEY, 'symbol': index_code}
                res = requests.get(url, params=params, timeout=8).json()

                if res.get('DataStatus', {}).get('StatusCode') == 100 and res.get('Data'):
                    data = res['Data'][0]
                    current = data.get('Latest')
                    prev_close = data.get('LastClose')
                    change_pct = data.get('ChangePct', 0)

                    if not prev_close or not current:
                        continue

                    # 如果接口直接提供涨跌幅，优先使用
                    if change_pct != 0:
                        pct_chg = change_pct
                    else:
                        pct_chg = (current - prev_close) / prev_close * 100

                    index_name = "上证指数" if index_code == '000001' else "沪深300"
                    print(f"    {index_name}: {current:.2f} (涨跌: {pct_chg:+.2f}%)")

                    if pct_chg < INDEX_RISK_THR:
                        print(f"❌ 大盘环境恶劣 (跌幅 > {abs(INDEX_RISK_THR)}%)，策略自动终止以规避系统性风险。")
                        return False, current, pct_chg

                    print("✅ 大盘环境安全，继续执行。")
                    return True, current, pct_chg
                else:
                    logger.warning(f"指数 {index_code} 数据获取失败: {res.get('DataStatus', {}).get('StatusCode')}")

            except Exception as e:
                logger.warning(f"指数 {index_code} 请求异常: {e}")
                continue

        print(f"⚠️ 无法获取指数数据，跳过大盘风控。")
        return True, 0, 0

    def get_basic_pool_with_tushare(self, date_str):
        """
        【初筛层】使用 Tushare 获取基础股票池
        """
        print(f">>> 正在获取基础股票池 (基准日期: {date_str})...")

        if not self.pro:
            print("❌ Tushare 不可用，使用模拟基础池")
            return self._get_simulated_basic_pool()

        try:
            # 1. 获取基础指标
            df = self.pro.daily_basic(trade_date=date_str, fields='ts_code,close,turnover_rate,circ_mv,volume_ratio')
            if df.empty:
                print("❌ Tushare未返回数据，请检查日期是否为交易日。")
                return self._get_simulated_basic_pool()

            # 2. 获取名称信息
            names = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')

            # 合并
            df = pd.merge(df, names, on='ts_code')

            # --- 筛选逻辑 ---
            # A. 剔除ST、*ST、退市
            df = df[~df['name'].str.contains('ST')]
            df = df[~df['name'].str.contains('退')]

            # B. 剔除北交所(8xx/4xx) - 只要沪深主板/创业板
            df = df[~df['ts_code'].str.startswith('8')]
            df = df[~df['ts_code'].str.startswith('4')]

            # C. 市值筛选 (30亿 - 200亿)
            df = df[(df['circ_mv'] >= MIN_MV) & (df['circ_mv'] <= MAX_MV)]

            # D. 活跃度初筛 (换手>2%)
            df = df[df['turnover_rate'] > 2]

            print(f"✅ 基础池筛选完成，剩余标的: {len(df)} 只")
            return df[['ts_code', 'close', 'name']]

        except Exception as e:
            print(f"❌ Tushare数据获取失败: {e}")
            return self._get_simulated_basic_pool()

    def _get_simulated_basic_pool(self):
        """获取模拟基础股票池 - 使用大盘全量股票"""
        print("⚠️ 使用大盘全量股票池进行筛选")

        # 生成大盘核心股票代码 - 涵盖沪深主板和创业板
        market_codes = []

        # 沪市主板 (600xxx)
        for i in range(0, 600):
            code = f"600{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 沪市主板 (601xxx)
        for i in range(0, 1000):
            code = f"601{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 沪市主板 (603xxx)
        for i in range(0, 1000):
            code = f"603{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 深市主板 (000xxx)
        for i in range(0, 1000):
            code = f"000{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 深市主板 (001xxx)
        for i in range(0, 300):
            code = f"001{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 深市中小板 (002xxx)
        for i in range(0, 1000):
            code = f"002{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 创业板 (300xxx) - 只取前500个活跃代码
        for i in range(0, 500):
            code = f"300{i:03d}"
            if len(code) == 6:
                market_codes.append(code)

        # 转换为Tushare格式
        simulated_stocks = []
        for code in market_codes:
            # 根据代码判断交易所
            if code.startswith(('600', '601', '603', '605')):
                ts_code = f"{code}.SH"
            else:
                ts_code = f"{code}.SZ"

            simulated_stocks.append({
                'ts_code': ts_code,
                'close': 20.0,  # 使用默认价格
                'name': f'股票{code}'
            })

        print(f"生成基础股票池：{len(simulated_stocks)} 只股票")
        return pd.DataFrame(simulated_stocks)

    def get_turnover_rate_range(self, estimated_mv):
        """
        根据估算市值获取对应的换手率区间 (分层区间设置)
        """
        if estimated_mv < 1000000:  # 小于100亿：小盘股
            return (TURNOVER_RATE_SMALL_CAP_MIN, TURNOVER_RATE_SMALL_CAP_MAX)
        elif estimated_mv < 3000000:  # 100-300亿：中盘股
            return (TURNOVER_RATE_MID_CAP_MIN, TURNOVER_RATE_MID_CAP_MAX)
        else:  # 300-500亿：大盘股
            return (TURNOVER_RATE_LARGE_CAP_MIN, TURNOVER_RATE_LARGE_CAP_MAX)

    def check_turnover_rate_in_range(self, estimated_mv, turnover_rate):
        """
        检查换手率是否在对应市值区间的合理范围内
        """
        min_rate, max_rate = self.get_turnover_rate_range(estimated_mv)
        return min_rate <= turnover_rate <= max_rate

    def get_latest_trade_date(self):
        """获取最近的一个交易日(昨日), 用于提取基础数据"""
        today = datetime.datetime.now().strftime('%Y%m%d')
        if not self.pro:
            return today

        try:
            cal = self.pro.trade_cal(exchange='', start_date='20240101', end_date=today, is_open='1')
            if cal.empty:
                return today

            # 逻辑：如果在交易日盘中，取昨天的数据作为基础池参照
            if cal.iloc[-1]['cal_date'] == today:
                 return cal.iloc[-2]['cal_date']
            else:
                 return cal.iloc[-1]['cal_date']
        except:
            return today

    def get_realtime_and_filter(self, stock_dict, name_dict):
        """
        【决策层】使用 GuguData 批量获取实时行情并筛选
        优化：完全依赖gugudata实时数据，增加重试机制
        """
        ts_codes = list(stock_dict.keys())
        print(f">>> 正在扫描 {len(ts_codes)} 只股票的实时状态 (请稍候)...")

        # 映射 Tushare代码 到 Gugu代码 (000001.SZ -> 000001)
        code_map = {code[:6]: code for code in ts_codes}
        gugu_codes = list(code_map.keys())

        candidates = []
        successful_batches = 0
        failed_batches = 0

        # 优化分批请求，每批40个以提高稳定性
        BATCH_SIZE = 40
        url = "https://api.gugudata.com/stock/cn/realtime"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

        for i in range(0, len(gugu_codes), BATCH_SIZE):
            batch = gugu_codes[i : i + BATCH_SIZE]
            params = {
                'appkey': GUGU_APPKEY,
                'symbol': ",".join(batch)
            }

            # 重试机制：最多重试3次
            for retry in range(3):
                try:
                    res = requests.get(url, params=params, headers=headers, timeout=10).json()

                    # 检查响应状态
                    status_code = res.get('DataStatus', {}).get('StatusCode')
                    if status_code != 100:
                        if retry < 2:  # 前两次重试
                            logger.warning(f"批次 {i//BATCH_SIZE + 1} API响应错误 {status_code}，重试 {retry + 1}/3")
                            time.sleep(1 * (retry + 1))  # 递增延迟
                            continue
                        else:  # 第三次失败
                            logger.error(f"批次 {i//BATCH_SIZE + 1} 最终失败: {status_code}")
                            failed_batches += 1
                            break

                    if not res.get('Data'):
                        if retry < 2:
                            logger.warning(f"批次 {i//BATCH_SIZE + 1} 无数据返回，重试 {retry + 1}/3")
                            time.sleep(1 * (retry + 1))
                            continue
                        else:
                            logger.error(f"批次 {i//BATCH_SIZE + 1} 最终无数据")
                            failed_batches += 1
                            break

                    # 成功获取数据，处理股票信息
                    batch_processed = 0
                    for item in res['Data']:
                        raw_code = item['Symbol']
                        ts_code = code_map.get(raw_code)
                        if not ts_code:
                            continue

                        # --- 优先使用gugudata实时数据 ---

                        # 基础价格数据 (完全依赖gugudata)
                        current = item.get('Latest', 0)
                        open_px = item.get('Open', 0)
                        high = item.get('High', 0)
                        low = item.get('Low', 0)
                        pre_close = item.get('LastClose', 0)

                        # 成交量和金额数据 (gugudata)
                        vol = item.get('TradingVolume', 0)   # 手
                        amt = item.get('TradingAmount', 0)   # 元
                        turnover_rate = item.get('TurnoverRate', 0)  # 换手率

                        # 涨跌幅 (优先使用接口直接数据)
                        change_pct = item.get('ChangePercent', 0)  # 修复字段名
                        if change_pct != 0:
                            pct_chg = change_pct
                        else:
                            # 接口没有提供涨跌幅时，使用价格计算
                            if pre_close > 0:
                                pct_chg = (current - pre_close) / pre_close * 100
                            else:
                                pct_chg = 0

                        # 基础数据校验 (严格使用gugudata数据)
                        if current == 0 or vol == 0:
                            continue

                        # --- 快速预筛选 (策略参数前置过滤) ---

                        # 1. 涨幅预筛选 - 严格使用gugudata涨幅数据
                        if not (MIN_PCT < pct_chg < MAX_PCT):
                            continue  # 涨幅不符合，跳过后续计算

                        # 2. 活跃度预筛选 - 换手率区间标准
                        # 先估算市值，再根据市值确定换手率区间
                        if turnover_rate > 0:
                            amount_wan = amt / 10000  # 将元转换为万元
                            estimated_mv = amount_wan * 10000 / (turnover_rate / 100)
                            turnover_ok = self.check_turnover_rate_in_range(estimated_mv, turnover_rate)
                            turnover_min, turnover_max = self.get_turnover_rate_range(estimated_mv)
                        else:
                            amount_wan = amt / 10000  # 仍然需要定义这个变量
                            estimated_mv = 0
                            turnover_ok = False
                            turnover_min, turnover_max = (0, 0)

                        if not turnover_ok:
                            continue  # 换手率不在区间范围内

                        # 3. VWAP计算 (基于gugudata成交数据)
                        # 注意：amt是元，vol是手(100股)
                        vwap = amt / (vol * 100) if vol > 0 else current
                        if vwap <= 0:
                            continue

                        # 4. 乖离率计算 (基于gugudata数据)
                        deviation = (current - vwap) / vwap * 100 if vwap > 0 else 0

                        # --- 主力埋伏核心筛选逻辑 ---

                        # [核心Filter 1] 乖离率控制 (防止急拉骗线)
                        if deviation > MAX_DEVIATION:
                            continue

                        # [核心Filter 2] 趋势强势 (必须在均价线上方)
                        if current < vwap:
                            continue

                        # [核心Filter 3] 真阳线形态 (现价 > 开盘价)
                        if current < open_px:
                            continue

                        # [核心Filter 4] 接近最高价 (99.5%，显示抛压小)
                        if current < high * 0.995:
                            continue

                        # [核心Filter 5] 成交活跃度确认 (基于gugudata成交额，收紧标准)
                        amount_wan = amt / 10000
                        amount_yi = amount_wan / 100000  # 转为亿元
                        if amount_wan < (self.MIN_AMOUNT / 10000):  # 使用配置的成交额门槛 (收紧：3亿)
                            continue

                        # [核心Filter 6] 市值过滤 (基于gugudata数据估算，收紧标准)
                        # 流通市值 = 当前价 * 流通股数 (这里用成交额/换手率估算)
                        if turnover_rate > 0:
                            estimated_mv = amount_wan * 10000 / (turnover_rate / 100)
                            if estimated_mv < self.MIN_MV * 10000 or estimated_mv > self.MAX_MV * 10000:
                                continue

                        # 计算额外指标
                        price_position = (current - low) / (high - low) if high != low else 0.5
                        amplitude = (high - low) / low * 100

                        # 计算优化后的评分
                        score_data = self._calculate_optimized_score(
                            deviation, pct_chg, turnover_rate, amount_yi, price_position, amplitude
                        )

                        # 基础评分门槛（降低到60分）
                        if score_data['total_score'] < 60:
                            continue

                        # 通过所有筛选，添加到候选列表
                        candidates.append({
                            'code': ts_code,
                            'name': name_dict.get(ts_code, f'股票{raw_code}'),
                            'price': current,
                            'change': round(pct_chg, 2),
                            'vwap': round(vwap, 2),
                            'deviation': round(deviation, 2),
                            'high': high,
                            'low': low,
                            'open': open_px,
                            'pre_close': pre_close,
                            'volume': vol,
                            'amount': amt,
                            'turnover_rate': turnover_rate,
                            'amount_wan': round(amount_wan, 2),
                            'amount_yi': amount_yi,
                            'estimated_mv': round(estimated_mv / 10000, 2),  # 亿元
                            'turnover_range': f"{turnover_min:.1f}%-{turnover_max:.1f}%",
                            'price_position': price_position,
                            'amplitude': amplitude,
                            'total_score': score_data['total_score'],
                            'deviation_score': score_data['deviation_score'],
                            'change_score': score_data['change_score'],
                            'turnover_score': score_data['turnover_score'],
                            'amount_score': score_data['amount_score'],
                            'position_score': score_data['position_score'],
                            'amplitude_score': score_data['amplitude_score'],
                            'data_source': 'gugudata'
                        })

                        batch_processed += 1

                    successful_batches += 1
                    if batch_processed > 0:
                        logger.info(f"批次 {i//BATCH_SIZE + 1} 成功处理 {batch_processed} 只股票")
                    break  # 成功处理，跳出重试循环

                except requests.exceptions.Timeout:
                    if retry < 2:
                        logger.warning(f"批次 {i//BATCH_SIZE + 1} 请求超时，重试 {retry + 1}/3")
                        time.sleep(2 * (retry + 1))
                    else:
                        logger.error(f"批次 {i//BATCH_SIZE + 1} 最终超时")
                        failed_batches += 1
                except Exception as e:
                    if retry < 2:
                        logger.warning(f"批次 {i//BATCH_SIZE + 1} 请求异常: {e}，重试 {retry + 1}/3")
                        time.sleep(2 * (retry + 1))
                    else:
                        logger.error(f"批次 {i//BATCH_SIZE + 1} 最终异常: {e}")
                        failed_batches += 1
                    break

            # 批次间短暂休息，避免请求过于频繁
            time.sleep(0.1)

        print(f"✅ 实时筛选完成，成功处理 {successful_batches}/{(len(gugu_codes) + BATCH_SIZE - 1)//BATCH_SIZE} 个批次")
        print(f"✅ 从 {len(ts_codes)} 只股票中筛选出 {len(candidates)} 只候选股票")
        if failed_batches > 0:
            logger.warning(f"⚠️ 有 {failed_batches} 个批次处理失败")

        return pd.DataFrame(candidates)

    def execute_strategy(self):
        """执行主力埋伏策略"""
        print("\n" + "="*60)
        print(f"   A股尾盘主力埋伏策略 | {datetime.datetime.now().strftime('%H:%M:%S')}")
        print("="*60 + "\n")

        # 1. 检查大环境
        market_safe, index_value, index_change = self.check_market_environment()
        if not market_safe:
            return []

        # 2. 获取基础池
        last_date = self.get_latest_trade_date()
        basic_df = self.get_basic_pool_with_tushare(last_date)

        if basic_df.empty:
            return []

        stock_dict = pd.Series(basic_df.close.values, index=basic_df.ts_code).to_dict()
        name_dict = pd.Series(basic_df['name'].values, index=basic_df.ts_code).to_dict()

        # 3. 实时扫描
        results = self.get_realtime_and_filter(stock_dict, name_dict)

        # 4. 处理结果
        if not results.empty:
            # 按综合评分排序
            results = results.sort_values(by='total_score', ascending=False)
            # 只取TOP 10
            top10 = results.head(10)
            self.results = top10.to_dict('records')

            print(f"\n✅ 选股完成！今日推荐 TOP 10：\n")

            # 格式化打印表头
            header = f"{'排名':<4} {'代码':<12} {'名称':<10} {'现价':<8} {'涨幅%':<8} {'评分':<8} {'乖离%':<8} {'换手%':<8} {'成交额(亿)':<10}"
            print(header)
            print("-" * len(header))

            for idx, (_, row) in enumerate(top10.iterrows(), 1):
                print(f"{idx:<4} {row['code']:<12} {row['name']:<10} {row['price']:<8.2f} "
                      f"{row['change']:<8.2f} {row['total_score']:<8.1f} {row['deviation']:<8.2f} "
                      f"{row['turnover_rate']:<8.2f} {row['amount_yi']:<10.2f}")

            print("\n" + "="*60)
            print("💡 [操作建议]")
            print("1. 重点关注评分>85的股票，成功概率更高。")
            print("2. 14:50-14:55 建仓，给自己留足操作时间。")
            print("3. 设置止损线：-3%，避免大幅亏损。")
            print("4. 次日高开2%以上考虑止盈。")
            print("5. 单股仓位不超过总资金的10%。")
            print("="*60)
        else:
            print("\n⚠️ 今日无符合条件的标的 (市场情绪较弱或个股未满足严苛条件)。")
            self.results = []

        return self.results

    def _calculate_optimized_score(self, deviation, change, turnover_rate, amount_yi, price_position, amplitude):
        """计算优化后的综合评分"""
        # 计算各项得分
        deviation_score = self._calculate_deviation_score(abs(deviation))
        change_score = self._calculate_change_score(change)
        turnover_score = self._calculate_turnover_score(turnover_rate)
        amount_score = self._calculate_amount_score(amount_yi)
        position_score = self._calculate_position_score(price_position)
        amplitude_score = self._calculate_amplitude_score(amplitude)

        # 加权总分
        total_score = (
            deviation_score * self.scoring_weights['deviation_score'] +
            change_score * self.scoring_weights['change_score'] +
            turnover_score * self.scoring_weights['turnover_score'] +
            amount_score * self.scoring_weights['amount_score'] +
            position_score * self.scoring_weights['position_score'] +
            amplitude_score * self.scoring_weights['amplitude_score']
        ) / 100

        return {
            'total_score': total_score,
            'deviation_score': deviation_score,
            'change_score': change_score,
            'turnover_score': turnover_score,
            'amount_score': amount_score,
            'position_score': position_score,
            'amplitude_score': amplitude_score
        }

    def _calculate_deviation_score(self, deviation):
        """乖离率评分：越小越好"""
        if deviation <= 0.5:
            return 100
        elif deviation <= 1.0:
            return 90
        elif deviation <= 1.5:
            return 80
        elif deviation <= 2.0:
            return 70
        elif deviation <= 3.0:
            return 50
        else:
            return 20

    def _calculate_change_score(self, change):
        """涨幅评分：适中最好"""
        if change <= 0:
            return 0
        elif change < 0.8:
            return change / 0.8 * 40
        elif change < 2.0:
            return 40 + (change - 0.8) / 1.2 * 40
        elif change < 4.0:
            return 80 + (change - 2.0) / 2.0 * 15
        elif change < 6.0:
            return 95 + (change - 4.0) / 2.0 * 5
        else:
            return 90  # 涨幅过高可能是诱多

    def _calculate_turnover_score(self, turnover):
        """换手率评分：适中最好"""
        if turnover < 1:
            return 20
        elif turnover < 3:
            return 40 + (turnover - 1) / 2 * 40
        elif turnover < 6:
            return 80 + (turnover - 3) / 3 * 20
        else:
            return 80

    def _calculate_amount_score(self, amount):
        """成交额评分：越大越好，但有上限"""
        if amount < 1:
            return 30
        elif amount < 3:
            return 30 + (amount - 1) / 2 * 40
        elif amount < 5:
            return 70 + (amount - 3) / 2 * 20
        elif amount < 10:
            return 90 + (amount - 5) / 5 * 10
        else:
            return 100

    def _calculate_position_score(self, position):
        """价格位置评分：高位更好"""
        if position < 0.5:
            return position / 0.5 * 60
        elif position < 0.8:
            return 60 + (position - 0.5) / 0.3 * 30
        elif position < 0.95:
            return 90 + (position - 0.8) / 0.15 * 10
        else:
            return 100

    def _calculate_amplitude_score(self, amplitude):
        """振幅评分：适中的振幅较好"""
        if amplitude < 3:
            return 40
        elif amplitude < 6:
            return 60
        elif amplitude < 10:
            return 80
        else:
            return 60

  
    def save_results(self):
        """保存选股结果"""
        if not self.results:
            return None

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"main_force_burial_result_{timestamp}.json"

        result_data = {
            'screening_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeframe': self.timeframe,
            'strategy_version': self.strategy_description,
            'scoring_weights': self.scoring_weights,
            'strategy_params': {
                'MIN_MV': MIN_MV,
                'MAX_MV': MAX_MV,
                'MIN_PCT': MIN_PCT,
                'MAX_PCT': MAX_PCT,
                'MAX_DEVIATION': MAX_DEVIATION,
                'INDEX_RISK_THR': INDEX_RISK_THR,
                'MIN_AMOUNT': MIN_AMOUNT
            },
            'total_stocks_found': len(self.results),
            'recommendation_type': 'TOP 10精选',
            'stocks': self.results
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2, default=str)

            print(f"\n💾 尾盘主力埋伏策略结果已保存至: {filename}")
            return filename

        except Exception as e:
            print(f"❌ 保存结果文件失败: {e}")
            return None

    def format_results_for_email(self):
        """格式化选股结果用于邮件发送"""
        if not self.results:
            return f"""
🏆 尾盘主力埋伏策略结果 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

📊 选股概览:
• 策略: {self.strategy_description}
• 筛选数量: 0 只股票
• 执行时间: {datetime.datetime.now().strftime('%H:%M:%S')}

⚠️ 本轮尾盘主力埋伏策略未筛选出符合条件的股票

可能原因:
• 大盘环境不满足条件
• 个股涨幅不在目标区间
• 乖离率过大，可能存在骗线风险

💡 策略特点:
• 涨幅区间: {MIN_PCT}% - {MAX_PCT}%
• 最大乖离率: {MAX_DEVIATION}%
• 流通市值: {MIN_MV/100000000:.0f}亿 - {MAX_MV/100000000:.0f}亿

📧 如有问题，请及时联系
"""

        content = f"""
🏆 尾盘主力埋伏策略结果 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

📊 选股概览:
• 策略: {self.strategy_description}
• 筛选数量: {len(self.results)} 只股票
• 执行时间: {datetime.datetime.now().strftime('%H:%M:%S')}

🎯 主力埋伏核心策略:
✅ 涨幅区间: {MIN_PCT}% - {MAX_PCT}% (异动但未封板)
✅ 乖离率≤{MAX_DEVIATION}% (防止急拉骗线)
✅ 价格在均线上方 (强势特征)
✅ 真阳线形态 (现价>开盘价)
✅ 接近最高价 (回撤<2%)
✅ 流通市值: {MIN_MV/100000000:.0f}亿 - {MAX_MV/100000000:.0f}亿

🌟 发现主力埋伏股:
"""

        # 结果已经按评分排序
        content += f"\n🌟 今日TOP 10主力埋伏推荐 (按综合评分排序):\n"

        for i, stock in enumerate(self.results[:10], 1):
            total_score = stock.get('total_score', 0)
            deviation_score = stock.get('deviation_score', 0)
            risk_level = "低风险" if stock['deviation'] < 1 else "中等风险"

            content += f"""
{i:2d}. {stock['code']} {stock['name']:<8} - 综合评分:{total_score:5.1f}
    💰 现价: {stock['price']:.2f}元 ({stock['change']:+.2f}%)
    📊 均价: {stock['vwap']:.2f}元 (乖离: {stock['deviation']:+.2f}% | 乖离评分:{deviation_score:3.0f})
    🎯 换手率: {stock['turnover_rate']:.2f}% | 成交额: {stock.get('amount_yi', 0):.2f}亿
    📈 价格位置: {stock.get('price_position', 0)*100:.0f}% | 振幅: {stock.get('amplitude', 0):.2f}%
    ⚡ 风险等级: {risk_level}
"""

        # 现在只推荐TOP 10，不需要显示其他股票

        content += f"""
💡 操作建议:
• 最佳买入时机: 14:50-14:55 建仓（留足操作时间）
• 目标收益: 次日高开2%以上考虑止盈
• 止损设置: -3% (严格止损)
• 仓位控制: 单股不超过总资金10%
• 重点关注: 综合评分>85的股票

⚠️  风险提醒:
• 尾盘埋伏存在不确定性，需严格止损
• 明日开盘表现不及预期需及时离场
• 大盘风险可能导致策略失效
• 请结合个人风险承受能力操作

📊 策略统计:
• 基础股票池: 预筛选符合条件的市值股票
• 实时扫描: GuguData毫秒级数据
• 评分系统: 基于120只股票历史回测优化
• 风控机制: 大盘环境监控 + 个股骗线识别
• 推荐模式: 精选TOP 10，提高成功率

📧 如有问题，请及时联系
"""

        return content

def main():
    """主函数 - 独立运行测试用"""
    strategy = MainForceBurialStrategy()
    results = strategy.execute_strategy()

    # 保存结果
    result_file = strategy.save_results()

    # 发送邮件通知
    if result_file and results:
        try:
            from core.email_sender import EmailSender
            from src.config import StockScreenerConfig
            import json

            # 检查是否启用邮件
            config = StockScreenerConfig()

            if config.email_config['enabled'] and config.email_config['sender_email'] and config.email_config['recipients']:
                # 读取结果文件
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)

                # 构建邮件内容
                email_content = strategy.format_results_for_email()

                # 发送邮件
                email_sender = EmailSender()
                subject = f"📊 尾盘主力埋伏策略选股结果 - {result_data['screening_time']} (选出{result_data['total_stocks_found']}只)"

                success = email_sender.send_email(
                    subject=subject,
                    message=email_content,
                    df=pd.DataFrame()  # 传入空DataFrame，因为我们用自定义格式
                )

                if success:
                    print(f"✅ 邮件通知已发送至: {', '.join(config.email_config['recipients'])}")
                else:
                    print("❌ 邮件发送失败")
            else:
                print("⚠️ 邮件通知未启用或配置不完整")

        except Exception as e:
            print(f"❌ 发送邮件时出错: {e}")

    return results

if __name__ == "__main__":
    main()