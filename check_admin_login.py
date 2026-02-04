"""检查admin用户登录问题"""
import sys
sys.path.insert(0, '评教系统最终版/评教系统管理端/backend_8fMBP/backend')

from app.database import SessionLocal
from app.models import User
from app.auth import verify_password, get_password_hash

db = SessionLocal()

# 查找admin用户
admin = db.query(User).filter(User.username == "admin").first()

if admin:
    print(f"✓ Admin用户存在")
    print(f"  用户名: {admin.username}")
    print(f"  角色: {admin.role}")
    print(f"  激活状态: {admin.is_active}")
    print(f"  密码哈希: {admin.hashed_password[:50]}...")
    
    # 测试密码验证
    test_passwords = ["admin123", "123456", "admin"]
    print(f"\n密码验证测试:")
    for pwd in test_passwords:
        result = verify_password(pwd, admin.hashed_password)
        print(f"  {pwd}: {'✓ 正确' if result else '✗ 错误'}")
    
    # 如果所有密码都不对，重置为admin123
    if not verify_password("admin123", admin.hashed_password):
        print(f"\n⚠ 密码不匹配，重置为 admin123")
        admin.hashed_password = get_password_hash("admin123")
        db.commit()
        print(f"✓ 密码已重置")
        
        # 再次验证
        if verify_password("admin123", admin.hashed_password):
            print(f"✓ 验证成功: admin123")
else:
    print(f"✗ Admin用户不存在，创建新用户")
    from app.models import UserRoleEnum
    
    new_admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRoleEnum.admin,
        is_active=True
    )
    db.add(new_admin)
    db.commit()
    print(f"✓ Admin用户已创建，密码: admin123")

db.close()
