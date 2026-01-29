from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImprovementItem(BaseModel):
    """改进建议项"""
    id: int
    suggestion_content: str
    suggestion_type: str
    priority: str
    status: str
    generate_date: datetime
    implement_date: Optional[datetime] = None
    implement_by: Optional[str] = None

    class Config:
        from_attributes = True
