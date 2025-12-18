#!/usr/bin/env python3
"""
系统状态监控脚本
显示11:30自动选股系统的运行状态
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
import glob

class SystemStatusMonitor:
    """系统状态监控器"""

    def __init__(self):
        self.project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def check_cron_status(self):
        """检查cron任务状态"""
        print("⏰ 定时任务状态")
        print("-" * 40)

        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                cron_jobs = [line for line in lines if line.strip() and not line.startswith('#')]

                if cron_jobs:
                    for job in cron_jobs:
                        if 'auto_1130_system.py' in job:
                            print("✅ 11:30自动选股任务已安装")
                            print(f"📋 任务详情: {job}")
                            break
                    else:
                        print("❌ 未找到11:30自动选股任务")
                else:
                    print("❌ 未找到任何cron任务")
            else:
                print("❌ 无法获取cron任务列表")

        except Exception as e:
            print(f"❌ 检查cron状态失败: {e}")

    def check_execution_logs(self):
        """检查执行日志"""
        print("\n📊 执行日志分析")
        print("-" * 40)

        log_file = os.path.join(self.project_path, 'results', 'execution_log.json')
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)

                if logs:
                    print(f"📈 总执行次数: {len(logs)}")

                    # 最近执行记录
                    recent_logs = logs[-5:]  # 最近5次
                    print("\n📅 最近执行记录:")
                    for log in reversed(recent_logs):
                        exec_time = log.get('execution_time', '')
                        success = "✅ 成功" if log.get('success') else "❌ 失败"
                        stocks = log.get('stocks_found', 0)
                        email = "📧 已发送" if log.get('email_sent') else "📧 未发送"

                        # 简化时间显示
                        time_str = exec_time.split(' ')[1][:5] if ' ' in exec_time else exec_time

                        print(f"  {time_str} | {success} | 选股{stocks}只 | {email}")

                    # 统计信息
                    total_executions = len(logs)
                    successful_executions = len([log for log in logs if log.get('success')])
                    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
                    avg_stocks = sum(log.get('stocks_found', 0) for log in logs) / total_executions if total_executions > 0 else 0

                    print(f"\n📊 统计信息:")
                    print(f"  成功率: {success_rate:.1f}% ({successful_executions}/{total_executions})")
                    print(f"  平均选股: {avg_stocks:.1f}只/次")

                    # 最近执行时间
                    last_execution = logs[-1].get('execution_time', '')
                    if last_execution:
                        print(f"  最近执行: {last_execution}")
                else:
                    print("📋 暂无执行记录")

            except Exception as e:
                print(f"❌ 读取执行日志失败: {e}")
        else:
            print("📋 暂无执行日志文件")

    def check_result_files(self):
        """检查结果文件"""
        print("\n📁 结果文件状态")
        print("-" * 40)

        # 查找所有结果文件
        result_patterns = [
            "advanced_screening_result_*.json",
            "enhanced_1130_result_*.json",
            "ml_validation_result_*.json",
            "continuous_backtest_report_*.json",
            "integrated_system_report_*.json"
        ]

        file_count = 0
        latest_file = None
        latest_time = None

        for pattern in result_patterns:
            files = glob.glob(os.path.join(self.project_path, pattern))
            file_count += len(files)

            for file in files:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file))
                    if latest_time is None or file_time > latest_time:
                        latest_time = file_time
                        latest_file = os.path.basename(file)
                except:
                    pass

        print(f"📊 结果文件统计:")
        print(f"  总文件数: {file_count}")

        if latest_file:
            print(f"  最新文件: {latest_file}")
            print(f"  更新时间: {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 按类型统计
        print(f"\n📋 文件类型分布:")
        for pattern in result_patterns:
            files = glob.glob(os.path.join(self.project_path, pattern))
            if files:
                file_type = pattern.split('_')[0] + '_' + pattern.split('_')[1]
                print(f"  {file_type}: {len(files)}个")

    def check_system_environment(self):
        """检查系统环境"""
        print("\n🔧 系统环境检查")
        print("-" * 40)

        # 检查虚拟环境
        venv_path = os.path.join(self.project_path, 'venv', 'bin', 'python')
        if os.path.exists(venv_path):
            print("✅ Python虚拟环境正常")
        else:
            print("❌ Python虚拟环境不存在")

        # 检查配置文件
        env_file = os.path.join(self.project_path, '.env')
        if os.path.exists(env_file):
            print("✅ 环境配置文件存在")
        else:
            print("⚠️  环境配置文件不存在")

        # 检查核心脚本
        core_scripts = [
            'scripts/auto_1130_system.py',
            'src/advanced_screening_system.py',
            'src/enhanced_1130_screening.py',
            'integrated_strategy_system.py'
        ]

        missing_scripts = []
        for script in core_scripts:
            if os.path.exists(os.path.join(self.project_path, script)):
                print(f"✅ {script}")
            else:
                print(f"❌ {script}")
                missing_scripts.append(script)

        if missing_scripts:
            print(f"\n⚠️  缺少核心脚本: {len(missing_scripts)}个")

    def show_next_schedule(self):
        """显示下次执行时间"""
        print("\n📅 下次执行计划")
        print("-" * 40)

        now = datetime.now()

        # 计算下一个工作日11:30
        days_ahead = 0
        while True:
            next_date = now + timedelta(days=days_ahead)
            if next_date.weekday() < 5:  # 周一到周五
                next_execution = next_date.replace(hour=11, minute=30, second=0, microsecond=0)
                if next_execution > now:
                    break
            days_ahead += 1

        time_diff = next_execution - now
        hours = time_diff.total_seconds() // 3600
        minutes = (time_diff.total_seconds() % 3600) // 60

        print(f"📅 下次执行时间: {next_execution.strftime('%Y-%m-%d %H:%M')}")
        print(f"⏰ 距离执行: {int(hours)}小时{int(minutes)}分钟")
        print(f"📝 执行内容: 高级多维度选股分析")
        print(f"📧 推送方式: 邮件通知")

    def display_status_report(self):
        """显示完整状态报告"""
        print("🚀 11:30自动选股系统状态报告")
        print("=" * 60)
        print(f"报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"系统版本: v4.0_integrated")
        print()

        self.check_cron_status()
        self.check_execution_logs()
        self.check_result_files()
        self.check_system_environment()
        self.show_next_schedule()

        print("\n" + "=" * 60)
        print("💡 快速操作指南:")
        print("  • 手动执行选股: ./run_1130_screening.sh")
        print("  • 查看实时日志: tail -f cron_1130.log")
        print("  • 管理定时任务: crontab -e")
        print("  • 运行集成系统: python integrated_strategy_system.py")
        print("  • 系统状态检查: python scripts/system_status.py")

def main():
    """主函数"""
    monitor = SystemStatusMonitor()
    monitor.display_status_report()

if __name__ == "__main__":
    main()