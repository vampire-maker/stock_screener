#!/usr/bin/env python3
"""
A股尾盘主力埋伏策略系统 - Web可视化界面
基于Streamlit构建
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

# 页面配置
st.set_page_config(
    page_title="A股选股策略系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stock-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .score-high { border-left-color: #10b981; }
    .score-medium { border-left-color: #f59e0b; }
    .score-low { border-left-color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
# 自定义策略配置存储
if 'custom_configs' not in st.session_state:
    st.session_state.custom_configs = {}
if 'selected_config' not in st.session_state:
    st.session_state.selected_config = "默认配置"

# ==================== 导入策略模块 ====================
try:
    from src.config import StockScreenerConfig
    from src.main_force_burial_strategy import MainForceBurialStrategy
    from core.email_sender import EmailSender
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    st.error(f"⚠️ 模块导入失败: {e}")

# ==================== 辅助函数 ====================
def load_latest_result():
    """加载最新的选股结果"""
    result_files = []
    for file in os.listdir('.'):
        if file.startswith('main_force_burial_result_') and file.endswith('.json'):
            result_files.append(file)

    if result_files:
        latest = max(result_files)
        with open(latest, 'r', encoding='utf-8') as f:
            return json.load(f), latest
    return None, None

def get_all_results():
    """获取所有历史结果"""
    results = []
    for file in sorted(os.listdir('.'), reverse=True):
        if file.startswith('main_force_burial_result_') and file.endswith('.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append(data)
            except:
                continue
            if len(results) >= 30:  # 最多显示30条历史
                break
    return results

def run_stock_screening():
    """执行选股策略"""
    if not CONFIG_AVAILABLE:
        return None, "配置模块未正确加载"

    try:
        strategy = MainForceBurialStrategy()
        results = strategy.execute_strategy()
        result_file = strategy.save_results()
        return results, result_file
    except Exception as e:
        return None, str(e)

# ==================== 自定义配置管理 ====================
CONFIG_FILE = "strategy_configs.json"

def load_custom_configs():
    """从文件加载自定义配置"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_custom_configs(configs):
    """保存自定义配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存失败: {e}")
        return False

def get_default_config():
    """获取默认配置"""
    return {
        'name': '默认配置',
        'description': '主力埋伏策略 v4.1 (优化评分版)',
        'params': {
            'MIN_MV': 200000,  # 20亿
            'MAX_MV': 20000000,  # 200亿
            'MIN_PCT': 0.5,  # 0.5%
            'MAX_PCT': 8.0,  # 8.0%
            'MAX_DEVIATION': 5.0,
            'INDEX_RISK_THR': -0.6,
            'MIN_AMOUNT': 10000000,  # 1亿
        },
        'weights': {
            'deviation_score': 25,
            'change_score': 15,
            'turnover_score': 20,
            'amount_score': 20,
            'position_score': 15,
            'amplitude_score': 5
        }
    }

def get_all_configs():
    """获取所有配置（包括默认配置）"""
    configs = {'默认配置': get_default_config()}
    configs.update(load_custom_configs())
    return configs

# ==================== 主页面 ====================
def main():
    """主应用"""

    # 侧边栏
    with st.sidebar:
        st.markdown("# 📈 A股选股系统")
        st.markdown("---")

        page = st.radio(
            "导航菜单",
            ["🏠 首页", "📊 最新选股", "📜 历史记录", "🔍 股票分析", "⚙️ 策略配置", "🚀 手动选股"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # 系统状态
        st.markdown("### 系统状态")
        if CONFIG_AVAILABLE:
            st.success("✅ 配置正常")
        else:
            st.error("❌ 配置异常")

        # 刷新按钮
        if st.button("🔄 刷新数据"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()

    # 首页
    if page == "🏠 首页":
        show_homepage()

    # 最新选股
    elif page == "📊 最新选股":
        show_latest_results()

    # 历史记录
    elif page == "📜 历史记录":
        show_history()

    # 股票分析
    elif page == "🔍 股票分析":
        show_stock_analysis()

    # 策略配置
    elif page == "⚙️ 策略配置":
        show_strategy_config()

    # 手动选股
    elif page == "🚀 手动选股":
        show_manual_screening()

# ==================== 首页 ====================
def show_homepage():
    """首页"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown("# 🚀 A股尾盘主力埋伏策略系统")
    st.markdown("### 基于量化分析的智能选股 | 实时数据 | 自动邮件通知")
    st.markdown('</div>', unsafe_allow_html=True)

    # 核心指标
    col1, col2, col3, col4 = st.columns(4)

    # 获取最新结果统计
    latest_data, _ = load_latest_result()

    if latest_data:
        total_stocks = latest_data.get('total_stocks_found', 0)
        avg_score = pd.DataFrame(latest_data.get('stocks', []))['total_score'].mean() if latest_data.get('stocks') else 0

        col1.metric("今日选股", f"{total_stocks}只")
        col2.metric("平均评分", f"{avg_score:.1f}")
        col3.metric("执行时间", latest_data.get('screening_time', ''))
        col4.metric("策略版本", "v4.1")
    else:
        col1.metric("今日选股", "暂无数据")
        col2.metric("平均评分", "--")
        col3.metric("执行时间", "--")
        col4.metric("策略版本", "v4.1")

    st.markdown("---")

    # 快速查看今日推荐
    st.subheader("📌 今日推荐 TOP 5")

    if latest_data and latest_data.get('stocks'):
        stocks = latest_data['stocks'][:5]
        for i, stock in enumerate(stocks, 1):
            score = stock['total_score']
            score_class = 'score-high' if score >= 75 else 'score-medium' if score >= 70 else 'score-low'

            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            col1.write(f"**#{i}**")
            col2.write(f"`{stock['code']}`")
            col3.write(f"**{stock['name']}**")
            col4.write(f"{stock['price']:.2f}元")
            col5.write(f"{stock['change']:+.2f}%")
    else:
        st.info("暂无选股数据，请先执行选股")

    st.markdown("---")

    # 策略说明
    with st.expander("📖 策略说明"):
        st.markdown("""
        ### 主力埋伏策略 v4.1

        **执行时间**: 每天14:50（尾盘）

        **核心逻辑**: 捕捉尾盘主力资金介入信号，博取次日开盘溢价

        **评分权重**:
        - 乖离率 (25%) - 避免追高风险
        - 换手率 (20%) - 反映活跃度
        - 成交额 (20%) - 确保流动性
        - 价格位置 (15%) - 捕捉强势特征
        - 涨幅 (15%) - 适中的涨幅表现
        - 振幅 (5%) - 价格稳定性

        **筛选条件**:
        - 市值: 20亿 - 200亿
        - 涨幅: 0.5% - 8.0%
        - 成交额: ≥1亿
        - 乖离率: ≤5%
        - 换手率: 1.5% - 8.0%
        """)

# ==================== 最新选股页面 ====================
def show_latest_results():
    """显示最新选股结果"""
    st.markdown("# 📊 今日选股结果")

    latest_data, filename = load_latest_result()

    if latest_data is None:
        st.warning("暂无选股数据")
        return

    # 基本信息
    col1, col2, col3 = st.columns(3)
    col1.info(f"**执行时间**: {latest_data.get('screening_time', '')}")
    col2.info(f"**选出股票**: {latest_data.get('total_stocks_found', 0)}只")
    col3.info(f"**策略版本**: {latest_data.get('strategy_version', '')}")

    st.markdown("---")

    # 选股结果表格
    st.subheader("📈 TOP 10 推荐股票")

    stocks = latest_data.get('stocks', [])
    if stocks:
        # 准备数据
        df_data = []
        for s in stocks:
            df_data.append({
                '排名': stocks.index(s) + 1,
                '代码': s['code'],
                '名称': s['name'],
                '现价(元)': round(s['price'], 2),
                '涨幅(%)': round(s['change'], 2),
                '评分': round(s['total_score'], 1),
                '乖离率(%)': round(s['deviation'], 2),
                '换手率(%)': round(s['turnover_rate'], 2),
                '成交额(亿)': round(s.get('amount_yi', 0), 2)
            })

        df = pd.DataFrame(df_data)

        # 颜色标记
        def color_score(val):
            if val >= 75:
                return 'background-color: #d1fae5'
            elif val >= 70:
                return 'background-color: #fef3c7'
            return 'background-color: #fee2e2'

        def color_change(val):
            if val > 0:
                return 'color: green'
            return 'color: red'

        # 显示表格
        st.dataframe(
            df.style
            .applymap(color_score, subset=['评分'])
            .applymap(color_change, subset=['涨幅(%)'])
            .format({'涨幅(%)': '{:+.1f}', '乖离率(%)': '{:+.1f}'}),
            use_container_width=True
        )

        st.markdown("---")

        # 详细信息
        st.subheader("📋 详细信息")

        for stock in stocks[:5]:
            with st.expander(f"📌 {stock['name']} ({stock['code']}) - 评分: {round(stock['total_score'], 1)}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**基本信息**")
                    st.write(f"- 代码: `{stock['code']}`")
                    st.write(f"- 现价: {stock['price']:.2f}元")
                    st.write(f"- 涨幅: {stock['change']:+.2f}%")

                with col2:
                    st.markdown("**技术指标**")
                    st.write(f"- 乖离率: {stock['deviation']:+.2f}%")
                    st.write(f"- 换手率: {stock['turnover_rate']:.2f}%")
                    st.write(f"- 成交额: {stock.get('amount_yi', 0):.2f}亿")

                with col3:
                    st.markdown("**评分详情**")
                    st.write(f"- 乖离率得分: {stock.get('deviation_score', 0)}")
                    st.write(f"- 涨幅得分: {stock.get('change_score', 0)}")
                    st.write(f"- 换手率得分: {stock.get('turnover_score', 0)}")

# ==================== 历史记录页面 ====================
def show_history():
    """显示历史记录"""
    st.markdown("# 📜 历史选股记录")

    results = get_all_results()

    if not results:
        st.warning("暂无历史记录")
        return

    # 统计信息
    st.subheader("📊 统计概览")

    total_stocks = sum([r.get('total_stocks_found', 0) for r in results])
    avg_stocks = total_stocks / len(results) if results else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("记录次数", len(results))
    col2.metric("总选股数", total_stocks)
    col3.metric("平均每次", f"{avg_stocks:.1f}只")

    st.markdown("---")

    # 历史列表
    st.subheader("📅 历史记录列表")

    for result in results[:20]:
        with st.expander(f"📅 {result.get('screening_time', '')} - 选出{result.get('total_stocks_found', 0)}只股票"):
            stocks = result.get('stocks', [])
            if stocks:
                # 显示前5只
                for stock in stocks[:5]:
                    st.write(f"**{stock['name']}** ({stock['code']}) - {stock['price']:.2f}元 {stock['change']:+.2f}% - 评分: {round(stock['total_score'], 1)}")

# ==================== 股票分析页面 ====================
def show_stock_analysis():
    """股票分析页面"""
    st.markdown("# 🔍 股票详情分析")

    # 获取所有历史结果中的股票
    all_stocks = {}
    results = get_all_results()

    for result in results:
        for stock in result.get('stocks', []):
            code = stock['code']
            if code not in all_stocks:
                all_stocks[code] = stock

    if not all_stocks:
        st.warning("暂无股票数据")
        return

    # 股票选择
    col1, col2 = st.columns([2, 1])

    with col1:
        stock_options = [f"{s['code']} - {s['name']}" for s in all_stocks.values()]
        selected = st.selectbox("选择股票", stock_options)

    with col2:
        if selected:
            code = selected.split(' - ')[0]
            stock_data = all_stocks.get(code)

            if stock_data:
                st.metric("现价", f"{stock_data['price']:.2f}元")
                st.metric("涨幅", f"{stock_data['change']:+.2f}%")
                st.metric("评分", f"{round(stock_data['total_score'], 1)}")

    # 详细分析
    if selected:
        code = selected.split(' - ')[0]
        stock_data = all_stocks.get(code)

        if stock_data:
            st.markdown("---")
            st.subheader(f"📊 {stock_data['name']} ({stock_data['code']}) 详细分析")

            # 评分雷达图
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 评分组成")
                scores = {
                    '乖离率得分': stock_data.get('deviation_score', 0),
                    '涨幅得分': stock_data.get('change_score', 0),
                    '换手率得分': stock_data.get('turnover_score', 0),
                    '成交额得分': stock_data.get('amount_score', 0),
                    '价格位置得分': stock_data.get('position_score', 0),
                    '振幅得分': stock_data.get('amplitude_score', 0),
                }

                for name, score in scores.items():
                    st.progress(score / 100, f"{name}: {score}")

            with col2:
                st.markdown("### 技术指标")
                st.write(f"- **VWAP**: {stock_data.get('vwap', 0):.2f}元")
                st.write(f"- **最高价**: {stock_data['high']:.2f}元")
                st.write(f"- **最低价**: {stock_data['low']:.2f}元")
                st.write(f"- **开盘价**: {stock_data['open']:.2f}元")
                st.write(f"- **价格位置**: {stock_data.get('price_position', 0)*100:.1f}%")
                st.write(f"- **振幅**: {stock_data.get('amplitude', 0):.2f}%")

# ==================== 策略配置页面 ====================
def show_strategy_config():
    """策略配置页面"""
    st.markdown("# ⚙️ 策略参数配置")

    # 加载所有配置
    all_configs = get_all_configs()

    # 创建两列布局
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📋 配置列表")

        # 显示配置列表
        for config_name in list(all_configs.keys()):
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{config_name}**")
                if config_name != '默认配置':
                    if c2.button("✏️", key=f"edit_{config_name}"):
                        st.session_state.edit_config = config_name
                    if c3.button("🗑️", key=f"delete_{config_name}"):
                        if st.session_state.get('confirm_delete', '') == config_name:
                            custom_configs = load_custom_configs()
                            if config_name in custom_configs:
                                del custom_configs[config_name]
                                save_custom_configs(custom_configs)
                                st.session_state.custom_configs = custom_configs
                                st.rerun()
                        else:
                            st.session_state.confirm_delete = config_name
                            st.warning("再次点击确认删除")

        if st.button("➕ 新建配置", use_container_width=True):
            st.session_state.edit_config = None
            st.session_state.show_new_config = True

    with col2:
        st.markdown("### 📝 配置详情")

        # 确定要编辑的配置
        edit_config_name = st.session_state.get('edit_config')
        show_new = st.session_state.get('show_new_config', False)

        if show_new or edit_config_name is not None:
            # 新建或编辑配置
            is_new = edit_config_name is None
            config_title = "新建配置" if is_new else f"编辑: {edit_config_name}"

            st.subheader(config_title)

            # 配置名称
            config_name = st.text_input(
                "配置名称",
                value="" if is_new else edit_config_name,
                disabled=not is_new
            )

            config_desc = st.text_input(
                "配置描述",
                value="" if is_new else all_configs[edit_config_name].get('description', '')
            )

            st.markdown("---")
            st.markdown("#### 基础参数")

            # 获取当前配置值
            current_config = all_configs[edit_config_name] if not is_new else get_default_config()
            params = current_config.get('params', {})

            c1, c2, c3 = st.columns(3)
            min_mv = c1.number_input("最小市值(亿)", 5, 500, params.get('MIN_MV', 200000) // 100000000)
            max_mv = c2.number_input("最大市值(亿)", 50, 2000, params.get('MAX_MV', 20000000) // 100000000)
            min_pct = c3.number_input("最小涨幅(%)", 0.0, 10.0, params.get('MIN_PCT', 0.5), 0.1)

            c1, c2, c3 = st.columns(3)
            max_pct = c1.number_input("最大涨幅(%)", 0.0, 20.0, params.get('MAX_PCT', 8.0), 0.1)
            max_dev = c2.number_input("最大乖离率(%)", 0.0, 20.0, params.get('MAX_DEVIATION', 5.0), 0.1)
            min_amt = c3.number_input("最小成交额(亿)", 0.1, 50.0, params.get('MIN_AMOUNT', 10000000) / 100000000, 0.1)

            st.markdown("---")
            st.markdown("#### 评分权重 (总和应为100)")

            weights = current_config.get('weights', {})
            w1, w2, w3 = st.columns(3)
            dev_weight = w1.number_input("乖离率权重", 0, 100, weights.get('deviation_score', 25))
            chg_weight = w2.number_input("涨幅权重", 0, 100, weights.get('change_score', 15))
            trn_weight = w3.number_input("换手率权重", 0, 100, weights.get('turnover_score', 20))

            w1, w2, w3 = st.columns(3)
            amt_weight = w1.number_input("成交额权重", 0, 100, weights.get('amount_score', 20))
            pos_weight = w2.number_input("价格位置权重", 0, 100, weights.get('position_score', 15))
            amp_weight = w3.number_input("振幅权重", 0, 100, weights.get('amplitude_score', 5))

            total_weight = dev_weight + chg_weight + trn_weight + amt_weight + pos_weight + amp_weight
            st.info(f"权重总和: {total_weight}% " + ("✅" if total_weight == 100 else "⚠️ 应为100%"))

            # 保存按钮
            col_save, col_cancel = st.columns(2)
            if col_save.button("💾 保存配置", type="primary", use_container_width=True):
                if not config_name:
                    st.error("请输入配置名称")
                elif config_name == '默认配置' and is_new:
                    st.error("不能使用'默认配置'作为名称")
                elif total_weight != 100:
                    st.error("权重总和必须为100%")
                else:
                    custom_configs = load_custom_configs()
                    new_config = {
                        'name': config_name,
                        'description': config_desc,
                        'params': {
                            'MIN_MV': min_mv * 100000000,
                            'MAX_MV': max_mv * 100000000,
                            'MIN_PCT': min_pct,
                            'MAX_PCT': max_pct,
                            'MAX_DEVIATION': max_dev,
                            'INDEX_RISK_THR': -0.6,
                            'MIN_AMOUNT': min_amt * 100000000,
                        },
                        'weights': {
                            'deviation_score': dev_weight,
                            'change_score': chg_weight,
                            'turnover_score': trn_weight,
                            'amount_score': amt_weight,
                            'position_score': pos_weight,
                            'amplitude_score': amp_weight
                        }
                    }
                    custom_configs[config_name] = new_config
                    if save_custom_configs(custom_configs):
                        st.session_state.custom_configs = custom_configs
                        st.session_state.edit_config = None
                        st.session_state.show_new_config = False
                        st.success(f"配置 '{config_name}' 已保存！")
                        st.rerun()

            if col_cancel.button("取消", use_container_width=True):
                st.session_state.edit_config = None
                st.session_state.show_new_config = False
                st.rerun()

        else:
            # 显示当前选中配置的详情
            selected = st.selectbox("选择配置查看", list(all_configs.keys()))
            if selected:
                config = all_configs[selected]
                st.markdown(f"**描述**: {config.get('description', '')}")

                st.markdown("---")
                st.markdown("#### 基础参数")

                params = config.get('params', {})
                c1, c2, c3 = st.columns(3)
                c1.metric("最小市值", f"{params.get('MIN_MV', 0) / 100000000:.0f}亿")
                c2.metric("最大市值", f"{params.get('MAX_MV', 0) / 100000000:.0f}亿")
                c3.metric("涨幅区间", f"{params.get('MIN_PCT', 0)}% - {params.get('MAX_PCT', 0)}%")

                c1, c2, c3 = st.columns(3)
                c1.metric("最大乖离率", f"{params.get('MAX_DEVIATION', 0)}%")
                c2.metric("风险阈值", f"{params.get('INDEX_RISK_THR', 0)}%")
                c3.metric("最小成交额", f"{params.get('MIN_AMOUNT', 0) / 100000000:.1f}亿")

                st.markdown("---")
                st.markdown("#### 评分权重")

                weights = config.get('weights', {})
                w_labels = {'deviation_score': '乖离率', 'change_score': '涨幅', 'turnover_score': '换手率',
                           'amount_score': '成交额', 'position_score': '价格位置', 'amplitude_score': '振幅'}

                c1, c2, c3 = st.columns(3)
                for i, (k, label) in enumerate(w_labels.items()):
                    col = [c1, c2, c3][i % 3]
                    col.metric(label, f"{weights.get(k, 0)}%")

    # 清理临时状态
    if 'confirm_delete' in st.session_state and st.session_state.confirm_delete not in load_custom_configs():
        del st.session_state.confirm_delete

# ==================== 手动选股页面 ====================
def show_manual_screening():
    """手动选股页面"""
    st.markdown("# 🚀 手动执行选股")

    # 加载所有配置
    all_configs = get_all_configs()

    # 配置选择
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_config = st.selectbox(
            "选择策略配置",
            list(all_configs.keys()),
            index=list(all_configs.keys()).index(st.session_state.get('selected_config', '默认配置'))
        )
        st.session_state.selected_config = selected_config

    # 显示当前配置摘要
    config = all_configs[selected_config]
    with col2:
        st.markdown("**配置描述**")
        st.caption(config.get('description', ''))
    with col3:
        params = config.get('params', {})
        st.markdown("**参数摘要**")
        st.caption(f"市值: {params['MIN_MV']/100000000:.0f}-{params['MAX_MV']/100000000:.0f}亿")
        st.caption(f"涨幅: {params['MIN_PCT']}%-{params['MAX_PCT']}%")

    st.markdown("---")

    st.markdown("""
    ### 执行说明

    点击下方按钮将立即执行选股策略，获取实时选股结果。
    预计执行时间：1-3分钟
    """)

    # 执行按钮
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🚀 开始选股", type="primary", use_container_width=True):
            st.markdown("### ⏳ 正在执行选股...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            # 执行选股
            try:
                status_text.text("📊 正在获取基础股票池...")
                progress_bar.progress(20)

                results, result_file = run_stock_screening_with_config(config)
                progress_bar.progress(50)

                if results is not None:
                    status_text.text("✅ 选股完成！")
                    progress_bar.progress(100)

                    st.success(f"成功选出 {len(results)} 只候选股票")

                    # 显示结果
                    st.markdown("---")
                    st.subheader("📈 选股结果 TOP 10")

                    for i, stock in enumerate(results[:10], 1):
                        score = stock['total_score']
                        score_color = "🟢" if score >= 75 else "🟡" if score >= 70 else "🔴"
                        st.markdown(f"{score_color} **{i}. {stock['name']}** ({stock['code']}) - 评分: {round(score, 1)}")

                else:
                    status_text.text(f"❌ 执行失败: {result_file}")
                    progress_bar.progress(0)
                    st.error(result_file)

            except Exception as e:
                st.error(f"执行出错: {e}")
                import traceback
                st.error(traceback.format_exc())

    st.markdown("---")

    # 最近执行记录
    st.subheader("📋 最近执行记录")

    latest_data, filename = load_latest_result()
    if latest_data:
        col1, col2 = st.columns(2)
        col1.info(f"**上次执行**: {latest_data.get('screening_time', '')}")
        col2.info(f"**选股数量**: {latest_data.get('total_stocks_found', 0)}只")
    else:
        st.warning("暂无执行记录")

def run_stock_screening_with_config(config):
    """使用指定配置执行选股策略"""
    if not CONFIG_AVAILABLE:
        return None, "配置模块未正确加载"

    try:
        import src.config as config_module
        import src.main_force_burial_strategy as strategy_module

        # 保存原始配置
        original_params = config_module.StockScreenerConfig.main_force_burial_params
        original_weights = None

        # 应用自定义配置
        if 'params' in config:
            config_module.StockScreenerConfig.main_force_burial_params = config['params']

        # 创建策略实例
        strategy = strategy_module.MainForceBurialStrategy()

        # 如果有自定义权重，应用权重
        if 'weights' in config:
            strategy.scoring_weights = config['weights']

        # 执行选股
        results = strategy.execute_strategy()

        # 更新结果中的配置信息
        if results:
            for stock in results:
                stock['config_name'] = config.get('name', '默认配置')

        result_file = strategy.save_results()

        # 恢复原始配置
        config_module.StockScreenerConfig.main_force_burial_params = original_params

        return results, result_file
    except Exception as e:
        import traceback
        return None, f"{str(e)}\n{traceback.format_exc()}"

# ==================== 页脚 ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>⚠️ 风险提示：本系统仅供量化研究，不构成投资建议</p>
    <p>股市有风险，投资需谨慎 | 数据来源：Tushare + GuguData</p>
    <p>© 2025 Stock Screener | Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
