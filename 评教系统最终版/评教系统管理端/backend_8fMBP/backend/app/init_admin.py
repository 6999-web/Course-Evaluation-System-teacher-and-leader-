#!/usr/bin/env python3
"""
初始化管理员账户脚本
"""

import sys
import os
from sqlalchemy.orm import Session
from database import get_db, engine
from models import User
from auth import get_password_hash

def create_admin_user():
    """创建默认管理员账户"""
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 检查是否已存在管理员账户
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("管理员账户已存在")
            print(f"用户名: {existing_admin.username}")
            print(f"邮箱: {existing_admin.email}")
            return
        
        # 创建管理员账户
        admin_user = User(
            username="admin",
            email="admin@system.com",
            password_hash=get_password_hash("admin123"),
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
        print("请访问前端页面进行登录")
        
    except Exception as e:
        print(f"❌ 创建管理员账户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化管理员账户...")
    create_admin_user()