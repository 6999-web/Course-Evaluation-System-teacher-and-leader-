#!/usr/bin/env python3
"""
只测试路径解析，不调用API
"""

import os
import sys

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "评教系统最终版/评教系统管理端/backend_8fMBP/backend"))

def test_path_resolution():
    """测试路径解析"""
    print("🔍 测试路径解析")
    print("=" * 60)
    
    # 模拟数据库中的路径（混合分隔符）
    file_path = "uploads/evaluation_submissions/teacher_001\\tpl_8cb26a5d_teacher_001_20260204100831_37adbe6d_完整教学反思.docx"
    
    print(f"\n原始路径: {file_path}")
    print(f"  包含反斜杠: {'\\' in file_path}")
    print(f"  包含正斜杠: {'/' in file_path}")
    
    # 应用修复
    print(f"\n应用修复:")
    file_path_fixed = file_path.replace('\\', '/')
    print(f"  1. replace('\\\\', '/'): {file_path_fixed}")
    
    file_path_normalized = os.path.normpath(file_path_fixed)
    print(f"  2. os.path.normpath(): {file_path_normalized}")
    
    # 尝试查找文件
    print(f"\n查找文件:")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"  基础目录: {base_dir}")
    
    possible_paths = [
        file_path_normalized,
        os.path.join(base_dir, "评教系统教师端", "backend", file_path_normalized),
        os.path.join(base_dir, "评教系统最终版", "评教系统教师端", "backend", file_path_normalized),
    ]
    
    for i, path in enumerate(possible_paths, 1):
        normalized = os.path.normpath(path)
        exists = os.path.exists(normalized)
        print(f"  {i}. {normalized}")
        print(f"     存在: {exists}")
        if exists:
            print(f"     ✅ 找到文件!")
            return True
    
    print(f"\n❌ 文件未找到")
    return False

if __name__ == "__main__":
    success = test_path_resolution()
    print("\n" + "=" * 60)
    if success:
        print("✅ 路径解析成功")
        sys.exit(0)
    else:
        print("❌ 路径解析失败")
        sys.exit(1)
