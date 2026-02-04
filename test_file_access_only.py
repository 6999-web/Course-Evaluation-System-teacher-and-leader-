#!/usr/bin/env python3
"""
只测试文件访问，不调用API
"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "评教系统最终版/评教系统管理端/backend_8fMBP/backend"))

from app.file_parser import FileParser

def test_file_access():
    """测试文件访问"""
    print("🔍 测试文件访问")
    print("=" * 60)
    
    # 模拟数据库中的路径（混合分隔符）
    file_path_db = "uploads/evaluation_submissions/teacher_001\\tpl_8cb26a5d_teacher_001_20260204100831_37adbe6d_完整教学反思.docx"
    
    print(f"\n数据库路径: {file_path_db}")
    
    # 应用修复
    file_path = file_path_db.replace('\\', '/')
    file_path = os.path.normpath(file_path)
    print(f"规范化路径: {file_path}")
    
    # 计算base_dir（模拟scoring.py）
    scoring_file = os.path.join(os.path.dirname(__file__), "评教系统最终版/评教系统管理端/backend_8fMBP/backend/app/routes/scoring.py")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(scoring_file))))
    parent_dir = os.path.dirname(os.path.dirname(base_dir))
    
    print(f"\nbase_dir: {base_dir}")
    print(f"parent_dir: {parent_dir}")
    
    # 尝试路径
    possible_paths = [
        file_path,
        os.path.join(parent_dir, "评教系统教师端", "backend", file_path),
        os.path.join(base_dir, "..", "..", "评教系统教师端", "backend", file_path),
    ]
    
    actual_file_path = None
    for i, path in enumerate(possible_paths, 1):
        normalized = os.path.normpath(path)
        exists = os.path.exists(normalized)
        print(f"\n路径 {i}: {normalized}")
        print(f"  存在: {exists}")
        if exists:
            actual_file_path = normalized
            print(f"  ✅ 找到文件!")
            break
    
    if not actual_file_path:
        print(f"\n❌ 文件未找到")
        return False
    
    # 尝试解析文件
    print(f"\n解析文件...")
    try:
        file_ext = os.path.splitext(actual_file_path)[1].lower().lstrip('.')
        content = FileParser.parse_file(actual_file_path, file_ext)
        print(f"✅ 文件解析成功")
        print(f"   内容长度: {len(content)} 字符")
        print(f"   前100字符: {content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 文件解析失败: {e}")
        return False

if __name__ == "__main__":
    success = test_file_access()
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过 - 文件访问和解析正常")
        sys.exit(0)
    else:
        print("❌ 测试失败")
        sys.exit(1)
