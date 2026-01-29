"""
材料相关的 Pydantic 模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MaterialResponse(BaseModel):
    """分发材料响应模型"""
    material_id: str
    material_name: str
    material_type: str
    file_url: str
    distributed_time: datetime
    is_viewed: bool
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    file_id: str
    file_name: str
    file_size: int
    upload_time: datetime


class MaterialSubmitRequest(BaseModel):
    """材料提交请求模型"""
    file_ids: List[str] = Field(..., min_items=1, description="文件ID列表")
    notes: Optional[str] = Field(None, description="备注")


class SubmissionResponse(BaseModel):
    """提交记录响应模型"""
    submission_id: str
    files: List[dict]
    submission_time: datetime
    review_status: str
    review_feedback: Optional[str]
    review_time: Optional[datetime]
    
    class Config:
        from_attributes = True
