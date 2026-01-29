"""
管理端同步数据接口
用于接收管理端的分发和审核信息
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.material import DistributedMaterial, TeacherSubmission

router = APIRouter(prefix="/admin", tags=["管理端同步"])


class DistributionSyncRequest(BaseModel):
    """分发同步请求"""
    material_id: str
    teacher_id: str
    material_name: str
    material_type: str
    file_url: str
    distributed_at: str


class ReviewSyncRequest(BaseModel):
    """审核同步请求"""
    submission_id: str
    status: str
    feedback: Optional[str] = None
    reviewed_at: str


@router.post("/sync-distribution", response_model=dict)
async def sync_distribution(
    data: DistributionSyncRequest,
    db: Session = Depends(get_db)
):
    """
    接收管理端的材料分发信息
    """
    try:
        # 检查是否已存在
        existing = db.query(DistributedMaterial).filter(
            DistributedMaterial.material_id == data.material_id,
            DistributedMaterial.teacher_id == data.teacher_id
        ).first()
        
        if existing:
            return {"message": "材料已存在"}
        
        # 解析分发时间 - 支持多种格式
        distributed_at = None
        try:
            # 尝试标准ISO格式
            distributed_at = datetime.fromisoformat(data.distributed_at.replace('Z', '+00:00'))
        except Exception as e1:
            try:
                # 尝试去掉微秒的格式
                if '.' in data.distributed_at:
                    base_time = data.distributed_at.split('.')[0]
                    distributed_at = datetime.fromisoformat(base_time)
                else:
                    distributed_at = datetime.fromisoformat(data.distributed_at)
            except Exception as e2:
                # 如果都失败，使用当前时间
                distributed_at = datetime.now()
        
        # 创建分发材料记录
        material = DistributedMaterial(
            material_id=data.material_id,
            teacher_id=data.teacher_id,
            material_name=data.material_name,
            material_type=data.material_type,
            file_url=data.file_url,
            file_size=0,  # 可以后续更新
            distributed_at=distributed_at,
            is_viewed=False
        )
        
        db.add(material)
        db.commit()
        
        return {"message": "同步成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )


@router.put("/sync-review", response_model=dict)
async def sync_review_status(
    data: ReviewSyncRequest,
    db: Session = Depends(get_db)
):
    """
    接收管理端的审核状态更新
    """
    try:
        # 查找提交记录
        submission = db.query(TeacherSubmission).filter(
            TeacherSubmission.submission_id == data.submission_id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提交记录不存在"
            )
        
        # 更新审核状态
        submission.review_status = data.status
        submission.review_feedback = data.feedback
        submission.reviewed_at = datetime.fromisoformat(data.reviewed_at.replace('Z', '+00:00'))
        
        db.commit()
        
        return {"message": "审核状态同步成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )


@router.get("/submission/{submission_id}", response_model=dict)
async def get_submission(
    submission_id: str,
    db: Session = Depends(get_db)
):
    """
    供管理端查询提交信息
    """
    submission = db.query(TeacherSubmission).filter(
        TeacherSubmission.submission_id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    return {
        "submission_id": submission.submission_id,
        "teacher_id": submission.teacher_id,
        "files": submission.files,
        "notes": submission.notes,
        "submitted_at": submission.submitted_at.isoformat(),
        "review_status": submission.review_status
    }
