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
        print(f"收到分发同步请求: material_id={data.material_id}, teacher_id={data.teacher_id}, material_name={data.material_name}")
        
        # 检查是否已存在
        existing = db.query(DistributedMaterial).filter(
            DistributedMaterial.material_id == data.material_id,
            DistributedMaterial.teacher_id == data.teacher_id
        ).first()
        
        if existing:
            print(f"材料已存在，跳过: {data.material_id}")
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
        
        # 创建分发材料记录 - 确保字段顺序正确
        material = DistributedMaterial(
            material_id=data.material_id,      # ✅ 材料ID
            teacher_id=data.teacher_id,        # ✅ 教师ID
            material_name=data.material_name,  # ✅ 材料名称
            material_type=data.material_type,  # ✅ 材料类型
            file_url=data.file_url,            # ✅ 文件URL
            file_size=0,                       # 可以后续更新
            distributed_at=distributed_at,     # ✅ 分发时间
            is_viewed=False                    # ✅ 是否已查看
        )
        
        db.add(material)
        db.commit()
        
        print(f"✅ 材料同步成功: {data.material_name} -> {data.teacher_id}")
        
        return {"message": "同步成功"}
        
    except Exception as e:
        db.rollback()
        print(f"❌ 同步失败: {str(e)}")
        import traceback
        traceback.print_exc()
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



class EvaluationTaskSyncRequest(BaseModel):
    """考评任务同步请求"""
    task_id: str
    template_id: str
    teacher_id: str
    template_name: str
    template_file_url: str
    template_file_type: str
    submission_requirements: dict = {}
    scoring_criteria: list = []
    total_score: int = 100
    deadline: str


@router.post("/sync-evaluation-task", response_model=dict)
async def sync_evaluation_task(
    data: EvaluationTaskSyncRequest,
    db: Session = Depends(get_db)
):
    """
    接收管理端的考评任务分配信息
    """
    try:
        from app.models.material import EvaluationTaskModel
        
        # 检查是否已存在
        existing = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == data.task_id
        ).first()
        
        if existing:
            return {"message": "考评任务已存在"}
        
        # 解析截止时间
        try:
            deadline = datetime.fromisoformat(data.deadline.replace('Z', '+00:00'))
        except Exception:
            try:
                if '.' in data.deadline:
                    base_time = data.deadline.split('.')[0]
                    deadline = datetime.fromisoformat(base_time)
                else:
                    deadline = datetime.fromisoformat(data.deadline)
            except Exception:
                deadline = datetime.now()
        
        # 创建考评任务
        task = EvaluationTaskModel(
            task_id=data.task_id,
            template_id=data.template_id,
            teacher_id=data.teacher_id,
            template_name=data.template_name,
            template_file_url=data.template_file_url,
            template_file_type=data.template_file_type,
            submission_requirements=data.submission_requirements or {},
            scoring_criteria=data.scoring_criteria or [],
            total_score=data.total_score,
            status="pending",
            deadline=deadline,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(task)
        db.commit()
        
        print(f"考评任务同步成功: {data.task_id}")
        return {"message": "考评任务同步成功"}
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )



class EvaluationScoreSyncRequest(BaseModel):
    """考评评分同步请求"""
    task_id: str
    template_id: str
    teacher_id: str
    scores: dict = {}
    total_score: float
    scoring_feedback: str = ""
    scored_at: str


@router.post("/sync-evaluation-score", response_model=dict)
async def sync_evaluation_score(
    data: EvaluationScoreSyncRequest,
    db: Session = Depends(get_db)
):
    """
    接收管理端的考评评分信息
    """
    try:
        from app.models.material import EvaluationTaskModel
        
        # 查找考评任务
        task = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == data.task_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 解析评分时间
        try:
            scored_at = datetime.fromisoformat(data.scored_at.replace('Z', '+00:00'))
        except Exception:
            try:
                if '.' in data.scored_at:
                    base_time = data.scored_at.split('.')[0]
                    scored_at = datetime.fromisoformat(base_time)
                else:
                    scored_at = datetime.fromisoformat(data.scored_at)
            except Exception:
                scored_at = datetime.now()
        
        # 更新任务评分信息
        task.scores = data.scores
        task.final_score = data.total_score
        task.scoring_feedback = data.scoring_feedback
        task.scored_at = scored_at
        task.status = "scored"
        task.updated_at = datetime.now()
        
        db.commit()
        
        print(f"考评评分同步成功: {data.task_id}")
        return {"message": "考评评分同步成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )
