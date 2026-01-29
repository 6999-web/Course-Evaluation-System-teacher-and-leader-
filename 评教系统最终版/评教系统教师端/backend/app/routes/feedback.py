from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.feedback import FeedbackItem
from app.services.feedback_service import FeedbackService

router = APIRouter()
feedback_service = FeedbackService()


@router.get("/list", response_model=List[FeedbackItem])
async def get_feedback_list(
    skip: int = 0,
    limit: int = 10,
    type: str = Query(None, description="反馈类型"),
    db: Session = Depends(get_db)
):
    """获取反馈列表"""
    return feedback_service.get_feedback_list(db, skip, limit, type)


@router.post("/process/{feedback_id}")
async def process_feedback(
    feedback_id: int,
    action: str,
    db: Session = Depends(get_db)
):
    """处理反馈"""
    return feedback_service.process_feedback(db, feedback_id, action)
