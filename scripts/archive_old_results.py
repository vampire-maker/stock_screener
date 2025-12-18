#!/usr/bin/env python3
"""
归档旧的结果文件
保留最近7天的结果，将更早的文件移动到archive目录
"""

import os
import glob
import shutil
from datetime import datetime, timedelta

def archive_old_results():
    """归档超过7天的结果文件"""

    # 创建归档目录
    archive_dir = "archive/results"
    os.makedirs(archive_dir, exist_ok=True)

    # 查找所有结果文件
    result_files = glob.glob("enhanced_1130_result_*.json")

    # 计算 cutoff 日期 (7天前)
    cutoff_date = datetime.now() - timedelta(days=7)

    archived_count = 0
    for file_path in result_files:
        # 从文件名提取日期
        try:
            filename = os.path.basename(file_path)
            # 格式: enhanced_1130_result_YYYYMMDD_HHMMSS.json
            date_str = filename.split('_')[3] + '_' + filename.split('_')[4].split('.')[0]
            file_date = datetime.strptime(date_str, '%Y%m%d_%H%M%S')

            if file_date < cutoff_date:
                # 移动到归档目录
                archive_path = os.path.join(archive_dir, filename)
                shutil.move(file_path, archive_path)
                archived_count += 1
                print(f"已归档: {filename}")

        except (IndexError, ValueError) as e:
            print(f"跳过无法解析日期的文件: {filename}")
            continue

    print(f"✅ 归档完成，共移动 {archived_count} 个文件")

    # 清理空目录
    try:
        os.rmdir("archive/old_results")  # 删除可能的旧目录
    except OSError:
        pass

if __name__ == "__main__":
    archive_old_results()