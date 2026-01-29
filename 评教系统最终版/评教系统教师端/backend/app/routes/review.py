from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.review import ReviewItem
from app.services.review_service import ReviewService

router = APIRouter()
review_service = ReviewService()


@router.get("/list", response_model=List[ReviewItem])
async def get_review_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取审核列表"""
    return review_service.get_review_list(db, skip, limit)


@router.post("/process/{review_id}")
async def process_review(
    review_id: int,
    action: str,
    db: Session = Depends(get_db)
):
    """处理审核"""
    return review_service.process_review(db, review_id, action)
