"""检查数据库位置"""
import sys
import os
sys.path.insert(0, '评教系统最终版/评教系统管理端/backend_8fMBP/backend')

from app.database import engine
from app.models import User
from app.auth import verify_password
from sqlalchemy.orm import Session

print(f"数据库URL: {engine.url}")
print(f"数据库文件: {engine.url.database}")

# 检查文件是否存在
db_file = engine.url.database
if os.path.exists(db_file):
    print(f"✓ 数据库文件存在: {db_file}")
    print(f"  文件大小: {os.path.getsize(db_file)} bytes")
else:
    print(f"✗ 数据库文件不存在: {db_file}")

# 查询admin用户
from app.database import SessionLocal
db = SessionLocal()
admin = db.query(User).filter(User.username == "admin").first()

if admin:
    print(f"\n✓ Admin用户存在")
    print(f"  ID: {admin.id}")
    print(f"  用户名: {admin.username}")
    print(f"  密码哈希: {admin.hashed_password[:80]}")
    
    # 测试密码
    result = verify_password("admin123", admin.hashed_password)
    print(f"\n密码验证 'admin123': {result}")
else:
    print(f"\n✗ Admin用户不存在")

db.close()
