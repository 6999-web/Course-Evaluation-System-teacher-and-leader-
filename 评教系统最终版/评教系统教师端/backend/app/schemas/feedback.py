from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FeedbackItem(BaseModel):
    """反馈项"""
    id: int
    evaluation_id: int
    course_name: str
    content: str
    feedback_type: str
    status: str
    submit_date: datetime
    process_date: Optional[datetime] = None
    process_by: Optional[str] = None

    class Config:
        from_attributes = True
