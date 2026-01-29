"""
Pydantic 数据模型
用于请求验证和响应序列化
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名，3-50个字符")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码，至少6个字符")
    confirm_password: str = Field(..., description="确认密码")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """验证用户名只包含字母、数字和下划线"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少为6个字符')
        
        # 检查是否包含数字和字母
        has_digit = any(char.isdigit() for char in v)
        has_letter = any(char.isalpha() for char in v)
        
        if not (has_digit and has_letter):
            raise ValueError('密码必须包含字母和数字')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证两次密码是否一致"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """JWT 令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class UserResponse(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True  # Pydantic v2 使用 from_attributes 替代 orm_mode


class LoginResponse(BaseModel):
    """登录响应模型"""
    message: str = Field(..., description="响应消息")
    token: Token
    user: UserResponse


class RegisterResponse(BaseModel):
    """注册响应模型"""
    message: str = Field(..., description="响应消息")
    user: UserResponse


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="响应消息")
    detail: Optional[str] = Field(None, description="详细信息")


# ==================== 材料分发与回收相关 Schemas ====================

from typing import List
from datetime import date


class EvaluationFormCreate(BaseModel):
    """考评表创建请求模型"""
    name: str = Field(..., min_length=1, max_length=200, description="考评表名称")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    dimensions: List[str] = Field(..., min_items=1, description="评分维度列表")
    participants: List[str] = Field(..., min_items=1, description="参与者ID列表")
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        """验证结束日期必须在开始日期之后"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须在开始日期之后')
        return v


class EvaluationFormResponse(BaseModel):
    """考评表响应模型"""
    form_id: str
    name: str
    start_date: datetime
    end_date: datetime
    dimensions: List[str]
    participants: List[str]
    form_data: dict
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    status: str
    
    class Config:
        from_attributes = True


class MaterialDistributeRequest(BaseModel):
    """材料分发请求模型"""
    material_ids: List[str] = Field(..., min_items=1, description="材料ID列表")
    material_types: List[str] = Field(..., min_items=1, description="材料类型列表")
    distribution_type: str = Field(..., description="分发类型: batch 或 targeted")
    target_teachers: List[str] = Field(default=[], description="目标教师ID列表（定向分发时必填）")
    
    @validator('distribution_type')
    def validate_distribution_type(cls, v):
        """验证分发类型"""
        if v not in ['batch', 'targeted']:
            raise ValueError('分发类型必须是 batch 或 targeted')
        return v
    
    @validator('target_teachers')
    def validate_target_teachers(cls, v, values):
        """验证定向分发时必须指定目标教师"""
        if 'distribution_type' in values and values['distribution_type'] == 'targeted' and not v:
            raise ValueError('定向分发时必须指定目标教师')
        return v


class DistributionRecordResponse(BaseModel):
    """分发记录响应模型"""
    distribution_id: str
    material_id: str
    material_type: str
    material_name: str
    distribution_type: str
    target_teachers: List[dict]
    distributed_by: Optional[int]
    distributed_at: datetime
    status: str
    
    class Config:
        from_attributes = True


class MaterialSubmissionResponse(BaseModel):
    """材料提交响应模型"""
    submission_id: str
    teacher_id: str
    teacher_name: str
    files: List[dict]
    notes: Optional[str]
    submitted_at: datetime
    review_status: str
    review_feedback: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReviewStatusUpdate(BaseModel):
    """审核状态更新请求模型"""
    status: str = Field(..., description="审核状态: approved, rejected, needs_revision")
    feedback: Optional[str] = Field(None, description="审核反馈")
    
    @validator('status')
    def validate_status(cls, v):
        """验证审核状态"""
        if v not in ['approved', 'rejected', 'needs_revision']:
            raise ValueError('审核状态必须是 approved, rejected 或 needs_revision')
        return v
