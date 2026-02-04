"""
材料查看和提交相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import json
import httpx
from datetime import datetime

from app.database import get_db
from app.models.material import DistributedMaterial, TeacherSubmission
from app.schemas.material import (
    MaterialResponse, FileUploadResponse,
    MaterialSubmitRequest, SubmissionResponse
)

router = APIRouter(prefix="/teacher/materials", tags=["材料管理"])

# 临时：模拟当前登录教师ID（实际应从JWT token获取）
CURRENT_TEACHER_ID = "teacher_001"
CURRENT_TEACHER_NAME = "张三"


@router.post("/sync", response_model=dict, status_code=status.HTTP_201_CREATED)
async def sync_distributed_material(
    sync_data: dict,
    db: Session = Depends(get_db)
):
    """
    同步管理端分发的材料
    
    - 接收管理端分发的材料信息
    - 创建材料分发记录
    """
    try:
        # 生成材料ID
        import uuid
        material_id = sync_data.get("material_id") or f"mat_{uuid.uuid4().hex[:8]}"
        
        # 处理distributed_at字段
        distributed_at = sync_data.get("distributed_at")
        if distributed_at:
            if isinstance(distributed_at, str):
                distributed_at = datetime.fromisoformat(distributed_at)
            elif isinstance(distributed_at, datetime):
                pass  # 已经是datetime对象
            else:
                distributed_at = datetime.utcnow()
        else:
            distributed_at = datetime.utcnow()
        
        # 创建分发记录
        material = DistributedMaterial(
            material_id=material_id,
            material_name=sync_data.get("material_name"),
            material_type=sync_data.get("material_type"),
            file_url=sync_data.get("file_url", ""),
            teacher_id=sync_data.get("teacher_id"),
            distributed_by=sync_data.get("distributed_by"),
            distributed_at=distributed_at
        )
        
        db.add(material)
        db.commit()
        db.refresh(material)
        
        return {
            "message": "材料分发同步成功",
            "material_id": material.material_id
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步材料分发失败: {str(e)}"
        )


@router.get("", response_model=dict)
async def get_distributed_materials(
    db: Session = Depends(get_db)
):
    """
    获取分发给当前教师的材料列表
    """
    try:
        materials = db.query(DistributedMaterial).filter(
            DistributedMaterial.teacher_id == CURRENT_TEACHER_ID
        ).order_by(DistributedMaterial.distributed_at.desc()).all()
        
        materials_data = []
        for material in materials:
            materials_data.append({
                "material_id": material.material_id,
                "material_name": material.material_name,
                "material_type": material.material_type,
                "file_url": material.file_url,
                "distributed_time": material.distributed_at.isoformat(),
                "is_viewed": material.is_viewed
            })
        
        return {
            "materials": materials_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取材料列表失败: {str(e)}"
        )


@router.get("/{material_id}/download")
async def download_material(
    material_id: str,
    db: Session = Depends(get_db)
):
    """
    下载材料文件
    """
    try:
        # 查找材料记录
        material = db.query(DistributedMaterial).filter(
            DistributedMaterial.material_id == material_id,
            DistributedMaterial.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="材料不存在或无权访问"
            )
        
        # 标记为已查看
        if not material.is_viewed:
            material.is_viewed = True
            material.viewed_at = datetime.utcnow()
            db.commit()
        
        # 构建文件路径
        file_path = material.file_url
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return FileResponse(
            path=file_path,
            filename=material.material_name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传文件
    
    - 验证文件类型和大小
    - 保存文件到服务器
    - 返回文件ID和元信息
    """
    try:
        # 验证文件类型
        allowed_types = ['pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg']
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型。允许的类型: {', '.join(allowed_types)}"
            )
        
        # 验证文件大小（50MB限制）
        max_size = 50 * 1024 * 1024  # 50MB
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（最大50MB）"
            )
        
        # 生成唯一文件ID
        file_id = f"{CURRENT_TEACHER_ID}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}_{file.filename}"
        
        # 创建上传目录
        upload_dir = f"uploads/submissions/{CURRENT_TEACHER_ID}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, file_id)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return FileUploadResponse(
            file_id=file_id,
            file_name=file.filename,
            file_size=file_size,
            upload_time=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )


@router.post("/submit", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_materials(
    submit_data: MaterialSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    提交材料
    
    - 接收文件ID列表和备注
    - 验证文件列表非空
    - 创建提交记录
    - 调用管理端API同步提交信息
    """
    try:
        # 验证文件是否存在
        files_info = []
        upload_dir = f"uploads/submissions/{CURRENT_TEACHER_ID}"
        
        for file_id in submit_data.file_ids:
            file_path = os.path.join(upload_dir, file_id)
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"文件 {file_id} 不存在"
                )
            
            file_size = os.path.getsize(file_path)
            files_info.append({
                "file_id": file_id,
                "file_name": file_id.split('_')[-1],  # 提取原始文件名
                "file_size": file_size,
                "file_url": file_path
            })
        
        # 生成提交ID
        submission_id = f"sub_{uuid.uuid4().hex[:8]}"
        
        # 创建提交记录
        submission = TeacherSubmission(
            submission_id=submission_id,
            teacher_id=CURRENT_TEACHER_ID,
            files=files_info,
            notes=submit_data.notes,
            submitted_at=datetime.utcnow(),
            review_status="pending",
            synced_to_admin=False
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # 【修改】异步调用同步服务，不阻塞返回
        import asyncio
        from app.services.admin_sync_service import sync_submission_to_admin
        
        # 在后台执行同步，不等待结果
        asyncio.create_task(sync_submission_to_admin(
            submission_id=submission.submission_id,
            teacher_id=CURRENT_TEACHER_ID,
            teacher_name=CURRENT_TEACHER_NAME,
            files=files_info,
            notes=submit_data.notes or "",
            submitted_at=submission.submitted_at.isoformat()
        ))
        
        return {
            "submission_id": submission.submission_id,
            "message": "材料提交成功",
            "submission_time": submission.submitted_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交材料失败: {str(e)}"
        )


@router.get("/submissions", response_model=dict)
async def get_submissions(
    db: Session = Depends(get_db)
):
    """
    获取当前教师的提交记录
    """
    try:
        submissions = db.query(TeacherSubmission).filter(
            TeacherSubmission.teacher_id == CURRENT_TEACHER_ID
        ).order_by(TeacherSubmission.submitted_at.desc()).all()
        
        submissions_data = []
        for submission in submissions:
            submissions_data.append({
                "submission_id": submission.submission_id,
                "files": [{"file_name": f["file_name"], "file_size": f["file_size"]} for f in submission.files],
                "submission_time": submission.submitted_at.isoformat(),
                "review_status": submission.review_status,
                "review_feedback": submission.review_feedback,
                "review_time": submission.reviewed_at.isoformat() if submission.reviewed_at else None
            })
        
        return {
            "submissions": submissions_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取提交记录失败: {str(e)}"
        )


@router.get("/submissions/{submission_id}/scoring", response_model=dict)
async def get_submission_scoring_results(
    submission_id: str,
    db: Session = Depends(get_db)
):
    """
    获取提交记录的评分结果
    
    - 查询该提交对应的所有评分记录
    - 返回评分明细（得分、等级、扣分理由）
    - Requirements: 7.6, 8.1
    """
    try:
        # 验证提交记录属于当前教师
        submission = db.query(TeacherSubmission).filter(
            TeacherSubmission.submission_id == submission_id,
            TeacherSubmission.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提交记录不存在或无权访问"
            )
        
        # 调用管理端API获取评分记录
        import httpx
        import json
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8001/api/scoring/records/{submission_id}",
                    timeout=10.0
                )
                
                if response.status_code == 404:
                    # 还没有评分记录
                    return {
                        "submission_id": submission_id,
                        "scoring_records": [],
                        "has_scoring": False,
                        "message": "暂无评分结果"
                    }
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="获取评分结果失败"
                    )
                
                data = response.json()
                records = data.get("records", [])
                
                # 格式化评分记录
                formatted_records = []
                for record in records:
                    score_details = record.get("score_details", {})
                    if isinstance(score_details, str):
                        try:
                            score_details = json.loads(score_details)
                        except:
                            score_details = {}
                    
                    formatted_records.append({
                        "id": record.get("id"),
                        "file_name": record.get("file_name"),
                        "file_type": record.get("file_type"),
                        "final_score": record.get("final_score"),
                        "grade": record.get("grade"),
                        "base_score": record.get("base_score", 0),
                        "bonus_score": record.get("bonus_score", 0),
                        "score_details": score_details,
                        "is_confirmed": record.get("is_confirmed", False),
                        "scoring_type": record.get("scoring_type", "auto"),
                        "scored_at": record.get("scored_at"),
                        "veto_triggered": record.get("veto_triggered", False),
                        "veto_reason": record.get("veto_reason")
                    })
                
                return {
                    "submission_id": submission_id,
                    "scoring_records": formatted_records,
                    "has_scoring": len(formatted_records) > 0,
                    "total_records": len(formatted_records)
                }
        
        except httpx.RequestError as e:
            # 管理端API不可用
            return {
                "submission_id": submission_id,
                "scoring_records": [],
                "has_scoring": False,
                "message": "评分服务暂不可用"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评分结果失败: {str(e)}"
        )
