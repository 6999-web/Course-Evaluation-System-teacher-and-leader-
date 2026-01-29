from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.evaluation import EvaluationTask, EvaluationData
from app.services.evaluation_service import EvaluationService

router = APIRouter()
evaluation_service = EvaluationService()


@router.get("/tasks", response_model=List[EvaluationTask])
async def get_evaluation_tasks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取评估任务列表"""
    return evaluation_service.get_evaluation_tasks(db, skip, limit)


@router.get("/tasks/{task_id}", response_model=EvaluationTask)
async def get_evaluation_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """获取评估任务详情"""
    return evaluation_service.get_evaluation_task(db, task_id)


@router.get("/data", response_model=List[EvaluationData])
async def get_evaluation_data(
    task_id: int = Query(None, description="评估任务ID"),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取评估数据列表"""
    return evaluation_service.get_evaluation_data(db, task_id, skip, limit)
