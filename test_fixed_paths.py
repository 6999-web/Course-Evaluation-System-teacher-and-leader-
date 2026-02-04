#!/usr/bin/env python3
"""
测试修复后的路径计算
"""

import os

# 模拟scoring.py中的__file__路径
scoring_file = r"C:\Users\xxzx-admin\Desktop\评教系统最终版\评教系统最终版\评教系统管理端\backend_8fMBP\backend\app\routes\scoring.py"

print("🔍 测试修复后的路径计算")
print("=" * 80)
print(f"\n__file__: {scoring_file}")

# 模拟scoring.py中的计算
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(scoring_file))))
print(f"\nbase_dir: {base_dir}")

# 从backend_8fMBP向上两级到评教系统最终版目录
parent_dir = os.path.dirname(os.path.dirname(base_dir))
print(f"parent_dir: {parent_dir}")

# 测试路径拼接
file_path = r"uploads\evaluation_submissions\teacher_001\tpl_8cb26a5d_teacher_001_20260204100831_37adbe6d_完整教学反思.docx"

possible_paths = [
    file_path,
    os.path.join(parent_dir, "评教系统教师端", "backend", file_path),
    os.path.join(base_dir, "..", "..", "评教系统教师端", "backend", file_path),
    os.path.normpath(os.path.join(os.path.dirname(scoring_file), "../../../../评教系统教师端/backend", file_path))
]

print(f"\n可能的路径:")
for i, path in enumerate(possible_paths, 1):
    normalized = os.path.normpath(path)
    exists = os.path.exists(normalized)
    print(f"  {i}. {normalized}")
    print(f"     存在: {exists}")
    if exists:
        print(f"     ✅ 找到!")
