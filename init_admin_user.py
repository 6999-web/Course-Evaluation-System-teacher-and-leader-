#!/usr/bin/env python3
"""
初始化管理员账户脚本
"""

import sys
import os

# 添加管理端后端路径到Python路径
sys.path.insert(0, r'评教系统最终版/评教系统管理端/backend_8fMBP/backend')

from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import get_password_hash

def create_admin_user():
    """创建默认管理员账户"""
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员账户
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("✅ 管理员账户已存在")
            print(f"用户名: {existing_admin.username}")
            print(f"邮箱: {existing_admin.email}")
            return
        
        # 创建管理员账户
        admin_user = User(
            username="admin",
            email="admin@system.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 管理员账户创建成功！")
        print("=" * 40)
        print("登录信息:")
        print("用户名: admin")
        print("密码: admin123")
        print("邮箱: admin@system.com")
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ 创建管理员账户失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化管理员账户...")
    create_admin_user()
