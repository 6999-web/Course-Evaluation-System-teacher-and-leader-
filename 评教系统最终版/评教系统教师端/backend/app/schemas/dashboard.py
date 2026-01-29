from pydantic import BaseModel
from datetime import datetime


class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_evaluations: int
    average_score: float
    completion_rate: float
    recent_trend: str
    positive_rate: float
    negative_rate: float
    neutral_rate: float


class RecentEvaluation(BaseModel):
    """最近的评估记录"""
    id: int
    course_name: str
    evaluation_date: datetime
    score: float
    feedback_count: int
    status: str

    class Config:
        from_attributes = True
