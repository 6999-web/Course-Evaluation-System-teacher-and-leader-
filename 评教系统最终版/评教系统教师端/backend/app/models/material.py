"""
材料分发与提交相关数据模型
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, Float
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


class EvaluationTaskModel(Base):
    """考评任务模型"""
    __tablename__ = "evaluation_form_tasks"
    
    task_id = Column(String, primary_key=True)
    template_id = Column(String(50), nullable=False, index=True)
    teacher_id = Column(String(50), nullable=False, index=True)
    
    # 考评表信息
    template_name = Column(String(200), nullable=False)
    template_file_url = Column(String(500), nullable=False)
    template_file_type = Column(String(20))  # pdf, excel, word
    
    # 提交要求
    submission_requirements = Column(JSON)  # {"file_types": ["pdf", "excel"], "max_files": 3, "description": "..."}
    scoring_criteria = Column(JSON)  # [{"name": "完成度", "max_score": 10}, ...]
    total_score = Column(Integer, default=100)
    
    # 任务状态
    status = Column(String(20), default="pending")  # pending, submitted, scored, completed
    deadline = Column(DateTime, nullable=False)
    
    # 查收状态
    is_viewed = Column(Boolean, default=False)  # 是否已查收（点击查看按钮）
    viewed_at = Column(DateTime, nullable=True)  # 查收时间
    
    # 提交信息
    submitted_files = Column(JSON)  # [{"file_id": "xxx", "file_name": "xxx", "file_size": 123, "file_url": "xxx"}, ...]
    submitted_at = Column(DateTime, nullable=True)
    submission_notes = Column(Text)
    
    # 评分信息
    scores = Column(JSON)  # {"完成度": 8, "准确性": 9, "规范性": 7}
    final_score = Column(Float, nullable=True)
    scoring_feedback = Column(Text)
    scored_at = Column(DateTime, nullable=True)
    
    # 修改记录
    score_history = Column(JSON)  # [{"old_score": 20, "new_score": 25, "reason": "...", "changed_at": "...", "changed_by": "..."}, ...]
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
