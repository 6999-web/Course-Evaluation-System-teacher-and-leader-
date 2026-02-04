"""
认证和授权工具模块
包含密码加密、JWT生成和验证等功能
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production-09876543210"  # 生产环境应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码
    
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    加密密码
    
    Args:
        password: 明文密码
    
    Returns:
        str: 加密后的密码
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌
    
    Args:
        data: 要编码的数据（通常包含用户ID、用户名等）
        expires_delta: 过期时间增量
    
    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT 令牌
    
    Args:
        token: JWT 令牌
    
    Returns:
        dict: 解码后的数据，如果令牌无效则返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（依赖注入函数）
    
    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话
    
    Returns:
        User: 当前用户对象
    
    Raises:
        HTTPException: 如果令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
    
    Returns:
        User: 活跃用户对象
    
    Raises:
        HTTPException: 如果用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user


def require_role(required_role: str):
    """
    角色权限装饰器工厂
    
    Args:
        required_role: 需要的角色
    
    Returns:
        function: 依赖注入函数
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要 {required_role} 角色权限"
            )
        return current_user
    return role_checker
