#!/usr/bin/env python3
"""
Cron定时任务设置器
配置11:30和14:30自动选股定时任务
"""

import os
import subprocess
from datetime import datetime

class DualCronSchedulerSetup:
    """双时段Cron调度器设置"""

    def __init__(self):
        self.project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.python_path = os.path.join(self.project_path, 'venv', 'bin', 'python')

        # 11:30配置
        self.scripts_1130 = os.path.join(self.project_path, 'scripts', 'auto_1130_system.py')
        self.log_file_1130 = os.path.join(self.project_path, 'cron_1130.log')

        # 14:30配置
        self.scripts_1430 = os.path.join(self.project_path, 'scripts', 'auto_1430_system.py')
        self.log_file_1430 = os.path.join(self.project_path, 'cron_1430.log')

    def check_requirements(self):
        """检查运行环境"""
        print("🔍 检查运行环境...")

        # 检查Python路径
        if not os.path.exists(self.python_path):
            print(f"❌ Python虚拟环境不存在: {self.python_path}")
            return False

        # 检查脚本文件
        scripts_to_check = [
            (self.scripts_1130, "11:30选股脚本"),
            (self.scripts_1430, "14:30选股脚本")
        ]

        for script_path, script_name in scripts_to_check:
            if not os.path.exists(script_path):
                print(f"❌ {script_name}不存在: {script_path}")
                return False

        # 检查当前目录
        if not os.path.exists(os.path.join(self.project_path, '.env')):
            print("⚠️  .env文件不存在，邮件功能可能无法正常工作")

        print("✅ 环境检查通过")
        return True

    def create_cron_jobs(self):
        """创建双时段cron任务"""
        print("⏰ 创建双时段定时任务...")

        # 11:30任务
        cron_command_1130 = f"{self.python_path} {self.scripts_1130}"
        log_command_1130 = f">> {self.log_file_1130} 2>&1"
        full_command_1130 = f"{cron_command_1130} {log_command_1130}"
        cron_entry_1130 = f"30 11 * * 1-5 cd {self.project_path} && {full_command_1130}"

        # 14:30任务
        cron_command_1430 = f"{self.python_path} {self.scripts_1430}"
        log_command_1430 = f">> {self.log_file_1430} 2>&1"
        full_command_1430 = f"{cron_command_1430} {log_command_1430}"
        cron_entry_1430 = f"30 14 * * 1-5 cd {self.project_path} && {full_command_1430}"

        print(f"📋 Cron任务内容:")
        print(f"\n🟢 11:30选股任务:")
        print(f"   时间: 每天11:30 (工作日)")
        print(f"   命令: {cron_command_1130}")
        print(f"   日志: {self.log_file_1130}")
        print(f"   完整命令: {cron_entry_1130}")

        print(f"\n🟡 14:30选股任务:")
        print(f"   时间: 每天14:30 (工作日)")
        print(f"   命令: {cron_command_1430}")
        print(f"   日志: {self.log_file_1430}")
        print(f"   完整命令: {cron_entry_1430}")

        return [cron_entry_1130, cron_entry_1430]

    def install_cron_job(self, cron_entry):
        """安装cron任务"""
        try:
            print("📦 安装cron任务...")

            # 获取当前的crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""

            # 检查是否已经存在相同任务
            if 'auto_1130_system.py' in current_cron:
                print("⚠️  检测到已存在的11:30选股任务")
                choice = input("是否要替换现有任务? (y/n): ").lower().strip()
                if choice != 'y':
                    print("❌ 取消安装")
                    return False

                # 移除现有任务
                lines = current_cron.split('\n')
                filtered_lines = [line for line in lines if 'auto_1130_system.py' not in line]
                current_cron = '\n'.join(filtered_lines)

            # 添加新任务
            new_cron = current_cron.rstrip() + '\n' + cron_entry + '\n'

            # 写入临时文件
            temp_file = '/tmp/cron_temp.txt'
            with open(temp_file, 'w') as f:
                f.write(new_cron)

            # 安装新的crontab
            subprocess.run(['crontab', temp_file], check=True)

            # 清理临时文件
            os.remove(temp_file)

            print("✅ Cron任务安装成功！")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Cron任务安装失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 安装过程中发生错误: {e}")
            return False

    def verify_cron_job(self):
        """验证cron任务安装"""
        try:
            print("🔍 验证cron任务...")

            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0 and 'auto_1130_system.py' in result.stdout:
                print("✅ Cron任务验证成功！")

                # 显示当前的相关任务
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'auto_1130_system.py' in line:
                        print(f"📋 已安装任务: {line}")

                return True
            else:
                print("❌ Cron任务验证失败")
                return False

        except Exception as e:
            print(f"❌ 验证过程中发生错误: {e}")
            return False

    def create_manual_run_script(self):
        """创建手动运行脚本"""
        print("📝 创建手动运行脚本...")

        script_content = f"""#!/bin/bash

# 11:30自动选股手动运行脚本
echo "🚀 手动执行11:30自动选股..."
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"

cd "{self.project_path}"

# 激活虚拟环境并运行
source venv/bin/activate
python scripts/auto_1130_system.py

echo "✅ 执行完成！时间: $(date '+%Y-%m-%d %H:%M:%S')"
"""

        script_path = os.path.join(self.project_path, 'run_1130_screening.sh')
        with open(script_path, 'w') as f:
            f.write(script_content)

        # 设置执行权限
        os.chmod(script_path, 0o755)

        print(f"✅ 手动运行脚本创建完成: {script_path}")
        print("💡 使用方法: ./run_1130_screening.sh")

    def show_status(self):
        """显示当前状态"""
        print("\n📊 系统状态信息")
        print("=" * 50)
        print(f"项目路径: {self.project_path}")
        print(f"Python路径: {self.python_path}")
        print(f"选股脚本: {self.script_path}")
        print(f"日志文件: {self.log_file}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查cron服务状态
        try:
            result = subprocess.run(['cronjob', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Cron服务正常运行")
            else:
                print("⚠️  请检查cron服务状态")
        except:
            # 尝试其他方式检查cron
            try:
                subprocess.run(['crontab', '-l'], capture_output=True, check=True)
                print("✅ Cron服务可用")
            except:
                print("⚠️  Cron服务可能未运行")

    def setup_scheduler(self):
        """设置完整的调度系统"""
        print("🚀 11:30自动选股定时器设置")
        print("=" * 60)
        print(f"设置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 检查环境
        if not self.check_requirements():
            return False

        # 显示状态
        self.show_status()

        # 创建cron任务
        cron_entry = self.create_cron_job()

        # 安装cron任务
        if not self.install_cron_job(cron_entry):
            return False

        # 验证安装
        if not self.verify_cron_job():
            return False

        # 创建手动运行脚本
        self.create_manual_run_script()

        print("\n🎉 定时器设置完成！")
        print("=" * 50)
        print("📅 自动执行计划:")
        print("   • 工作日 11:30 自动执行选股")
        print("   • 自动发送邮件通知")
        print("   • 自动记录执行日志")
        print()
        print("🔧 管理命令:")
        print("   • 查看当前任务: crontab -l")
        print("   • 编辑任务: crontab -e")
        print("   • 删除任务: crontab -r (谨慎使用)")
        print("   • 手动执行: ./run_1130_screening.sh")
        print("   • 查看日志: tail -f cron_1130.log")
        print()
        print("⚠️  注意事项:")
        print("   • 确保计算机在11:30时处于开机状态")
        print("   • 确保网络连接正常")
        print("   • 确保邮件配置正确")
        print("   • 建议定期检查执行日志")

        return True

def main():
    """主函数"""
    setup = CronSchedulerSetup()
    success = setup.setup_scheduler()

    if success:
        print("\n✅ 定时器设置成功！系统将在工作日11:30自动执行选股。")
        print("💡 建议立即运行一次测试: python scripts/auto_1130_system.py")
    else:
        print("\n❌ 定时器设置失败，请检查错误信息并重试。")

if __name__ == "__main__":
    main()