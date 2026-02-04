#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加 scoring_result 列到 material_submissions 表

这个脚本用于将 DeepSeek 自动评分系统集成到现有数据库中。
"""

import sqlite3
import json
import os
from datetime import datetime

def migrate_database(db_path):
    """迁移数据库，添加评分相关列"""
    
    print(f"开始迁移数据库: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查 scoring_result 列是否已存在
        cursor.execute("PRAGMA table_info(material_submissions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'scoring_result' not in columns:
            print("添加 scoring_result 列...")
            cursor.execute("""
                ALTER TABLE material_submissions 
                ADD COLUMN scoring_result TEXT
            """)
            print("✓ scoring_result 列添加成功")
        else:
            print("✓ scoring_result 列已存在")
        
        # 检查其他评分相关列
        missing_columns = []
        expected_columns = {
            'scoring_status': 'TEXT DEFAULT "pending"',
            'parsed_content': 'TEXT',
            'file_hash': 'TEXT',
            'encrypted_path': 'TEXT'
        }
        
        for col_name, col_def in expected_columns.items():
            if col_name not in columns:
                missing_columns.append((col_name, col_def))
        
        # 添加缺失的列
        for col_name, col_def in missing_columns:
            print(f"添加 {col_name} 列...")
            cursor.execute(f"""
                ALTER TABLE material_submissions 
                ADD COLUMN {col_name} {col_def}
            """)
            print(f"✓ {col_name} 列添加成功")
        
        # 创建评分相关表（如果不存在）
        create_scoring_tables(cursor)
        
        # 提交更改
        conn.commit()
        print("✓ 数据库迁移完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def create_scoring_tables(cursor):
    """创建评分相关表"""
    
    # 评分记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scoring_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id TEXT NOT NULL,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_name TEXT NOT NULL,
            base_score REAL NOT NULL,
            bonus_score REAL DEFAULT 0,
            final_score REAL NOT NULL,
            grade TEXT NOT NULL,
            score_details TEXT,
            veto_triggered BOOLEAN DEFAULT 0,
            veto_reason TEXT,
            scoring_type TEXT DEFAULT 'auto',
            scored_by INTEGER,
            scored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_confirmed BOOLEAN DEFAULT 0,
            confirmed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ scoring_records 表创建/检查完成")
    
    # 评分异议表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scoring_appeals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scoring_record_id INTEGER NOT NULL,
            teacher_id TEXT NOT NULL,
            teacher_name TEXT NOT NULL,
            appeal_reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            reviewed_by INTEGER,
            review_result TEXT,
            reviewed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ scoring_appeals 表创建/检查完成")
    
    # 评分模板表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scoring_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT NOT NULL UNIQUE,
            template_content TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER
        )
    """)
    print("✓ scoring_templates 表创建/检查完成")
    
    # 插入默认评分模板
    insert_default_templates(cursor)

def insert_default_templates(cursor):
    """插入默认评分模板"""
    
    templates = [
        ("教案", "教案评分模板"),
        ("教学反思", "教学反思评分模板"),
        ("教研/听课记录", "教研听课记录评分模板"),
        ("成绩/学情分析", "成绩学情分析评分模板"),
        ("课件", "课件评分模板")
    ]
    
    for file_type, description in templates:
        cursor.execute("""
            INSERT OR IGNORE INTO scoring_templates (file_type, template_content, is_active)
            VALUES (?, ?, 1)
        """, (file_type, json.dumps({
            "description": description,
            "scoring_criteria": [
                {"name": "内容完整性", "max_score": 25},
                {"name": "逻辑清晰度", "max_score": 25},
                {"name": "专业准确性", "max_score": 25},
                {"name": "创新性", "max_score": 25}
            ],
            "veto_items": [
                "内容造假或抄袭",
                "存在严重知识性错误",
                "完全偏离主题"
            ]
        }, ensure_ascii=False)))
    
    print("✓ 默认评分模板插入完成")

def main():
    """主函数"""
    
    print("=" * 60)
    print("DeepSeek 自动评分系统 - 数据库迁移工具")
    print("=" * 60)
    
    # 数据库路径列表
    db_paths = [
        "app/evaluation_system.db",
        "evaluation_system.db",
        "../evaluation_system.db"
    ]
    
    # 查找所有数据库文件并迁移
    found_dbs = []
    for path in db_paths:
        if os.path.exists(path):
            found_dbs.append(path)
    
    if not found_dbs:
        print("❌ 未找到数据库文件，请确保在正确的目录下运行此脚本")
        print("预期路径:")
        for path in db_paths:
            print(f"  - {path}")
        return False
    
    print(f"找到 {len(found_dbs)} 个数据库文件:")
    for db_path in found_dbs:
        print(f"  - {db_path}")
    
    # 迁移所有数据库文件
    all_success = True
    for db_path in found_dbs:
        print(f"\n处理数据库: {db_path}")
        
        # 备份数据库
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✓ 数据库已备份到: {backup_path}")
        except Exception as e:
            print(f"⚠️ 备份失败: {e}")
            continue
        
        # 执行迁移
        success = migrate_database(db_path)
        if not success:
            all_success = False
    
    success = all_success
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 所有数据库迁移成功完成！")
        print("=" * 60)
        print("\n现在可以使用 DeepSeek 自动评分功能了。")
        print("\n下一步:")
        print("1. 重启后端服务")
        print("2. 测试评分功能")
        print("3. 查看评分结果")
    else:
        print("\n" + "=" * 60)
        print("❌ 部分或全部数据库迁移失败")
        print("=" * 60)
        print("\n请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    main()