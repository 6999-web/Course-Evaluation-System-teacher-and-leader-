"""
认证相关路由
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import os

from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# 临时用户存储（实际应该从数据库查询）
USERS_DB = {
    "teacher_001": {
        "username": "teacher_001",
        "password": "teacher123",
        "full_name": "张三",
        "email": "teacher@example.com"
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    full_name: str
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建JWT令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=12)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    用户登录
    
    - 验证用户名和密码
    - 返回JWT令牌
    """
    user = USERS_DB.get(credentials.username)
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user["username"],
            "full_name": user["full_name"],
            "email": user["email"]
        }
    )


@router.post("/register", response_model=LoginResponse)
async def register(credentials: RegisterRequest):
    """
    用户注册
    
    - 创建新用户账户
    - 返回JWT令牌
    """
    # 检查用户名是否已存在
    if credentials.username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查密码确认
    if credentials.password != credentials.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )
    
    # 创建新用户
    USERS_DB[credentials.username] = {
        "username": credentials.username,
        "password": credentials.password,
        "full_name": credentials.full_name,
        "email": credentials.email
    }
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": credentials.username,
            "full_name": credentials.full_name,
            "email": credentials.email
        }
    )


@router.get("/me")
async def get_current_user(token: str = None):
    """
    获取当前用户信息
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供令牌"
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌无效"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效"
        )
    
    user = USERS_DB.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"]
    }
