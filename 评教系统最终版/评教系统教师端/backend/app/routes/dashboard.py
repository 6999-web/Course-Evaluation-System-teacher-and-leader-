from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.dashboard import DashboardStats, RecentEvaluation
from app.services.dashboard_service import DashboardService

router = APIRouter()
dashboard_service = DashboardService()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    return dashboard_service.get_dashboard_stats(db)


@router.get("/recent-evaluations", response_model=List[RecentEvaluation])
async def get_recent_evaluations(limit: int = 5, db: Session = Depends(get_db)):
    """获取最近的评估记录"""
    return dashboard_service.get_recent_evaluations(db, limit)
