"""
考评任务相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models.material import EvaluationTaskModel
from app.schemas.material import MaterialSubmitRequest

router = APIRouter(prefix="/teacher/evaluation-tasks", tags=["考评任务"])

# 临时：模拟当前登录教师ID（实际应从JWT token获取）
CURRENT_TEACHER_ID = "teacher_001"
CURRENT_TEACHER_NAME = "张三"


@router.get("", response_model=dict)
async def get_evaluation_tasks(
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db)
):
    """
    获取当前教师的考评任务列表
    
    - 支持按状态筛选
    - 返回待办考评和已提交考评
    """
    try:
        # 使用原始SQL查询来避免字段不存在的问题
        from sqlalchemy import text
        
        sql = """
        SELECT task_id, template_id, teacher_id, template_name, template_file_url, 
               template_file_type, status, deadline, submitted_files, submitted_at, 
               submission_notes, scores, final_score, scoring_feedback, scored_at, 
               score_history, total_score, scoring_criteria, submission_requirements, created_at, updated_at
        FROM evaluation_form_tasks
        WHERE teacher_id = :teacher_id
        """
        
        if status_filter:
            sql += " AND status = :status"
        
        sql += " ORDER BY deadline"
        
        params = {"teacher_id": CURRENT_TEACHER_ID}
        if status_filter:
            params["status"] = status_filter
        
        result = db.execute(text(sql), params)
        rows = result.fetchall()
        
        tasks_data = []
        for row in rows:
            # 解析JSON字段
            import json
            submission_requirements = {}
            scoring_criteria = []
            submitted_files = []
            scores = {}
            score_history = []
            
            try:
                if row[8]:  # submitted_files
                    submitted_files = json.loads(row[8]) if isinstance(row[8], str) else row[8]
            except:
                pass
            
            try:
                if row[11]:  # scores
                    scores = json.loads(row[11]) if isinstance(row[11], str) else row[11]
            except:
                pass
            
            try:
                if row[15]:  # score_history
                    score_history = json.loads(row[15]) if isinstance(row[15], str) else row[15]
            except:
                pass
            
            try:
                if row[17]:  # scoring_criteria
                    scoring_criteria = json.loads(row[17]) if isinstance(row[17], str) else row[17]
            except:
                pass
            
            try:
                if row[18]:  # submission_requirements
                    submission_requirements = json.loads(row[18]) if isinstance(row[18], str) else row[18]
            except:
                pass
            
            # 判断是否已过期
            from datetime import datetime
            deadline = row[7]
            if isinstance(deadline, str):
                from dateutil import parser
                deadline = parser.parse(deadline)
            is_overdue = datetime.now() > deadline
            
            task_data = {
                "task_id": row[0],
                "template_id": row[1],
                "template_name": row[3],
                "template_file_url": row[4],
                "template_file_type": row[5],
                "status": row[6],
                "deadline": deadline.isoformat() if hasattr(deadline, 'isoformat') else str(deadline),
                "is_overdue": is_overdue,
                "submission_requirements": submission_requirements,
                "scoring_criteria": scoring_criteria,
                "total_score": row[16] or 100,  # 使用数据库中的实际总分，默认100
                "submitted_at": row[9].isoformat() if row[9] and hasattr(row[9], 'isoformat') else row[9],
                "score": row[12],  # final_score
                "scores": scores,
                "scoring_feedback": row[13],
                "scored_at": row[14].isoformat() if row[14] and hasattr(row[14], 'isoformat') else row[14],
                "score_history": score_history,
                "is_viewed": False,
                "viewed_at": None
            }
            tasks_data.append(task_data)
        
        # 分类返回
        pending_tasks = [t for t in tasks_data if t["status"] == "pending"]
        submitted_tasks = [t for t in tasks_data if t["status"] in ["submitted", "scored", "completed"]]
        
        return {
            "pending_tasks": pending_tasks,
            "submitted_tasks": submitted_tasks,
            "total": len(tasks_data)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取考评任务失败: {str(e)}"
        )


@router.get("/{task_id}", response_model=dict)
async def get_evaluation_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    获取单个考评任务详情
    """
    try:
        task = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == task_id,
            EvaluationTaskModel.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 判断是否已过期
        is_overdue = datetime.now() > task.deadline
        
        # 标记为已查收（如果字段存在）
        try:
            if hasattr(task, 'is_viewed') and not task.is_viewed:
                task.is_viewed = True
                task.viewed_at = datetime.now()
                db.commit()
        except Exception:
            # 如果字段不存在，忽略错误
            pass
        
        # 安全地获取is_viewed字段
        is_viewed = False
        viewed_at = None
        try:
            is_viewed = task.is_viewed if hasattr(task, 'is_viewed') else False
            viewed_at = task.viewed_at if hasattr(task, 'viewed_at') else None
        except Exception:
            pass
        
        return {
            "task_id": task.task_id,
            "template_id": task.template_id,
            "template_name": task.template_name,
            "template_file_url": task.template_file_url,
            "template_file_type": task.template_file_type,
            "status": task.status,
            "deadline": task.deadline.isoformat(),
            "is_overdue": is_overdue,
            "submission_requirements": task.submission_requirements,
            "scoring_criteria": task.scoring_criteria,
            "total_score": task.total_score or 100,  # 使用数据库中的实际总分
            "submitted_files": task.submitted_files,
            "submitted_at": task.submitted_at.isoformat() if task.submitted_at else None,
            "submission_notes": task.submission_notes,
            "score": task.final_score,
            "scores": task.scores,
            "scoring_feedback": task.scoring_feedback,
            "scored_at": task.scored_at.isoformat() if task.scored_at else None,
            "score_history": task.score_history,
            "is_viewed": is_viewed,
            "viewed_at": viewed_at.isoformat() if viewed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取考评任务失败: {str(e)}"
        )


@router.post("/{task_id}/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_evaluation_file(
    task_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传考评文件
    
    - 验证文件类型和大小
    - 保存文件到服务器
    - 返回文件ID和元信息
    """
    try:
        # 查找考评任务
        task = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == task_id,
            EvaluationTaskModel.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 检查是否已过期
        if datetime.now() > task.deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="考评已过期，无法上传文件"
            )
        
        # 验证文件类型
        allowed_types = task.submission_requirements.get("file_types", ["pdf", "excel", "word"])
        file_ext = file.filename.split('.')[-1].lower()
        
        # 映射文件扩展名到类型
        ext_to_type = {
            "pdf": "pdf",
            "xlsx": "excel", "xls": "excel",
            "docx": "word", "doc": "word"
        }
        
        file_type = ext_to_type.get(file_ext)
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型。允许的类型: {', '.join(allowed_types)}"
            )
        
        # 验证文件大小（50MB限制）
        max_size = 50 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过限制（最大50MB）"
            )
        
        # 检查文件数量限制
        max_files = task.submission_requirements.get("max_files", 3)
        current_files = len(task.submitted_files) if task.submitted_files else 0
        if current_files >= max_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件数量超过限制（最多{max_files}个）"
            )
        
        # 生成唯一文件ID
        file_id = f"{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}_{file.filename}"
        
        # 创建上传目录
        upload_dir = f"uploads/evaluation_submissions/{CURRENT_TEACHER_ID}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, file_id)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "file_id": file_id,
            "file_name": file.filename,
            "file_size": file_size,
            "file_type": file_type,
            "upload_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )


@router.post("/{task_id}/submit", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_evaluation_files(
    task_id: str,
    file_ids: List[str] = Query(..., description="文件ID列表"),
    notes: str = Query("", description="提交备注"),
    db: Session = Depends(get_db)
):
    """
    提交考评文件
    
    - 验证文件列表非空
    - 创建提交记录
    - 同步到管理端
    """
    try:
        # 查找考评任务
        task = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == task_id,
            EvaluationTaskModel.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 检查是否已过期
        if datetime.now() > task.deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="考评已过期，无法提交文件"
            )
        
        # 验证文件是否存在
        files_info = []
        upload_dir = f"uploads/evaluation_submissions/{CURRENT_TEACHER_ID}"
        
        for file_id in file_ids:
            file_path = os.path.join(upload_dir, file_id)
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"文件 {file_id} 不存在"
                )
            
            file_size = os.path.getsize(file_path)
            files_info.append({
                "file_id": file_id,
                "file_name": file_id.split('_')[-1],
                "file_size": file_size,
                "file_url": file_path
            })
        
        # 更新任务
        task.submitted_files = files_info
        task.submitted_at = datetime.now()
        task.submission_notes = notes
        task.status = "submitted"
        task.updated_at = datetime.now()
        
        db.commit()
        
        # 同步到管理端
        import asyncio
        from app.services.evaluation_sync_service import sync_evaluation_submission_to_admin
        
        asyncio.create_task(sync_evaluation_submission_to_admin(
            task_id=task.task_id,
            template_id=task.template_id,
            teacher_id=CURRENT_TEACHER_ID,
            teacher_name=CURRENT_TEACHER_NAME,
            files=files_info,
            notes=notes,
            submitted_at=task.submitted_at.isoformat()
        ))
        
        return {
            "task_id": task.task_id,
            "message": "文件提交成功",
            "submitted_at": task.submitted_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交文件失败: {str(e)}"
        )


@router.delete("/{task_id}/files/{file_id}", response_model=dict)
async def delete_evaluation_file(
    task_id: str,
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    删除已上传的考评文件
    
    - 只能删除未提交的文件
    """
    try:
        # 查找考评任务
        task = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == task_id,
            EvaluationTaskModel.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 检查是否已提交
        if task.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已提交的文件无法删除"
            )
        
        # 删除文件
        upload_dir = f"uploads/evaluation_submissions/{CURRENT_TEACHER_ID}"
        file_path = os.path.join(upload_dir, file_id)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            "message": "文件删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )


@router.get("/{task_id}/download/{file_id}")
async def download_evaluation_file(
    task_id: str,
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    下载考评文件
    """
    try:
        # 查找考评任务
        task = db.query(EvaluationTaskModel).filter(
            EvaluationTaskModel.task_id == task_id,
            EvaluationTaskModel.teacher_id == CURRENT_TEACHER_ID
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 构建文件路径
        upload_dir = f"uploads/evaluation_submissions/{CURRENT_TEACHER_ID}"
        file_path = os.path.join(upload_dir, file_id)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return FileResponse(
            path=file_path,
            filename=file_id.split('_')[-1],
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )
