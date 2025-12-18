#!/usr/bin/env python3
"""
日志文件轮转脚本
当日志文件超过1MB时，轮转并压缩旧日志
"""

import os
import gzip
import shutil
from datetime import datetime

def rotate_log_file(log_file_path, max_size_mb=1):
    """轮转日志文件"""

    if not os.path.exists(log_file_path):
        print(f"日志文件不存在: {log_file_path}")
        return

    # 获取文件大小 (MB)
    file_size_mb = os.path.getsize(log_file_path) / (1024 * 1024)

    if file_size_mb < max_size_mb:
        print(f"日志文件大小 {file_size_mb:.2f}MB 小于阈值 {max_size_mb}MB，无需轮转")
        return

    print(f"日志文件大小 {file_size_mb:.2f}MB，开始轮转...")

    # 创建归档目录
    archive_dir = "archive/logs"
    os.makedirs(archive_dir, exist_ok=True)

    # 生成归档文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_filename = f"auto_scheduler_{timestamp}.log.gz"
    archive_path = os.path.join(archive_dir, archive_filename)

    # 压缩并移动日志文件
    with open(log_file_path, 'rb') as f_in:
        with gzip.open(archive_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # 清空原日志文件
    with open(log_file_path, 'w') as f:
        f.write(f"日志轮转完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")

    # 获取压缩后大小
    compressed_size_mb = os.path.getsize(archive_path) / (1024 * 1024)
    print(f"✅ 日志轮转完成:")
    print(f"   原文件: {file_size_mb:.2f}MB")
    print(f"   压缩后: {compressed_size_mb:.2f}MB")
    print(f"   节省空间: {((file_size_mb - compressed_size_mb) / file_size_mb * 100):.1f}%")
    print(f"   归档文件: {archive_path}")

def cleanup_old_logs(keep_days=30):
    """清理超过指定天数的旧日志"""

    archive_dir = "archive/logs"
    if not os.path.exists(archive_dir):
        return

    cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
    deleted_count = 0

    for filename in os.listdir(archive_dir):
        file_path = os.path.join(archive_dir, filename)
        if os.path.getmtime(file_path) < cutoff_time:
            os.remove(file_path)
            deleted_count += 1
            print(f"删除旧日志: {filename}")

    if deleted_count > 0:
        print(f"✅ 清理完成，删除了 {deleted_count} 个旧日志文件")

if __name__ == "__main__":
    # 轮转当前日志
    rotate_log_file("auto_scheduler.log")

    # 清理30天前的旧日志
    cleanup_old_logs(keep_days=30)