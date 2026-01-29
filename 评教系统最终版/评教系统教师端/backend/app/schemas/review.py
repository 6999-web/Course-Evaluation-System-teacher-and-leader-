from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReviewItem(BaseModel):
    """审核项"""
    id: int
    item_type: str
    item_id: int
    content: str
    status: str
    submit_date: datetime
    review_date: Optional[datetime] = None
    review_result: Optional[str] = None
    review_by: Optional[str] = None

    class Config:
        from_attributes = True
