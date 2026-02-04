#!/usr/bin/env python3
"""
测试管理员密码
"""

import sqlite3
import os
from passlib.context import CryptContext

# 使用与管理端相同的密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db_path = '评教系统最终版/评教系统管理端/backend_8fMBP/backend/app/evaluation_system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, hashed_password FROM users WHERE username = "admin"')
    user = cursor.fetchone()
    if user:
        username, hashed_password = user
        print(f'用户名: {username}')
        
        # 测试不同密码
        passwords = ["123456", "admin123", "admin", "password"]
        for pwd in passwords:
            try:
                result = pwd_context.verify(pwd, hashed_password)
                print(f'密码 "{pwd}": {result}')
                if result:
                    print(f'✅ 正确密码是: {pwd}')
                    break
            except Exception as e:
                print(f'密码 "{pwd}" 验证错误: {e}')
    else:
        print('未找到admin用户')
    
    conn.close()
else:
    print('数据库文件不存在')