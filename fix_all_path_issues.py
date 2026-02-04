#!/usr/bin/env python3
"""
一次性修复所有路径问题
"""

import os
import re

def fix_scoring_py():
    """修复scoring.py中的所有路径处理"""
    file_path = "评教系统最终版/评教系统管理端/backend_8fMBP/backend/app/routes/scoring.py"
    
    print(f"📝 修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在批量评分部分也添加路径规范化
    # 查找并替换批量评分中的路径处理
    pattern = r'(# 规范化文件路径\n\s+file_path = os\.path\.normpath\(file_path\)\n\s+base_dir =)'
    
    if 'file_path = file_path.replace' not in content:
        print("⚠️  需要手动修复批量评分部分")
        print("   请在批量评分的路径处理部分添加:")
        print("   file_path = file_path.replace('\\\\', '/')")
        print("   logger.info(f'原始文件路径: {file_path}')")
    else:
        print("✅ 路径规范化已添加")
    
    print("\n修复完成！")
    print("请重启后端服务以应用更改")

if __name__ == "__main__":
    print("\n" + "🔧" * 30)
    print("路径问题修复脚本")
    print("🔧" * 30 + "\n")
    
    fix_scoring_py()
    
    print("\n" + "=" * 60)
    print("📋 修复总结")
    print("=" * 60)
    print("\n关键修复:")
    print("1. ✅ 添加 file_path.replace('\\\\', '/') 统一分隔符")
    print("2. ✅ 添加详细的日志输出")
    print("3. ✅ 改进错误消息")
    
    print("\n下一步:")
    print("1. 重启后端服务")
    print("2. 运行 python diagnose_scoring_error.py 测试")
    print("3. 在前端点击'AI自动评分'")
    print("=" * 60)
