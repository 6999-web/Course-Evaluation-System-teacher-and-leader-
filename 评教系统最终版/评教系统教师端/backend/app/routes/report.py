from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.report import ReportItem
from app.services.report_service import ReportService

router = APIRouter()
report_service = ReportService()


@router.get("/list", response_model=List[ReportItem])
async def get_report_list(
    skip: int = 0,
    limit: int = 10,
    type: str = Query(None, description="报告类型"),
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    return report_service.get_report_list(db, skip, limit, type)


@router.get("/generate")
async def generate_report(
    report_type: str,
    parameters: dict,
    db: Session = Depends(get_db)
):
    """生成报告"""
    return report_service.generate_report(db, report_type, parameters)
