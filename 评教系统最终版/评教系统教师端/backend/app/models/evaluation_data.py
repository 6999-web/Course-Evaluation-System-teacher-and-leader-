from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.models.base import Base


class EvaluationData(Base):
    __tablename__ = "evaluation_data"
    
    record_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="记录唯一标识")
    task_id = Column(String(50), ForeignKey("evaluation_tasks.task_id"), index=True, comment="关联评教任务ID")
    student_hash = Column(String(100), index=True, comment="学生匿名标识")
    dimension_scores = Column(Text, comment="各维度得分（如：教学态度：95）")
    text_feedback = Column(Text, comment="学生文字反馈")
    submission_time = Column(DateTime, default=datetime.utcnow, comment="提交时间")
    validity_flag = Column(Boolean, default=True, comment="有效性标识（true/false）")
    validity_reason = Column(Text, nullable=True, comment="有效性原因")
    
    # 关系
    task = relationship("EvaluationTask", back_populates="evaluation_data")
