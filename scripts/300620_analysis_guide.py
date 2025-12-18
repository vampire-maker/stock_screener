#!/usr/bin/env python3
"""
300620光库科技分析指导
由于API限制，提供实时数据获取方法和分析框架
"""

import os
import json
from datetime import datetime

class StockAnalysisGuide:
    """股票分析指导器"""

    def __init__(self):
        self.stock_code = "300620"
        self.stock_name = "光库科技"
        self.industry = "光电子器件制造"

    def show_company_profile(self):
        """显示公司概况"""
        print("🏢 公司概况")
        print("=" * 50)
        print(f"公司名称: {self.stock_name}")
        print(f"股票代码: {self.stock_code}")
        print(f"所属行业: {self.industry}")
        print()
        print("📋 主营业务:")
        print("  • 光纤器件的研发、生产和销售")
        print("  • 光通信器件制造")
        print("  • 激光器件产品")
        print()
        print("🏆 竞争优势:")
        print("  • 技术研发实力强")
        print("  • 产品应用领域广泛")
        print("  • 在光通信领域有一定地位")
        print("  • 客户资源相对稳定")

    def show_industry_analysis(self):
        """显示行业分析"""
        print("\n🌍 行业分析")
        print("=" * 50)
        print("📈 行业前景:")
        print("  • 5G建设持续拉动光通信需求")
        print("  • 数据中心建设需求增长")
        print("  • 算力网络发展带来新机遇")
        print("  • 新能源汽车带动相关需求")
        print()
        print("⚡ 行业热点:")
        print("  • 光模块市场景气度提升")
        print("  • CPO技术发展趋势")
        print("  • 硅光子技术突破")
        print("  • 国产化替代加速")
        print()
        print("🏛️ 政策支持:")
        print("  • 数字经济政策持续发力")
        print("  • 新基建投资增加")
        print("  • 科技创新政策支持")

    def show_technical_analysis_framework(self):
        """显示技术分析框架"""
        print("\n📊 技术分析框架")
        print("=" * 50)
        print("🎯 关键技术指标:")
        print("  • 均线系统: MA5, MA10, MA20, MA60")
        print("  • 成交量分析: 量比、换手率")
        print("  • 技术指标: MACD, RSI, KDJ")
        print("  • 价格位置: 相对高低点位置")
        print()
        print("🔍 关键价格位:")
        print("  • 近期支撑位和压力位")
        print("  • 重要均线位置")
        print("  • 前期高低点参考")
        print()
        print("📈 走势判断:")
        print("  • 价格是否站上重要均线")
        print("  • 成交量是否配合")
        print("  • 技术指标信号")

    def show_fundamental_analysis_framework(self):
        """显示基本面分析框架"""
        print("\n💰 基本面分析框架")
        print("=" * 50)
        print("📊 财务指标:")
        print("  • 市盈率 (PE)")
        print("  • 市净率 (PB)")
        print("  • 净资产收益率 (ROE)")
        print("  • 营收增长率")
        print("  • 净利润增长率")
        print("  • 资产负债率")
        print()
        print("🏭 经营指标:")
        print("  • 主营业务收入")
        print("  • 毛利率")
        print("  • 研发投入占比")
        print("  • 客户集中度")
        print("  • 产品毛利率")

    def show_risk_management(self):
        """显示风险管理"""
        print("\n⚠️ 风险管理")
        print("=" * 50)
        print("🎯 操作风险:")
        print("  • 设置止损位: 建议亏损5-8%止损")
        print("  • 设置止盈位: 根据目标收益率设定")
        print("  • 仓位控制: 单股不超过总资金20%")
        print("  • 分批建仓: 避免一次性全部买入")
        print()
        print("🌊 市场风险:")
        print("  • 大盘波动风险")
        print("  • 行业周期风险")
        print("  • 政策变化风险")
        print("  • 国际贸易风险")
        print()
        print("🏢 公司风险:")
        print("  • 技术更新迭代风险")
        print("  • 客户集中度风险")
        print("  • 原材料价格波动风险")
        print("  • 竞争加剧风险")

    def show_trading_strategy(self):
        """显示交易策略"""
        print("\n💡 交易策略建议")
        print("=" * 50)
        print("🎯 选股时机:")
        print("  • 技术面突破重要均线")
        print("  • 成交量放大配合")
        print("  • 行业景气度提升期")
        print("  • 公司业绩发布前后")
        print()
        print("📈 持仓策略:")
        print("  • 短线: 1-3个交易日")
        print("  • 中线: 1-4周")
        print("  • 长线: 3-6个月")
        print()
        print("💰 仓位管理:")
        print("  • 初次建仓: 不超过10%")
        print("  • 加仓时机: 回调确认支撑时")
        print("  • 减仓时机: 快速上涨后")
        print("  • 清仓条件: 破位重要支撑")

    def show_data_sources(self):
        """显示数据来源"""
        print("\n📊 实时数据获取渠道")
        print("=" * 50)
        print("🌐 免费数据源:")
        print("  1. 新浪财经 (finance.sina.com.cn)")
        print("  2. 东方财富网 (eastmoney.com)")
        print("  3. 腾讯证券 (gu.qq.com)")
        print("  4. 雪球网 (xueqiu.com)")
        print("  5. 同花顺 (10jqka.com.cn)")
        print()
        print("💻 专业软件:")
        print("  1. 同花顺软件")
        print("  2. 大智慧软件")
        print("  3. 通达信软件")
        print("  4. 文华财经软件")
        print()
        print("📱 手机APP:")
        print("  1. 同花顺APP")
        print("  2. 东方财富APP")
        print("  3. 雪球APP")
        print("  4. 腾讯自选股")

    def generate_monitoring_checklist(self):
        """生成监控清单"""
        print("\n📋 每日监控清单")
        print("=" * 50)
        print("✅ 价格监控:")
        print("  □ 开盘价格和开盘涨幅")
        print("  □ 当前价格和涨跌幅")
        print("  □ 成交量和换手率")
        print("  □ 分时走势图形态")
        print()
        print("✅ 技术指标:")
        print("  □ 均线系统状态")
        print("  □ MACD指标信号")
        print("  □ RSI指标位置")
        print("  □ 成交量配合度")
        print()
        print("✅ 资金面:")
        print("  □ 主力资金流向")
        print("  □ 北向资金动向")
        print("  □ 机构持仓变化")
        print("  □ 融资融券数据")
        print()
        print("✅ 基本面:")
        print("  □ 行业新闻和动态")
        print("  □ 公司公告信息")
        print("  □ 相关政策变化")
        print("  □ 竞争对手表现")

    def save_analysis_template(self):
        """保存分析模板"""
        template = {
            "stock_info": {
                "code": self.stock_code,
                "name": self.stock_name,
                "industry": self.industry,
                "analysis_date": datetime.now().strftime('%Y-%m-%d')
            },
            "daily_monitoring": {
                "price": {
                    "open": 0,
                    "high": 0,
                    "low": 0,
                    "current": 0,
                    "change": 0,
                    "change_percent": 0
                },
                "volume": {
                    "total_volume": 0,
                    "turnover_rate": 0,
                    "volume_ratio": 0
                },
                "technical": {
                    "ma5": 0,
                    "ma10": 0,
                    "ma20": 0,
                    "ma60": 0,
                    "macd": {"dif": 0, "dea": 0, "histogram": 0},
                    "rsi": 0,
                    "kdj": {"k": 0, "d": 0, "j": 0}
                }
            },
            "analysis_notes": "",
            "trading_plan": {
                "strategy": "",
                "position_size": 0,
                "entry_price": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "holding_period": ""
            }
        }

        filename = f"300620_analysis_template_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)

        print(f"\n💾 分析模板已保存: {filename}")
        return filename

    def run_complete_guide(self):
        """运行完整指导"""
        print("🚀 300620光库科技投资分析指导")
        print("=" * 60)
        print(f"指导时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self.show_company_profile()
        self.show_industry_analysis()
        self.show_technical_analysis_framework()
        self.show_fundamental_analysis_framework()
        self.show_risk_management()
        self.show_trading_strategy()
        self.show_data_sources()
        self.generate_monitoring_checklist()
        self.save_analysis_template()

        print("\n" + "=" * 60)
        print("🎯 分析总结:")
        print("  1. 光库科技属于光通信行业，行业前景良好")
        print("  2. 技术面需要关注均线系统和成交量配合")
        print("  3. 基本面需要关注财务指标和业绩增长")
        print("  4. 风险控制是投资成功的关键")
        print("  5. 建议多渠道获取实时数据")
        print("  6. 保持理性投资，不要盲目追涨杀跌")
        print()
        print("⚠️ 重要提醒:")
        print("  • 本指导仅供参考，不构成投资建议")
        print("  • 投资有风险，入市需谨慎")
        print("  • 请结合自身情况做出投资决策")
        print("  • 建议咨询专业投资顾问")

def main():
    """主函数"""
    guide = StockAnalysisGuide()
    guide.run_complete_guide()

if __name__ == "__main__":
    main()