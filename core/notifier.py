"""
消息推送模块
"""
import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, List
from config import StockScreenerConfig, WECHAT_CONFIG, EMAIL_CONFIG

class StockNotifier:
    def __init__(self):
        self.config = StockScreenerConfig()
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.config.OUTPUT_DIR):
            os.makedirs(self.config.OUTPUT_DIR)

    def console_notify(self, message: str, df: pd.DataFrame):
        """控制台输出通知"""
        print("=" * 60)
        print("📈 A股选股结果")
        print("=" * 60)
        print(message)

        if not df.empty:
            print(f"\n📊 详细股票列表:")
            print("-" * 60)
            for idx, row in df.iterrows():
                print(f"{idx+1:2d}. {row['名称']}({row['代码']}) | "
                      f"涨幅:{row['涨跌幅']:+6.2f}% | "
                      f"换手:{row['换手率']:5.2f}% | "
                      f"量比:{row['量比']:.2f} | "
                      f"市值:{row['总市值']:6.0f}亿")
        print("=" * 60)

    def save_to_file(self, message: str, df: pd.DataFrame, filename: str = None):
        """保存到文件"""
        if filename is None:
            filename = f"stock_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 保存为JSON格式
        json_file = os.path.join(self.config.OUTPUT_DIR, f"{filename}.json")
        result_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": message,
            "count": len(df),
            "stocks": df.to_dict('records') if not df.empty else []
        }

        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {json_file}")
        except Exception as e:
            print(f"保存JSON文件失败: {e}")

        # 保存为Excel格式
        if not df.empty:
            excel_file = os.path.join(self.config.OUTPUT_DIR, f"{filename}.xlsx")
            try:
                df.to_excel(excel_file, index=False, engine='openpyxl')
                print(f"结果已保存到: {excel_file}")
            except Exception as e:
                print(f"保存Excel文件失败: {e}")

        # 保存纯文本格式
        txt_file = os.path.join(self.config.OUTPUT_DIR, f"{filename}.txt")
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(message)
                f.write("\n\n详细数据:\n")
                f.write(df.to_string(index=False))
            print(f"结果已保存到: {txt_file}")
        except Exception as e:
            print(f"保存文本文件失败: {e}")

    def send_wechat_notification(self, message: str, df: pd.DataFrame):
        """发送企业微信通知"""
        if not WECHAT_CONFIG.get("enabled") or not WECHAT_CONFIG.get("webhook_url"):
            print("企业微信推送未配置，跳过微信通知")
            return

        try:
            import requests

            # 构造消息内容
            if df.empty:
                content = {
                    "msgtype": "text",
                    "text": {
                        "content": f"📈 A股选股结果\n\n{message}\n\n今日未找到符合条件的股票，继续关注市场动态。"
                    }
                }
            else:
                # 构造格式化的股票列表
                stock_list = []
                for idx, row in df.iterrows():
                    stock_info = f"{idx+1}. {row['名称']}({row['代码']})\n" \
                               f"   涨幅: {row['涨跌幅']:+.2f}% | 换手: {row['换手率']:.2f}% | 量比: {row['量比']:.2f}"
                    stock_list.append(stock_info)

                content = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": f"""## 📈 A股选股结果

**筛选时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**选出股票**: {len(df)} 只

**股票列表**:

{chr(10).join(stock_list)}

---
*由A股智能选股系统自动生成*
"""
                    }
                }

            # 发送请求
            response = requests.post(
                WECHAT_CONFIG["webhook_url"],
                json=content,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    print("✅ 微信推送成功")
                else:
                    print(f"❌ 微信推送失败: {result.get('errmsg', '未知错误')}")
            else:
                print(f"❌ 微信推送请求失败: {response.status_code}")

        except Exception as e:
            print(f"❌ 微信推送异常: {e}")

    def send_email_notification(self, message: str, df: pd.DataFrame):
        """发送邮件通知"""
        try:
            from email_sender import EmailSender

            with EmailSender() as email_sender:
                # 生成邮件主题
                subject = EMAIL_CONFIG.get("subject_template", "A股选股结果").format(
                    date=datetime.now().strftime('%Y-%m-%d'),
                    count=len(df)
                )

                success = email_sender.send_email(subject, message, df)
                if success:
                    print("✅ 邮件推送成功")
                else:
                    print("❌ 邮件推送失败")

        except Exception as e:
            print(f"❌ 邮件推送异常: {e}")

    def send_test_email(self):
        """发送测试邮件"""
        try:
            from email_sender import EmailSender

            with EmailSender() as email_sender:
                return email_sender.send_test_email()

        except Exception as e:
            print(f"❌ 发送测试邮件失败: {e}")
            return False

    def notify(self, message: str, df: pd.DataFrame, push_types: List[str] = None):
        """统一推送接口"""
        if push_types is None:
            push_types = self.config.PUSH_TYPES

        print(f"\n📢 开始推送选股结果 (推送方式: {', '.join(push_types)})")

        for push_type in push_types:
            try:
                if push_type == "console":
                    self.console_notify(message, df)
                elif push_type == "file":
                    self.save_to_file(message, df)
                elif push_type == "wechat":
                    self.send_wechat_notification(message, df)
                elif push_type == "email":
                    self.send_email_notification(message, df)
                else:
                    print(f"未知的推送方式: {push_type}")

            except Exception as e:
                print(f"推送方式 {push_type} 执行失败: {e}")

        print("📢 推送完成\n")

    def get_latest_results(self, limit: int = 10) -> List[Dict]:
        """获取最近的选股结果"""
        try:
            result_files = []
            for file in os.listdir(self.config.OUTPUT_DIR):
                if file.endswith('.json'):
                    file_path = os.path.join(self.config.OUTPUT_DIR, file)
                    result_files.append((os.path.getmtime(file_path), file_path))

            # 按修改时间排序，获取最新的
            result_files.sort(reverse=True, key=lambda x: x[0])

            latest_results = []
            for _, file_path in result_files[:limit]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                        latest_results.append(result)
                except Exception as e:
                    print(f"读取结果文件失败 {file_path}: {e}")

            return latest_results

        except Exception as e:
            print(f"获取历史结果失败: {e}")
            return []

    def generate_statistics_report(self) -> str:
        """生成统计报告"""
        try:
            latest_results = self.get_latest_results(30)  # 获取最近30次结果

            if not latest_results:
                return "暂无历史选股数据"

            total_screens = len(latest_results)
            total_stocks = sum(result.get("count", 0) for result in latest_results)
            avg_stocks_per_screen = total_stocks / total_screens if total_screens > 0 else 0

            # 统计出现频率最高的股票
            stock_frequency = {}
            for result in latest_results:
                for stock in result.get("stocks", []):
                    symbol = stock.get("代码", "")
                    name = stock.get("名称", "")
                    key = f"{name}({symbol})"
                    stock_frequency[key] = stock_frequency.get(key, 0) + 1

            # 获取出现次数最多的前10只股票
            top_stocks = sorted(stock_frequency.items(),
                              key=lambda x: x[1], reverse=True)[:10]

            report = f"""
=== 选股统计报告 ===
统计周期: 最近 {total_screens} 次选股
选股时间: {latest_results[-1].get('timestamp', 'N/A')} 至 {latest_results[0].get('timestamp', 'N/A')}

统计数据:
- 总选股次数: {total_screens}
- 总选出股票: {total_stocks} 只
- 平均每次选出: {avg_stocks_per_screen:.1f} 只

高频股票 (最近30次中出现次数最多):
"""
            for idx, (stock_name, frequency) in enumerate(top_stocks, 1):
                report += f"{idx:2d}. {stock_name}: {frequency} 次\n"

            return report

        except Exception as e:
            return f"生成统计报告失败: {e}"