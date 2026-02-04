#!/usr/bin/env python3
"""
测试文件路径修复
"""

import os
import sys

def test_path_normalization():
    """测试路径规范化"""
    print("🧪 测试文件路径规范化")
    print("=" * 60)
    
    # 测试各种路径格式
    test_paths = [
        "uploads/evaluation_submissions/teacher_001\\tpl_xxx",
        "uploads\\evaluation_submissions\\teacher_001\\tpl_xxx",
        "uploads/evaluation_submissions/teacher_001/tpl_xxx",
    ]
    
    print("\n1. 测试路径规范化...")
    for path in test_paths:
        normalized = os.path.normpath(path)
        print(f"   原始: {path}")
        print(f"   规范: {normalized}")
        print()
    
    # 测试路径拼接
    print("2. 测试路径拼接...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = "uploads/submissions/teacher_001/test.txt"
    
    # 错误的方式（字符串拼接）
    wrong_path = f"{base_dir}/{relative_path}"
    print(f"   错误方式: {wrong_path}")
    
    # 正确的方式（os.path.join）
    correct_path = os.path.join(base_dir, relative_path)
    print(f"   正确方式: {correct_path}")
    
    # 规范化后
    normalized_path = os.path.normpath(correct_path)
    print(f"   规范化后: {normalized_path}")
    
    print("\n✅ 路径处理测试完成")
    print("\n关键点:")
    print("1. 使用 os.path.normpath() 规范化路径")
    print("2. 使用 os.path.join() 拼接路径")
    print("3. 避免字符串拼接路径")
    print("4. Windows会自动处理正斜杠和反斜杠")

def check_teacher_backend_files():
    """检查教师端文件是否存在"""
    print("\n" + "=" * 60)
    print("🔍 检查教师端文件")
    print("=" * 60)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n当前目录: {current_dir}")
    
    # 尝试找到教师端目录
    possible_teacher_dirs = [
        os.path.join(current_dir, "评教系统最终版", "评教系统教师端", "backend"),
        os.path.join(current_dir, "..", "评教系统教师端", "backend"),
        os.path.join(current_dir, "评教系统教师端", "backend"),
    ]
    
    teacher_backend_dir = None
    for dir_path in possible_teacher_dirs:
        normalized_dir = os.path.normpath(dir_path)
        print(f"\n尝试: {normalized_dir}")
        if os.path.exists(normalized_dir):
            teacher_backend_dir = normalized_dir
            print(f"✅ 找到教师端目录!")
            break
        else:
            print(f"❌ 不存在")
    
    if not teacher_backend_dir:
        print("\n⚠️  未找到教师端目录")
        return
    
    # 检查uploads目录
    uploads_dir = os.path.join(teacher_backend_dir, "uploads")
    if os.path.exists(uploads_dir):
        print(f"\n✅ uploads目录存在: {uploads_dir}")
        
        # 列出子目录
        try:
            subdirs = [d for d in os.listdir(uploads_dir) if os.path.isdir(os.path.join(uploads_dir, d))]
            print(f"\n子目录:")
            for subdir in subdirs:
                print(f"   • {subdir}")
                
                # 检查teacher_001目录
                if subdir in ["submissions", "evaluation_submissions"]:
                    teacher_dir = os.path.join(uploads_dir, subdir, "teacher_001")
                    if os.path.exists(teacher_dir):
                        print(f"     ✅ {subdir}/teacher_001 存在")
                        files = os.listdir(teacher_dir)
                        if files:
                            print(f"     文件数: {len(files)}")
                            for f in files[:3]:  # 只显示前3个
                                print(f"       - {f}")
        except Exception as e:
            print(f"❌ 读取目录失败: {e}")
    else:
        print(f"\n❌ uploads目录不存在: {uploads_dir}")

def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("文件路径修复测试")
    print("🎯" * 30 + "\n")
    
    test_path_normalization()
    check_teacher_backend_files()
    
    print("\n" + "=" * 60)
    print("📝 修复说明")
    print("=" * 60)
    print("\n已修复的问题:")
    print("1. ✅ 使用 os.path.normpath() 规范化所有路径")
    print("2. ✅ 使用 os.path.join() 拼接路径")
    print("3. ✅ 添加日志输出，便于调试")
    print("4. ✅ 支持Windows和Linux路径格式")
    
    print("\n下一步:")
    print("1. 重启后端服务")
    print("2. 在前端点击'AI自动评分'")
    print("3. 查看后端日志中的路径信息")
    print("=" * 60)

if __name__ == "__main__":
    main()
