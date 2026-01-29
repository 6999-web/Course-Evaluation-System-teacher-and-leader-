from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class EvaluationTask(BaseModel):
    """评估任务"""
    id: int
    task_name: str
    start_date: datetime
    end_date: datetime
    status: str
    total_students: int
    completed_students: int
    completion_rate: float

    class Config:
        from_attributes = True


class EvaluationData(BaseModel):
    """评估数据"""
    id: int
    task_id: int
    course_id: int
    course_name: str
    teacher_id: int
    teacher_name: str
    score: float
    feedback: Optional[str] = None
    evaluation_date: datetime
    student_id: Optional[int] = None
    student_name: Optional[str] = None

    class Config:
        from_attributes = True
