#!/usr/bin/env python3
"""
项目自动清理脚本
包括结果文件归档、日志轮转、临时文件清理等功能
"""

import os
import sys
import glob
import shutil
from datetime import datetime, timedelta

def cleanup():
    """执行所有清理任务"""

    print("🚀 开始项目清理...")
    print("=" * 50)

    # 1. 归档旧的结果文件
    print("\n📁 归档结果文件...")
    try:
        from scripts.archive_old_results import archive_old_results
        archive_old_results()
    except ImportError:
        print("⚠️ 无法导入归档模块，跳过")

    # 2. 轮转日志文件
    print("\n📝 轮转日志文件...")
    try:
        from scripts.rotate_logs import rotate_log_file, cleanup_old_logs
        rotate_log_file("auto_scheduler.log")
        cleanup_old_logs(30)
    except ImportError:
        print("⚠️ 无法导入日志轮转模块，跳过")

    # 3. 清理临时文件
    print("\n🗑️ 清理临时文件...")
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*.log.*",
        "test_*.json",
        "debug_*.txt"
    ]

    cleaned_count = 0
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                    print(f"删除临时文件: {file_path}")
            except OSError as e:
                print(f"无法删除 {file_path}: {e}")

    # 4. 清理空的__pycache__目录
    print("\n🐍 清理Python缓存...")
    cleaned_dirs = 0
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                if not os.listdir(pycache_path):  # 目录为空
                    os.rmdir(pycache_path)
                    cleaned_dirs += 1
                    print(f"删除空缓存目录: {pycache_path}")
                else:
                    # 非空目录，删除.pyc文件
                    pyc_files = glob.glob(os.path.join(pycache_path, "*.pyc"))
                    for pyc_file in pyc_files:
                        os.remove(pyc_file)
                        cleaned_count += 1
            except OSError as e:
                print(f"清理缓存失败 {pycache_path}: {e}")

    # 5. 显示清理统计
    print("\n" + "=" * 50)
    print("📊 清理统计:")
    print(f"   删除临时文件: {cleaned_count} 个")
    print(f"   清理缓存目录: {cleaned_dirs} 个")

    # 6. 显示当前项目状态
    print("\n📈 当前项目状态:")

    # 统计结果文件
    result_files = glob.glob("enhanced_1130_result_*.json")
    archived_files = glob.glob("archive/results/*.json")
    print(f"   当前结果文件: {len(result_files)} 个")
    print(f"   归档结果文件: {len(archived_files)} 个")

    # 统计日志文件
    if os.path.exists("auto_scheduler.log"):
        log_size = os.path.getsize("auto_scheduler.log") / (1024 * 1024)
        print(f"   当前日志大小: {log_size:.2f} MB")

    log_files = glob.glob("archive/logs/*.gz")
    print(f"   归档日志文件: {len(log_files)} 个")

    print("\n✅ 项目清理完成！")

if __name__ == "__main__":
    cleanup()