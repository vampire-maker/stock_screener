"""
邮件发送模块
支持SMTP邮件发送，支持HTML格式和附件
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from datetime import datetime
import pandas as pd
from src.config import StockScreenerConfig

class EmailSender:
    def __init__(self):
        config_obj = StockScreenerConfig()
        self.config = config_obj.email_config
        self.smtp_server = None
        self._connect_smtp()

    def _connect_smtp(self):
        """连接SMTP服务器"""
        if not self.config.get("enabled"):
            return False

        try:
            # 根据端口选择连接方式
            if self.config.get("smtp_port", 587) == 587:
                # 587端口使用STARTTLS
                self.smtp_server = smtplib.SMTP(
                    self.config["smtp_server"],
                    self.config["smtp_port"]
                )
                self.smtp_server.starttls()
            elif self.config.get("smtp_port", 465) == 465:
                # 465端口使用SSL
                self.smtp_server = smtplib.SMTP_SSL(
                    self.config["smtp_server"],
                    self.config["smtp_port"]
                )
            else:
                # 其他端口使用普通连接
                self.smtp_server = smtplib.SMTP(
                    self.config["smtp_server"],
                    self.config["smtp_port"]
                )

            # 登录邮箱
            self.smtp_server.login(
                self.config["sender_email"],
                self.config["sender_password"]
            )

            print("✅ SMTP服务器连接成功")
            return True

        except Exception as e:
            print(f"❌ SMTP服务器连接失败: {e}")
            self.smtp_server = None
            return False

    def _create_html_content(self, message: str, df: pd.DataFrame) -> str:
        """创建HTML格式的邮件内容"""
        if df.empty:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .content {{ margin: 20px 0; }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
                    .no-stocks {{ color: #ff6b6b; font-size: 16px; text-align: center; margin: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📈 A股智能选股系统</h2>
                    <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="content">
                    <pre>{message}</pre>
                    <div class="no-stocks">⚠️ 今日未找到符合条件的股票</div>
                </div>
                <div class="footer">
                    <p>本邮件由A股智能选股系统自动发送</p>
                    <p>如有疑问，请联系系统管理员</p>
                </div>
            </body>
            </html>
            """
        else:
            # 创建股票列表表格
            table_rows = ""
            for idx, row in df.iterrows():
                change_color = "#28a745" if row['涨跌幅'] > 0 else "#dc3545"
                table_rows += f"""
                <tr>
                    <td>{idx+1}</td>
                    <td><strong>{row['名称']}</strong><br><small>{row['代码']}</small></td>
                    <td style="color: {change_color}; font-weight: bold;">{row['涨跌幅']:+.2f}%</td>
                    <td>{row['换手率']:.2f}%</td>
                    <td>{row['量比']:.2f}</td>
                    <td>{row['总市值']:.0f}亿</td>
                </tr>
                """

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .content {{ margin: 20px 0; }}
                    .stock-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    .stock-table th, .stock-table td {{
                        border: 1px solid #ddd; padding: 12px; text-align: center;
                    }}
                    .stock-table th {{ background-color: #007bff; color: white; font-weight: bold; }}
                    .stock-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .stock-table tr:hover {{ background-color: #f5f5f5; }}
                    .summary {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ color: #666; font-size: 12px; margin-top: 30px; }}
                    .positive {{ color: #28a745; }}
                    .negative {{ color: #dc3545; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📈 A股智能选股结果</h2>
                    <p>筛选时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <div class="summary">
                    <h3>📊 今日筛选结果</h3>
                    <p><strong>选出股票数量:</strong> {len(df)} 只</p>
                    <p><strong>平均涨幅:</strong> {df['涨跌幅'].mean():+.2f}%</p>
                    <p><strong>最大涨幅:</strong> {df['涨跌幅'].max():+.2f}%</p>
                    <p><strong>平均换手率:</strong> {df['换手率'].mean():.2f}%</p>
                </div>

                <div class="content">
                    <h3>🔍 主力埋伏策略v3.1选股规则 (平衡优化版)</h3>
                    <ul>
                        <li><strong>涨幅区间:</strong> 1.0% - 9.0% (适度放宽)</li>
                        <li><strong>市值区间:</strong> 30亿 - 500亿</li>
                        <li><strong>成交额门槛:</strong> ≥ 2000万 (适度降低)</li>
                        <li><strong>换手率分层 (严格):</strong></li>
                        <li>&nbsp;&nbsp;&nbsp;• 小盘股(30-100亿): 3.0% - 11.0% (保持严格)</li>
                        <li>&nbsp;&nbsp;&nbsp;• 中盘股(100-300亿): 2.0% - 9.0% (保持严格)</li>
                        <li>&nbsp;&nbsp;&nbsp;• 大盘股(300-500亿): 1.5% - 7.0% (保持严格)</li>
                        <li><strong>价格形态:</strong> 现价 &gt; VWAP 均价线</li>
                        <li><strong>阳线形态:</strong> 真阳线 (现价 &gt; 开盘价)</li>
                        <li><strong>乖离控制:</strong> 乖离率 ≤ 4.0% (适度放宽)</li>
                    </ul>

                    <h3>📋 股票详细列表</h3>
                    <table class="stock-table">
                        <thead>
                            <tr>
                                <th>序号</th>
                                <th>股票名称</th>
                                <th>涨跌幅</th>
                                <th>换手率</th>
                                <th>量比</th>
                                <th>市值(亿)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>

                <div class="footer">
                    <p><strong>风险提示:</strong> 本选股结果仅供学习参考，不构成投资建议。股市有风险，投资需谨慎。</p>
                    <p>本邮件由A股智能选股系统自动发送 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """
        return html_content

    def _create_attachment(self, df: pd.DataFrame, filename: str = None) -> MIMEApplication:
        """创建Excel附件"""
        if filename is None:
            filename = f"选股结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # 保存为临时文件
        temp_file = os.path.join("results", filename)
        df.to_excel(temp_file, index=False, engine='openpyxl')

        # 读取文件并创建附件
        with open(temp_file, 'rb') as f:
            attachment = MIMEApplication(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)

        # 删除临时文件
        try:
            os.remove(temp_file)
        except:
            pass

        return attachment

    def send_email(self, subject: str, message: str, df: pd.DataFrame):
        """发送邮件"""
        if not self.config.get("enabled"):
            print("邮件推送未启用")
            return False

        if not self.smtp_server:
            print("SMTP服务器未连接")
            return False

        if not self.config.get("recipients"):
            print("未配置收件人邮箱")
            return False

        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')

            # 设置邮件头
            sender_name = self.config.get("sender_name", "A股选股系统")
            sender_email = self.config["sender_email"]
            # QQ邮箱要求发件人格式严格，去掉显示名称
            msg['From'] = sender_email
            msg['To'] = ", ".join(self.config["recipients"])
            msg['Subject'] = Header(subject, 'utf-8')

            # 添加纯文本内容
            text_content = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_content)

            # 添加HTML内容（如果启用）
            if self.config.get("include_html", True):
                html_content = self._create_html_content(message, df)
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)

            # 添加Excel附件（如果启用且有数据）
            if self.config.get("attach_excel", True) and not df.empty:
                attachment = self._create_attachment(df)
                msg.attach(attachment)

            # 发送邮件
            text = msg.as_string()
            self.smtp_server.sendmail(sender_email, self.config["recipients"], text)

            print(f"✅ 邮件发送成功: {self.config['recipients']}")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    def send_test_email(self):
        """发送测试邮件"""
        test_subject = "A股选股系统 - 测试邮件"
        test_message = """
这是一封测试邮件，用于验证邮件配置是否正确。

如果您收到这封邮件，说明邮件推送功能已正常工作。

A股选股系统将在交易日14:30自动执行选股，并发送结果到您的邮箱。

祝您投资顺利！
"""

        # 创建测试数据
        test_df = pd.DataFrame({
            '代码': ['000001', '000002'],
            '名称': ['平安银行', '万科A'],
            '涨跌幅': [3.5, 4.2],
            '换手率': [6.5, 7.8],
            '量比': [1.2, 1.5],
            '总市值': [180, 120]
        })

        return self.send_email(test_subject, test_message, test_df)

    def close(self):
        """关闭SMTP连接"""
        if self.smtp_server:
            try:
                self.smtp_server.quit()
                print("SMTP连接已关闭")
            except:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()