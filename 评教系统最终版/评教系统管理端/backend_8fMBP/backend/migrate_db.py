#!/usr/bin/env python3
"""
数据库迁移脚本
添加缺失的列到evaluation_assignment_tasks表
"""

import sqlite3
import sys

def migrate():
    """执行迁移"""
    try:
        # 连接数据库
        db_path = '评教系统最终版/评教系统管理端/backend_8fMBP/backend/evaluation_system.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查is_viewed列是否存在
        cursor.execute("PRAGMA table_info(evaluation_assignment_tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"现有列: {columns}")
        
        # 添加缺失的列
        if 'is_viewed' not in columns:
            print("添加 is_viewed 列...")
            cursor.execute("ALTER TABLE evaluation_assignment_tasks ADD COLUMN is_viewed BOOLEAN DEFAULT 0")
            print("✅ is_viewed 列已添加")
        else:
            print("✅ is_viewed 列已存在")
        
        if 'viewed_at' not in columns:
            print("添加 viewed_at 列...")
            cursor.execute("ALTER TABLE evaluation_assignment_tasks ADD COLUMN viewed_at DATETIME")
            print("✅ viewed_at 列已添加")
        else:
            print("✅ viewed_at 列已存在")
        
        # 提交更改
        conn.commit()
        print("\n✅ 数据库迁移完成")
        
        # 验证
        cursor.execute("PRAGMA table_info(evaluation_assignment_tasks)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"迁移后的列: {columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
