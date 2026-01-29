"""
材料分发与提交相关数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON
from datetime import datetime
from app.models.base import Base


class DistributedMaterial(Base):
    """分发材料模型"""
    __tablename__ = "distributed_materials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String(50), nullable=False, index=True)
    teacher_id = Column(String(50), nullable=False, index=True)
    material_name = Column(String(200), nullable=False)
    material_type = Column(String(20), nullable=False)  # "file" or "evaluation_form"
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer)
    distributed_at = Column(DateTime, nullable=False)
    is_viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime, nullable=True)


class TeacherSubmission(Base):
    """教师提交模型"""
    __tablename__ = "teacher_submissions"
    
    submission_id = Column(String, primary_key=True)
    teacher_id = Column(String(50), nullable=False, index=True)
    files = Column(JSON, nullable=False)
    notes = Column(Text)
    submitted_at = Column(DateTime, nullable=False)
    review_status = Column(String(20), default="pending")
    review_feedback = Column(Text)
    reviewed_at = Column(DateTime, nullable=True)
    synced_to_admin = Column(Boolean, default=False)  # 是否已同步到管理端
