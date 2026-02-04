"""
自动评分系统数据库迁移脚本

此脚本用于将现有数据库升级以支持自动评分系统功能
包括：
1. 创建7个新数据表
2. 为现有表添加新字段
3. 初始化默认配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
from models import (
    ScoringTemplate, ScoringRecord, ScoringAppeal, ReviewRecord,
    BonusItem, ScoringLog, SystemScoringConfig,
    MaterialSubmission, EvaluationAssignmentTask
)
import json
from datetime import datetime

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def check_column_exists(table_name: str, column_name: str) -> bool:
    """检查表中是否存在指定列"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_column_if_not_exists(table_name: str, column_name: str, column_definition: str):
    """如果列不存在则添加"""
    if not check_column_exists(table_name, column_name):
        with engine.connect() as conn:
            try:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"))
                conn.commit()
                print(f"✓ 已添加列: {table_name}.{column_name}")
            except Exception as e:
                print(f"✗ 添加列失败 {table_name}.{column_name}: {str(e)}")
    else:
        print(f"○ 列已存在: {table_name}.{column_name}")


def migrate_database():
    """执行数据库迁移"""
    print("=" * 60)
    print("开始数据库迁移 - 自动评分系统")
    print("=" * 60)
    
    # 步骤1: 创建新表
    print("\n[步骤1] 创建新数据表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ 所有数据表已创建或已存在")
    except Exception as e:
        print(f"✗ 创建数据表失败: {str(e)}")
        return False
    
    # 步骤2: 为现有表添加新字段
    print("\n[步骤2] 为现有表添加新字段...")
    
    # MaterialSubmission 表新增字段
    print("\n  MaterialSubmission 表:")
    add_column_if_not_exists("material_submissions", "scoring_status", "VARCHAR(20) DEFAULT 'pending'")
    add_column_if_not_exists("material_submissions", "parsed_content", "TEXT")
    add_column_if_not_exists("material_submissions", "file_hash", "VARCHAR(64)")
    add_column_if_not_exists("material_submissions", "encrypted_path", "VARCHAR(500)")
    
    # EvaluationAssignmentTask 表新增字段
    print("\n  EvaluationAssignmentTask 表:")
    add_column_if_not_exists("evaluation_assignment_tasks", "required_file_types", "TEXT")
    add_column_if_not_exists("evaluation_assignment_tasks", "bonus_enabled", "BOOLEAN DEFAULT 1")
    add_column_if_not_exists("evaluation_assignment_tasks", "max_bonus_score", "FLOAT DEFAULT 10")
    add_column_if_not_exists("evaluation_assignment_tasks", "auto_scoring_enabled", "BOOLEAN DEFAULT 1")
    
    # 步骤3: 初始化系统配置
    print("\n[步骤3] 初始化系统配置...")
    db = SessionLocal()
    try:
        # 检查是否已存在配置
        existing_config = db.query(SystemScoringConfig).filter(
            SystemScoringConfig.config_key == "deepseek_api"
        ).first()
        
        if not existing_config:
            # 创建 Deepseek API 配置
            api_config = SystemScoringConfig(
                config_key="deepseek_api",
                config_value=json.dumps({
                    "api_url": "https://api.deepseek.com/v1/chat/completions",
                    "api_key": "sk-b6ca926900534f1fa31067d49980ec56",
                    "model": "deepseek-chat",
                    "temperature": 0.1,
                    "max_retries": 3,
                    "timeout": 30
                }),
                description="Deepseek API 配置",
                is_trial_mode=True
            )
            db.add(api_config)
            print("✓ 已创建 Deepseek API 配置")
        else:
            print("○ Deepseek API 配置已存在")
        
        # 创建试运行模式配置
        trial_config = db.query(SystemScoringConfig).filter(
            SystemScoringConfig.config_key == "trial_mode"
        ).first()
        
        if not trial_config:
            trial_config = SystemScoringConfig(
                config_key="trial_mode",
                config_value=json.dumps({
                    "enabled": True,
                    "require_full_review": True,
                    "start_date": datetime.now().isoformat(),
                    "duration_days": 30
                }),
                description="试运行模式配置",
                is_trial_mode=True
            )
            db.add(trial_config)
            print("✓ 已创建试运行模式配置")
        else:
            print("○ 试运行模式配置已存在")
        
        # 创建评分规则配置
        scoring_rules = db.query(SystemScoringConfig).filter(
            SystemScoringConfig.config_key == "scoring_rules"
        ).first()
        
        if not scoring_rules:
            scoring_rules = SystemScoringConfig(
                config_key="scoring_rules",
                config_value=json.dumps({
                    "grade_standards": {
                        "excellent": {"min": 90, "max": 100},
                        "good": {"min": 80, "max": 89},
                        "pass": {"min": 60, "max": 79},
                        "fail": {"min": 0, "max": 59}
                    },
                    "max_bonus_score": 10,
                    "veto_items": {
                        "general": ["造假", "师德失范", "未提交核心文件"]
                    }
                }),
                description="评分规则配置",
                is_trial_mode=False
            )
            db.add(scoring_rules)
            print("✓ 已创建评分规则配置")
        else:
            print("○ 评分规则配置已存在")
        
        db.commit()
        print("✓ 系统配置初始化完成")
        
    except Exception as e:
        db.rollback()
        print(f"✗ 初始化系统配置失败: {str(e)}")
        return False
    finally:
        db.close()
    
    # 步骤4: 验证迁移结果
    print("\n[步骤4] 验证迁移结果...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        "scoring_templates",
        "scoring_records",
        "scoring_appeals",
        "review_records",
        "bonus_items",
        "scoring_logs",
        "system_scoring_config"
    ]
    
    all_tables_exist = True
    for table in required_tables:
        if table in tables:
            print(f"✓ 表存在: {table}")
        else:
            print(f"✗ 表缺失: {table}")
            all_tables_exist = False
    
    if all_tables_exist:
        print("\n" + "=" * 60)
        print("✓ 数据库迁移成功完成！")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("✗ 数据库迁移未完全成功，请检查错误信息")
        print("=" * 60)
        return False


def rollback_migration():
    """回滚迁移（仅用于开发测试）"""
    print("=" * 60)
    print("警告：即将回滚数据库迁移")
    print("=" * 60)
    
    confirm = input("确认要删除所有自动评分系统相关表吗？(yes/no): ")
    if confirm.lower() != "yes":
        print("已取消回滚操作")
        return
    
    with engine.connect() as conn:
        try:
            # 删除新创建的表
            tables_to_drop = [
                "scoring_logs",
                "bonus_items",
                "review_records",
                "scoring_appeals",
                "scoring_records",
                "scoring_templates",
                "system_scoring_config"
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    print(f"✓ 已删除表: {table}")
                except Exception as e:
                    print(f"✗ 删除表失败 {table}: {str(e)}")
            
            conn.commit()
            print("\n✓ 回滚完成")
            
        except Exception as e:
            print(f"✗ 回滚失败: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="自动评分系统数据库迁移工具")
    parser.add_argument("--rollback", action="store_true", help="回滚迁移（删除所有相关表）")
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
    else:
        success = migrate_database()
        sys.exit(0 if success else 1)
