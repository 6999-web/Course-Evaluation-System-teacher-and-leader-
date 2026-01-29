from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class EvaluationTask(Base):
    __tablename__ = "evaluation_tasks"
    
    task_id = Column(String(50), primary_key=True, index=True, comment="任务ID（格式：2024-1-T001）")
    course_id = Column(String(50), index=True, comment="关联课程ID（对接教务系统）")
    teacher_id = Column(String(50), index=True, comment="授课教师ID")
    student_count = Column(Integer, comment="应评学生数")
    completed_count = Column(Integer, default=0, comment="已评学生数")
    quality_score = Column(Float, default=0.0, comment="数据质量评分（0-100）")
    
    # 关系
    evaluation_data = relationship("EvaluationData", back_populates="task")
