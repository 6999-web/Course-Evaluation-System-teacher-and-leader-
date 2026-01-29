from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppealItem(BaseModel):
    """申诉项"""
    id: int
    evaluation_id: int
    course_name: str
    appeal_reason: str
    status: str
    submit_date: datetime
    process_date: Optional[datetime] = None
    process_result: Optional[str] = None
    process_by: Optional[str] = None

    class Config:
        from_attributes = True
