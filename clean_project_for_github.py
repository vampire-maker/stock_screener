#!/usr/bin/env python3
"""
清理项目文件夹，准备上传到GitHub
"""

import os
import shutil
import glob
from pathlib import Path

def clean_project():
    """清理项目文件"""

    print("🧹 开始清理项目文件...")
    print("=" * 60)

    # 创建备份目录（如果需要）
    backup_dir = "backup_before_github"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 需要保留的核心文件和目录
    keep_patterns = [
        "src/",
        "core/",
        "scripts/",
        "requirements.txt",
        ".env.example",
        "README.md",
        ".gitignore",
        "LICENSE",
        "pyproject.toml",
        "setup.py"
    ]

    # 需要删除的文件模式
    delete_patterns = [
        # 测试文件
        "test_*.py",
        "*_test*.py",
        "analyze_*.py",

        # 日期文件
        "2025*",
        "*_2025*",

        # 结果文件
        "*result*.json",
        "*result_*.png",
        "*result_*.html",

        # 日志文件
        "*.log",

        # 备份文件
        "backup_*",
        "*_backup*",

        # 临时文件
        "*.tmp",
        "__pycache__/",
        "*.pyc",
        ".DS_Store",

        # 数据文件
        "*.csv",
        "*.xlsx",
        "data/",
        "logs/",

        # AI/IDE文件
        ".vscode/",
        ".idea/",

        # Python相关
        "venv/",
        "env/",
        ".env",
    ]

    # 特殊保留文件
    special_keep = [
        # 保留最新的结果文件作为示例
        "main_force_burial_result_20251218_144017.json",
        "main_force_burial_result_20251216_145152.json",
    ]

    # 移动测试和分析文件到备份目录
    print("\n📦 移动测试和分析文件...")
    moved_count = 0

    # 查找需要移动的文件
    for pattern in ["test_*.py", "analyze_*.py", "*_test*.py"]:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                dest = os.path.join(backup_dir, file_path)
                shutil.move(file_path, dest)
                moved_count += 1
                print(f"  移动: {file_path}")

    # 移动带日期的文件
    for file_path in glob.glob("*2025*"):
        if os.path.isfile(file_path) and file_path not in special_keep:
            dest = os.path.join(backup_dir, file_path)
            shutil.move(file_path, dest)
            moved_count += 1
            print(f"  移动: {file_path}")

    # 移动结果文件（保留示例）
    for file_path in glob.glob("*result*"):
        if os.path.isfile(file_path) and file_path not in special_keep:
            dest = os.path.join(backup_dir, file_path)
            shutil.move(file_path, dest)
            moved_count += 1
            print(f"  移动: {file_path}")

    # 移动备份目录（跳过当前创建的备份目录）
    for dir_path in glob.glob("backup_*"):
        if os.path.isdir(dir_path) and dir_path != backup_dir:
            dest = os.path.join(backup_dir, dir_path)
            shutil.move(dir_path, dest)
            moved_count += 1
            print(f"  移动目录: {dir_path}")

    print(f"\n✅ 已移动 {moved_count} 个文件到备份目录")

    # 删除不需要的文件和目录
    print("\n🗑️ 清理不需要的文件...")
    deleted_count = 0

    # 删除__pycache__目录
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                cache_path = os.path.join(root, d)
                shutil.rmtree(cache_path)
                deleted_count += 1
                print(f"  删除: {cache_path}")

    # 删除日志文件
    for log_file in glob.glob("*.log"):
        os.remove(log_file)
        deleted_count += 1
        print(f"  删除: {log_file}")

    # 删除临时文件
    for ext in [".pyc", ".tmp", ".DS_Store"]:
        for file_path in glob.glob(f"*{ext}"):
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"  删除: {file_path}")

    print(f"\n✅ 已删除 {deleted_count} 个文件")

    # 显示清理后的目录结构
    print("\n📁 清理后的项目结构:")
    print("-" * 40)

    for root, dirs, files in os.walk("."):
        # 跳过隐藏目录和备份目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != backup_dir]

        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")

        subindent = " " * 2 * (level + 1)
        for f in sorted(files)[:5]:  # 每个目录最多显示5个文件
            if not f.startswith('.'):
                print(f"{subindent}{f}")

        if len(files) > 5:
            print(f"{subindent}... 还有 {len(files) - 5} 个文件")

    print("\n" + "=" * 60)
    print("✅ 项目清理完成！")
    print(f"📦 备份文件保存在: {backup_dir}/")
    print("\n📝 下一步:")
    print("1. 创建 .gitignore 文件")
    print("2. 创建 README.md 文件")
    print("3. 初始化 Git 仓库")
    print("4. 上传到 GitHub")

    return backup_dir

if __name__ == "__main__":
    clean_project()