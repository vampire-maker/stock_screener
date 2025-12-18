#!/usr/bin/env python3
"""
系统清理工具
自动清理缓存文件、日志文件和临时数据
"""

import os
import sys
import shutil
import glob
import json
import time
import logging
import tarfile
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from config import get_config
    config = get_config()
except ImportError:
    config = None

# 确保日志目录存在
logs_dir = project_root / 'logs'
logs_dir.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'system_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemCleanup:
    """系统清理工具"""

    def __init__(self):
        self.project_root = project_root
        self.archive_dir = self.project_root / 'archive'
        self.logs_dir = self.project_root / 'logs'
        self.results_dir = self.project_root / 'results'

        # 创建必要的目录
        self.archive_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)

        # 清理配置
        self.cleanup_config = {
            'cache_retention_days': 7,
            'log_retention_days': 30,
            'result_retention_days': 90,
            'temp_file_retention_hours': 24
        }

    def clean_python_cache(self):
        """清理Python缓存文件"""
        logger.info("开始清理Python缓存文件...")

        cache_patterns = [
            '**/__pycache__/',
            '**/*.pyc',
            '**/*.pyo',
            '**/*.pyd'
        ]

        cleaned_count = 0
        for pattern in cache_patterns:
            for item in self.project_root.glob(pattern):
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                        logger.info(f"删除缓存目录: {item}")
                    else:
                        item.unlink()
                        logger.info(f"删除缓存文件: {item}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"删除缓存失败 {item}: {e}")

        logger.info(f"Python缓存清理完成，共删除 {cleaned_count} 项")
        return cleaned_count

    def clean_old_results(self, retention_days=None):
        """归档和清理旧的结果文件"""
        retention_days = retention_days or self.cleanup_config['result_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        logger.info(f"开始归档 {retention_days} 天前的结果文件...")

        # 创建归档子目录
        old_results_dir = self.archive_dir / 'old_results'
        old_results_dir.mkdir(exist_ok=True)

        result_patterns = [
            '*result*.json',
            '*screening*.json',
            '*burial*.json'
        ]

        archived_count = 0
        for pattern in result_patterns:
            for file_path in self.results_dir.glob(pattern):
                try:
                    # 获取文件修改时间
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                    if file_mtime < cutoff_date:
                        # 创建归档文件名
                        archive_name = f"{file_mtime.strftime('%Y%m')}/{file_path.name}"
                        archive_path = old_results_dir / archive_name

                        # 创建月度目录
                        archive_path.parent.mkdir(exist_ok=True)

                        # 移动文件到归档目录
                        shutil.move(str(file_path), str(archive_path))
                        logger.info(f"归档结果文件: {file_path.name} -> {archive_name}")
                        archived_count += 1

                except Exception as e:
                    logger.warning(f"归档结果文件失败 {file_path}: {e}")

        logger.info(f"结果文件归档完成，共归档 {archived_count} 个文件")
        return archived_count

    def clean_old_logs(self, retention_days=None):
        """压缩和清理旧的日志文件"""
        retention_days = retention_days or self.cleanup_config['log_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        logger.info(f"开始压缩 {retention_days} 天前的日志文件...")

        old_logs_dir = self.archive_dir / 'old_logs'
        old_logs_dir.mkdir(exist_ok=True)

        compressed_count = 0
        for log_file in self.logs_dir.glob('*.log'):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                if file_mtime < cutoff_date:
                    # 创建压缩文件
                    archive_name = f"{log_file.stem}_{file_mtime.strftime('%Y%m')}.tar.gz"
                    archive_path = old_logs_dir / archive_name

                    # 压缩日志文件
                    with tarfile.open(archive_path, 'w:gz') as tar:
                        tar.add(log_file, arcname=log_file.name)

                    # 删除原文件
                    log_file.unlink()
                    logger.info(f"压缩日志文件: {log_file.name} -> {archive_name}")
                    compressed_count += 1

            except Exception as e:
                logger.warning(f"压缩日志文件失败 {log_file}: {e}")

        logger.info(f"日志文件压缩完成，共压缩 {compressed_count} 个文件")
        return compressed_count

    def clean_temp_files(self, retention_hours=None):
        """清理临时文件"""
        retention_hours = retention_hours or self.cleanup_config['temp_file_retention_hours']
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        logger.info(f"开始清理 {retention_hours} 小时前的临时文件...")

        temp_patterns = [
            '**/*.tmp',
            '**/*.temp',
            '**/*~',
            '**/.DS_Store',
            '**/Thumbs.db'
        ]

        cleaned_count = 0
        for pattern in temp_patterns:
            for file_path in self.project_root.glob(pattern):
                try:
                    # 跳过重要目录
                    if any(part.startswith('.') for part in file_path.parts):
                        continue

                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        logger.info(f"删除临时文件: {file_path}")
                        cleaned_count += 1

                except Exception as e:
                    logger.warning(f"删除临时文件失败 {file_path}: {e}")

        logger.info(f"临时文件清理完成，共删除 {cleaned_count} 个文件")
        return cleaned_count

    def clean_stock_cache(self):
        """清理股票缓存文件"""
        logger.info("开始清理股票缓存文件...")

        cache_files = [
            'smart_stock_universe.json',
            'stock_data_cache.json',
            'api_cache.json'
        ]

        cleaned_count = 0
        for cache_file in cache_files:
            cache_path = self.project_root / cache_file
            if cache_path.exists():
                try:
                    # 检查缓存文件年龄
                    file_age = time.time() - cache_path.stat().st_mtime
                    if file_age > 86400:  # 24小时
                        cache_path.unlink()
                        logger.info(f"删除过期缓存: {cache_file}")
                        cleaned_count += 1
                    else:
                        logger.info(f"缓存文件仍新鲜，保留: {cache_file}")
                except Exception as e:
                    logger.warning(f"删除缓存文件失败 {cache_file}: {e}")

        logger.info(f"股票缓存清理完成，共删除 {cleaned_count} 个文件")
        return cleaned_count

    def get_disk_usage_stats(self):
        """获取磁盘使用统计"""
        stats = {
            'total_size': 0,
            'directories': {}
        }

        important_dirs = ['src', 'core', 'scripts', 'logs', 'results', 'archive', 'venv']

        for dir_name in important_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                size = 0
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        size += file_path.stat().st_size

                stats['directories'][dir_name] = {
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                }
                stats['total_size'] += size

        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
        return stats

    def generate_cleanup_report(self, cleanup_results):
        """生成清理报告"""
        report = {
            'cleanup_time': datetime.now().isoformat(),
            'cleanup_results': cleanup_results,
            'disk_usage_before': cleanup_results.get('disk_usage_before', {}),
            'disk_usage_after': self.get_disk_usage_stats()
        }

        # 计算节省的空间
        before_size = cleanup_results.get('disk_usage_before', {}).get('total_size', 0)
        after_size = report['disk_usage_after']['total_size']
        saved_space = before_size - after_size

        report['saved_space_mb'] = round(saved_space / (1024 * 1024), 2)

        # 保存报告
        report_path = self.logs_dir / f'cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"清理报告已保存到: {report_path}")
        return report

    def run_full_cleanup(self):
        """执行完整的系统清理"""
        logger.info("开始执行完整系统清理...")
        start_time = time.time()

        # 获取清理前的磁盘使用情况
        disk_usage_before = self.get_disk_usage_stats()

        # 执行各项清理任务
        cleanup_results = {
            'disk_usage_before': disk_usage_before,
            'tasks': {}
        }

        try:
            # 1. 清理Python缓存
            cache_count = self.clean_python_cache()
            cleanup_results['tasks']['python_cache'] = {'cleaned_count': cache_count}

            # 2. 归档旧结果文件
            archived_count = self.clean_old_results()
            cleanup_results['tasks']['old_results'] = {'archived_count': archived_count}

            # 3. 压缩旧日志文件
            compressed_count = self.clean_old_logs()
            cleanup_results['tasks']['old_logs'] = {'compressed_count': compressed_count}

            # 4. 清理临时文件
            temp_count = self.clean_temp_files()
            cleanup_results['tasks']['temp_files'] = {'cleaned_count': temp_count}

            # 5. 清理股票缓存
            cache_count = self.clean_stock_cache()
            cleanup_results['tasks']['stock_cache'] = {'cleaned_count': cache_count}

        except Exception as e:
            logger.error(f"清理过程中发生错误: {e}")

        # 生成清理报告
        cleanup_time = time.time() - start_time
        cleanup_results['total_time_seconds'] = round(cleanup_time, 2)

        report = self.generate_cleanup_report(cleanup_results)

        logger.info(f"系统清理完成！耗时 {cleanup_time:.2f} 秒")
        logger.info(f"节省磁盘空间: {report['saved_space_mb']:.2f} MB")

        return report

def main():
    """主函数"""
    print("🧹 股票筛选系统清理工具")
    print("=" * 50)

    cleaner = SystemCleanup()

    # 显示清理前的磁盘使用情况
    print("\n📊 清理前磁盘使用情况:")
    disk_usage_before = cleaner.get_disk_usage_stats()
    for dir_name, info in disk_usage_before['directories'].items():
        print(f"  {dir_name}/: {info['size_mb']} MB")
    print(f"  总计: {disk_usage_before['total_size_mb']} MB")

    # 执行清理
    print("\n🚀 开始清理...")
    report = cleaner.run_full_cleanup()

    # 显示清理结果
    print("\n📋 清理结果:")
    for task_name, result in report['cleanup_results']['tasks'].items():
        for key, value in result.items():
            print(f"  {task_name}: {value}")

    print(f"\n💾 节省磁盘空间: {report['saved_space_mb']:.2f} MB")
    print(f"⏱️  清理耗时: {report['cleanup_results']['total_time_seconds']:.2f} 秒")

    print("\n✅ 系统清理完成！")

if __name__ == "__main__":
    main()