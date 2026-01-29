from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.appeal import AppealItem
from app.services.appeal_service import AppealService

router = APIRouter()
appeal_service = AppealService()


@router.get("/list", response_model=List[AppealItem])
async def get_appeal_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取申诉列表"""
    return appeal_service.get_appeal_list(db, skip, limit)


@router.post("/submit")
async def submit_appeal(
    appeal_data: dict,
    db: Session = Depends(get_db)
):
    """提交申诉"""
    return appeal_service.submit_appeal(db, appeal_data)


@router.post("/process/{appeal_id}")
async def process_appeal(
    appeal_id: int,
    action: str,
    db: Session = Depends(get_db)
):
    """处理申诉"""
    return appeal_service.process_appeal(db, appeal_id, action)
