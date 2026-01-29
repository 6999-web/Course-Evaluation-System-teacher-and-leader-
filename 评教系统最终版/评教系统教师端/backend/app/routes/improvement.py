from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.improvement import ImprovementItem
from app.services.improvement_service import ImprovementService

router = APIRouter()
improvement_service = ImprovementService()


@router.get("/suggestions", response_model=List[ImprovementItem])
async def get_improvement_suggestions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取改进建议列表"""
    return improvement_service.get_improvement_suggestions(db, skip, limit)


@router.post("/implement/{suggestion_id}")
async def implement_improvement(
    suggestion_id: int,
    db: Session = Depends(get_db)
):
    """实施改进建议"""
    return improvement_service.implement_improvement(db, suggestion_id)
