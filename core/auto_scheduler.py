#!/usr/bin/env python3
"""
自动定时调度器
不依赖APScheduler，使用原生Python实现定时任务
"""

import json
import time
from datetime import datetime, timedelta, date
import os
import logging
import subprocess
import signal
import sys
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
def load_env():
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

class AutoScheduler:
    """自动调度器"""

    def __init__(self):
        self.running = True
        self.last_executed = {
            '11:30': None,
            '14:30': None,
            '14:50': None
        }

        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，准备关闭调度器...")
        self.running = False

    def should_execute_task(self, current_time, target_hour, target_minute):
        """检查是否应该执行任务"""
        target_time = datetime(
            current_time.year, current_time.month, current_time.day,
            target_hour, target_minute, 0, 0
        )

        # 检查是否在目标时间的1分钟窗口内
        window_start = target_time
        window_end = target_time + timedelta(minutes=1)

        # 检查今天是否已经执行过
        task_key = f"{target_hour:02d}:{target_minute:02d}"
        today = current_time.date()

        return (window_start <= current_time <= window_end and
                self.last_executed[task_key] != today)

    def execute_stock_screening(self, timeframe='11:30'):
        """执行股票筛选"""
        try:
            logger.info(f"开始执行{timeframe}股票筛选任务...")
            start_time = datetime.now()

            # 设置环境变量
            env = os.environ.copy()
            env.update({
                'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.qq.com'),
                'SMTP_PORT': os.getenv('SMTP_PORT', '587'),
                'SENDER_EMAIL': os.getenv('SENDER_EMAIL', ''),
                'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD', ''),
                'RECEIVER_EMAIL': os.getenv('RECEIVER_EMAIL', ''),
                'TIMEFRAME': timeframe  # 添加时间段标识
            })

            # 根据时间段执行不同的选股脚本
            if timeframe == '14:30':
                # 执行快刀手晚进早出策略v2.0
                script_path = 'src/quick_knife_strategy.py'
                logger.info("使用快刀手晚进早出策略v2.0 (涨幅2.8-4.5%, 量比1.0-1.6, 换手率U型分布)")
            elif timeframe == '14:50':
                # 执行14:50主力埋伏策略v4.1 (优化评分版)
                script_path = 'src/main_force_burial_strategy.py'
                logger.info("使用主力埋伏策略v4.1 (优化评分版 - 精选TOP 10)")
            else:
                # 执行11:30自适应主力埋伏策略
                script_path = 'adaptive_main_force_strategy.py'
                logger.info("使用自适应主力埋伏策略 (判断交易时段，自动选择数据源)")

            # 执行选股脚本
            result = subprocess.run(
                ['python3', script_path],
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            execution_time = datetime.now() - start_time

            if result.returncode == 0:
                logger.info(f"股票筛选执行成功，耗时: {execution_time.total_seconds():.2f}秒")
                logger.info(f"输出: {result.stdout}")
            else:
                logger.error(f"股票筛选执行失败，返回码: {result.returncode}")
                logger.error(f"错误输出: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("股票筛选执行超时（5分钟）")
        except Exception as e:
            logger.error(f"执行股票筛选时发生错误: {e}")

    def check_and_execute_tasks(self):
        """检查并执行任务"""
        current_time = datetime.now()
        current_date = current_time.date()

        # 检查11:30任务
        if self.should_execute_task(current_time, 11, 30):
            task_key = '11:30'
            if self.last_executed[task_key] != current_date:
                logger.info("执行11:30股票筛选任务...")
                self.execute_stock_screening('11:30')
                self.last_executed[task_key] = current_date

        # 检查14:30任务 - 快刀手晚进早出策略
        elif self.should_execute_task(current_time, 14, 30):
            task_key = '14:30'
            if self.last_executed[task_key] != current_date:
                logger.info("执行14:30快刀手晚进早出策略任务...")
                self.execute_stock_screening('14:30')
                self.last_executed[task_key] = current_date

        # 检查14:50任务
        elif self.should_execute_task(current_time, 14, 50):
            task_key = '14:50'
            if self.last_executed[task_key] != current_date:
                logger.info("执行14:50尾盘主力埋伏任务（优化评分版）...")
                self.execute_stock_screening('14:50')
                self.last_executed[task_key] = current_date

    def get_next_task_time(self):
        """获取下次任务时间"""
        current_time = datetime.now()
        current_date = current_time.date()

        # 今天的任务时间
        task1 = datetime(
            current_time.year, current_time.month, current_time.day,
            11, 30, 0, 0
        )
        task2 = datetime(
            current_time.year, current_time.month, current_time.day,
            14, 30, 0, 0
        )
        task3 = datetime(
            current_time.year, current_time.month, current_time.day,
            14, 50, 0, 0
        )
        today_tasks = [task1, task2, task3]

        # 找到下一个未执行的任务
        for task_time in today_tasks:
            if task_time > current_time:
                task_key = f"{task_time.hour:02d}:{task_time.minute:02d}"
                if self.last_executed[task_key] != current_date:
                    return task_time

        # 如果今天的任务都完成了，返回明天的第一个任务
        tomorrow = current_date + timedelta(days=1)
        tomorrow_task = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day,
            11, 30, 0, 0
        )
        return tomorrow_task

    def run(self):
        """运行调度器"""
        logger.info("🚀 股票筛选自动调度器启动")
        logger.info("=" * 50)
        logger.info("⏰ 定时任务:")
        logger.info("  • 11:30 - 自适应主力埋伏策略 (实时数据，如休盘则使用最新历史数据)")
        logger.info("  • 14:30 - 快刀手晚进早出策略v2.0 (涨幅2.8-4.5%, 量比1.0-1.6, 换手率U型)")
        logger.info("  • 14:50 - 主力埋伏策略v4.1 (优化评分版 - 精选TOP 10)")
        logger.info("💡 按 Ctrl+C 停止调度器")
        logger.info("=" * 50)

        try:
            while self.running:
                current_time = datetime.now()

                # 检查并执行任务
                self.check_and_execute_tasks()

                # 显示状态（每分钟显示一次）
                if current_time.second == 0:
                    next_task_time = self.get_next_task_time()
                    time_until_next = next_task_time - current_time

                    if time_until_next.days >= 0:
                        hours = time_until_next.seconds // 3600
                        minutes = (time_until_next.seconds % 3600) // 60

                        logger.info(f"⏰ 当前时间: {current_time.strftime('%H:%M:%S')} | "
                                  f"下次任务: {next_task_time.strftime('%H:%M')} | "
                                  f"剩余: {hours:02d}:{minutes:02d}")

                # 短暂休眠，避免CPU占用过高
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭...")
        except Exception as e:
            logger.error(f"调度器运行出错: {e}")
        finally:
            logger.info("🛑 股票筛选自动调度器已关闭")

    def save_status(self):
        """保存执行状态"""
        status_file = Path('scheduler_status.json')
        status_data = {
            'last_updated': datetime.now().isoformat(),
            'last_executed': {k: v.isoformat() if isinstance(v, (datetime, date)) else None for k, v in self.last_executed.items()}
        }

        try:
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")

    def load_status(self):
        """加载执行状态"""
        status_file = Path('scheduler_status.json')

        try:
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status_data = json.load(f)

                for key, date_str in status_data.get('last_executed', {}).items():
                    if date_str and date_str is not None:
                        self.last_executed[key] = datetime.fromisoformat(date_str).date()

                logger.info("已加载上次执行状态")
        except Exception as e:
            logger.error(f"加载状态失败: {e}")

def main():
    """主函数"""
    scheduler = AutoScheduler()

    # 加载上次执行状态
    scheduler.load_status()

    try:
        scheduler.run()
    finally:
        # 保存当前状态
        scheduler.save_status()

if __name__ == "__main__":
    main()