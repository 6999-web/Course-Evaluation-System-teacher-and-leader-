"""重置admin密码为admin123"""
import sys
sys.path.insert(0, '评教系统最终版/评教系统管理端/backend_8fMBP/backend')

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()

# 查找admin用户
admin = db.query(User).filter(User.username == "admin").first()

if admin:
    print(f"找到admin用户")
    print(f"  当前密码哈希: {admin.hashed_password[:50]}...")
    
    # 重置密码
    new_password = "admin123"
    admin.hashed_password = get_password_hash(new_password)
    db.commit()
    
    print(f"\n✓ 密码已重置为: {new_password}")
    print(f"  新密码哈希: {admin.hashed_password[:50]}...")
else:
    print("✗ Admin用户不存在")

db.close()
