"""重置admin密码"""
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash, verify_password

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
    
    # 验证
    if verify_password(new_password, admin.hashed_password):
        print(f"✓ 密码验证成功")
    else:
        print(f"✗ 密码验证失败")
else:
    print("✗ Admin用户不存在")

db.close()
