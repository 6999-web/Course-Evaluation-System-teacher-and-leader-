"""
自动评分 API 路由
"""

import logging
import os
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import User, MaterialSubmission
from ..auth import get_current_active_user
from ..scoring_engine import ScoringEngine
from ..file_parser import FileParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

# 从环境变量读取 API 密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-b6ca926900534f1fa31067d49980ec56")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

# 初始化评分引擎
scoring_engine = ScoringEngine(DEEPSEEK_API_KEY, DEEPSEEK_API_URL)


@router.post("/score/{submission_id}")
async def score_submission(
    submission_id: str,
    bonus_items: Optional[List[dict]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    对单个提交的文件进行评分
    
    支持两种ID类型:
    1. submission_id - MaterialSubmission的ID (材料提交)
    2. task_id - EvaluationAssignmentTask的ID (考评任务)
    
    Args:
        submission_id: 提交记录 ID 或任务 ID
        bonus_items: 加分项列表
        
    Returns:
        评分结果
    """
    try:
        from ..models import EvaluationAssignmentTask
        
        # 先尝试作为MaterialSubmission查找
        submission = db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == submission_id
        ).first()
        
        # 如果不是MaterialSubmission，尝试作为EvaluationAssignmentTask查找
        if not submission:
            task = db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.task_id == submission_id
            ).first()
            
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"提交记录或任务不存在: {submission_id}"
                )
            
            # 使用EvaluationAssignmentTask的数据
            files = task.submitted_files or []
            if not files:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="任务中没有提交文件"
                )
            
            # 获取第一个文件
            file_info = files[0]
            file_path = file_info.get("file_url") or file_info.get("path")
            file_name = file_info.get("file_name")
            
            # 从文件名推断文件类型
            file_type_mapping = {
                'pdf': '教案',
                'docx': '教学反思',
                'doc': '教学反思',
                'pptx': '课件',
                'ppt': '课件',
                'txt': '教学反思'
            }
            
            if file_name:
                file_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
                file_type = file_type_mapping.get(file_ext, '教案')
            else:
                file_type = file_info.get("type", '教案')
            
            if not file_path or not file_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件信息不完整: path={file_path}, type={file_type}"
                )
            
            # 规范化文件路径（处理Windows反斜杠和混合分隔符）
            logger.info(f"原始文件路径: {file_path}")
            file_path = file_path.replace('\\', '/')  # 先统一为正斜杠
            file_path = os.path.normpath(file_path)  # 再规范化为系统路径
            logger.info(f"规范化后路径: {file_path}")
            
            # 尝试多个可能的文件路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            logger.info(f"基础目录: {base_dir}")
            
            # 从backend_8fMBP向上两级到评教系统最终版目录
            parent_dir = os.path.dirname(os.path.dirname(base_dir))
            
            possible_paths = [
                file_path,
                os.path.join(parent_dir, "评教系统教师端", "backend", file_path),
                os.path.join(base_dir, "..", "..", "评教系统教师端", "backend", file_path),
                os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../评教系统教师端/backend", file_path))
            ]
            
            actual_file_path = None
            for i, path in enumerate(possible_paths, 1):
                normalized_path = os.path.normpath(path)
                logger.info(f"尝试路径 {i}: {normalized_path}")
                logger.info(f"  文件存在: {os.path.exists(normalized_path)}")
                if os.path.exists(normalized_path):
                    actual_file_path = normalized_path
                    logger.info(f"✅ 找到文件: {actual_file_path}")
                    break
            
            if not actual_file_path:
                error_msg = f"文件不存在。原始路径: {file_info.get('file_url') or file_info.get('path')}, 规范化路径: {file_path}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            # 解析文件内容
            logger.info(f"开始解析文件: {actual_file_path}")
            try:
                file_ext = os.path.splitext(actual_file_path)[1].lower().lstrip('.')
                content = FileParser.parse_file(actual_file_path, file_ext)
            except Exception as e:
                logger.error(f"文件解析失败: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"文件解析失败: {str(e)}"
                )
            
            # 获取考评表信息（总分和评分标准）
            from ..models import EvaluationTemplate
            template = db.query(EvaluationTemplate).filter(
                EvaluationTemplate.template_id == task.template_id
            ).first()
            
            total_score = 100  # 默认100分
            scoring_criteria = None
            
            if template:
                total_score = template.total_score or 100
                scoring_criteria = template.scoring_criteria
                logger.info(f"使用考评表总分: {total_score}分")
                if scoring_criteria:
                    logger.info(f"使用考评表评分标准: {len(scoring_criteria)}个指标")
            
            # 进行评分
            logger.info(f"开始评分: {submission_id}")
            scoring_result = scoring_engine.score_file(
                file_type, 
                content, 
                total_score=total_score,
                scoring_criteria=scoring_criteria,
                bonus_items=bonus_items
            )
            
            if not scoring_result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"评分失败: {scoring_result.get('error', '未知错误')}"
                )
            
            # 更新任务状态
            task.status = "scored"
            task.scored_at = datetime.utcnow()
            task.total_score = scoring_result.get("final_score", 0)
            task.scoring_feedback = scoring_result.get("summary", "")
            
            # 保存详细评分结果到scores字段
            task.scores = {
                "base_score": scoring_result.get("base_score", 0),
                "bonus_score": scoring_result.get("bonus_score", 0),
                "final_score": scoring_result.get("final_score", 0),
                "grade": scoring_result.get("grade", ""),
                "veto_triggered": scoring_result.get("veto_triggered", False),
                "veto_reason": scoring_result.get("veto_reason", ""),
                "score_details": scoring_result.get("score_details", []),
                "summary": scoring_result.get("summary", ""),
                "scored_at": datetime.utcnow().isoformat()
            }
            
            db.commit()
            
            return {
                "success": True,
                "submission_id": submission_id,
                "scoring_result": task.scores
            }
        
        # 原有的MaterialSubmission处理逻辑
        # 获取文件信息
        files = submission.files or []
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提交记录中没有文件"
            )
        
        # 获取第一个文件
        file_info = files[0]
        file_path = file_info.get("file_url") or file_info.get("path")
        file_name = file_info.get("file_name")
        
        # 从文件名推断文件类型
        file_type_mapping = {
            'pdf': '教案',  # 默认将PDF视为教案
            'docx': '教学反思',  # 默认将DOCX视为教学反思
            'doc': '教学反思',
            'pptx': '课件',
            'ppt': '课件',
            'txt': '教学反思'
        }
        
        if file_name:
            file_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            file_type = file_type_mapping.get(file_ext, '教案')  # 默认为教案
        else:
            file_type = file_info.get("type", '教案')
        
        if not file_path or not file_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件信息不完整: path={file_path}, type={file_type}"
            )
        
        # 规范化文件路径（处理Windows反斜杠和混合分隔符）
        logger.info(f"原始文件路径: {file_path}")
        file_path = file_path.replace('\\', '/')  # 先统一为正斜杠
        file_path = os.path.normpath(file_path)  # 再规范化为系统路径
        logger.info(f"规范化后路径: {file_path}")
        
        # 尝试多个可能的文件路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        logger.info(f"基础目录: {base_dir}")
        
        # 从backend_8fMBP向上两级到评教系统最终版目录
        parent_dir = os.path.dirname(os.path.dirname(base_dir))
        
        possible_paths = [
            file_path,
            os.path.join(parent_dir, "评教系统教师端", "backend", file_path),
            os.path.join(base_dir, "..", "..", "评教系统教师端", "backend", file_path),
            os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../评教系统教师端/backend", file_path))
        ]
        
        actual_file_path = None
        for i, path in enumerate(possible_paths, 1):
            normalized_path = os.path.normpath(path)
            logger.info(f"尝试路径 {i}: {normalized_path}")
            logger.info(f"  文件存在: {os.path.exists(normalized_path)}")
            if os.path.exists(normalized_path):
                actual_file_path = normalized_path
                logger.info(f"找到文件: {actual_file_path}")
                break
        
        # 检查文件是否存在
        if not actual_file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件不存在: {file_path}。尝试的路径: {possible_paths}"
            )
        
        # 解析文件内容
        logger.info(f"开始解析文件: {actual_file_path}")
        try:
            # 从文件路径获取扩展名用于解析
            file_ext = os.path.splitext(actual_file_path)[1].lower().lstrip('.')
            content = FileParser.parse_file(actual_file_path, file_ext)
        except Exception as e:
            logger.error(f"文件解析失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件解析失败: {str(e)}"
            )
        
        # 进行评分
        logger.info(f"开始评分: {submission_id}")
        scoring_result = scoring_engine.score_file(file_type, content, bonus_items)
        
        if not scoring_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"评分失败: {scoring_result.get('error', '未知错误')}"
            )
        
        # 更新提交记录
        submission.review_status = "scored"
        submission.reviewed_at = datetime.utcnow()
        
        # 保存评分结果
        submission.scoring_result = {
            "base_score": scoring_result.get("base_score", 0),
            "bonus_score": scoring_result.get("bonus_score", 0),
            "final_score": scoring_result.get("final_score", 0),
            "grade": scoring_result.get("grade", ""),
            "veto_triggered": scoring_result.get("veto_triggered", False),
            "veto_reason": scoring_result.get("veto_reason", ""),
            "score_details": scoring_result.get("score_details", []),
            "summary": scoring_result.get("summary", ""),
            "scored_at": datetime.utcnow().isoformat()
        }
        
        db.commit()
        
        return {
            "success": True,
            "submission_id": submission_id,
            "scoring_result": submission.scoring_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"评分异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评分异常: {str(e)}"
        )


@router.post("/batch-score")
async def batch_score(
    submission_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量评分
    
    Args:
        submission_ids: 提交记录 ID 列表
        
    Returns:
        批量评分结果
    """
    try:
        results = []
        success_count = 0
        failed_count = 0
        
        for submission_id in submission_ids:
            try:
                # 查找提交记录
                submission = db.query(MaterialSubmission).filter(
                    MaterialSubmission.submission_id == submission_id
                ).first()
                
                if not submission:
                    results.append({
                        "submission_id": submission_id,
                        "success": False,
                        "error": "提交记录不存在"
                    })
                    failed_count += 1
                    continue
                
                # 获取文件信息
                files = submission.files or []
                if not files:
                    results.append({
                        "submission_id": submission_id,
                        "success": False,
                        "error": "提交记录中没有文件"
                    })
                    failed_count += 1
                    continue
                
                # 获取第一个文件
                file_info = files[0]
                file_path = file_info.get("file_url") or file_info.get("path")
                file_name = file_info.get("file_name")
                
                # 从文件名推断文件类型
                file_type_mapping = {
                    'pdf': '教案',  # 默认将PDF视为教案
                    'docx': '教学反思',  # 默认将DOCX视为教学反思
                    'doc': '教学反思',
                    'pptx': '课件',
                    'ppt': '课件',
                    'txt': '教学反思'
                }
                
                if file_name:
                    file_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
                    file_type = file_type_mapping.get(file_ext, '教案')  # 默认为教案
                else:
                    file_type = file_info.get("type", '教案')
                
                if not file_path or not file_type:
                    results.append({
                        "submission_id": submission_id,
                        "success": False,
                        "error": f"文件信息不完整: path={file_path}, type={file_type}"
                    })
                    failed_count += 1
                    continue
                
                # 规范化文件路径（处理Windows反斜杠和混合分隔符）
                logger.info(f"[批量评分] 原始文件路径: {file_path}")
                file_path = file_path.replace('\\', '/')  # 先统一为正斜杠
                file_path = os.path.normpath(file_path)  # 再规范化为系统路径
                logger.info(f"[批量评分] 规范化后路径: {file_path}")
                
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                logger.info(f"[批量评分] 基础目录: {base_dir}")
                
                # 从backend_8fMBP向上两级到评教系统最终版目录
                parent_dir = os.path.dirname(os.path.dirname(base_dir))
                
                # 尝试多个可能的文件路径
                possible_paths = [
                    file_path,
                    os.path.join(parent_dir, "评教系统教师端", "backend", file_path),
                    os.path.join(base_dir, "..", "..", "评教系统教师端", "backend", file_path),
                    os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../评教系统教师端/backend", file_path))
                ]
                
                actual_file_path = None
                for i, path in enumerate(possible_paths, 1):
                    normalized_path = os.path.normpath(path)
                    logger.info(f"[批量评分] 尝试路径 {i}: {normalized_path}")
                    logger.info(f"[批量评分]   文件存在: {os.path.exists(normalized_path)}")
                    if os.path.exists(normalized_path):
                        actual_file_path = normalized_path
                        logger.info(f"[批量评分] ✅ 找到文件: {actual_file_path}")
                        break
                
                # 检查文件是否存在
                if not actual_file_path:
                    error_msg = f"文件不存在。原始路径: {file_info.get('file_url') or file_info.get('path')}, 规范化路径: {file_path}"
                    logger.error(f"[批量评分] {error_msg}")
                    results.append({
                        "submission_id": submission_id,
                        "success": False,
                        "error": error_msg
                    })
                    failed_count += 1
                    continue
                
                # 解析文件内容
                try:
                    # 从文件路径获取扩展名用于解析
                    file_ext = os.path.splitext(actual_file_path)[1].lower().lstrip('.')
                    content = FileParser.parse_file(actual_file_path, file_ext)
                except Exception as e:
                    results.append({
                        "submission_id": submission_id,
                        "success": False,
                        "error": f"文件解析失败: {str(e)}"
                    })
                    failed_count += 1
                    continue
                
                # 进行评分
                scoring_result = scoring_engine.score_file(file_type, content)
                
                if not scoring_result.get("success"):
                    results.append({
                        "submission_id": submission_id,
                        "success": False,
                        "error": f"评分失败: {scoring_result.get('error', '未知错误')}"
                    })
                    failed_count += 1
                    continue
                
                # 更新提交记录
                submission.review_status = "scored"
                submission.reviewed_at = datetime.utcnow()
                submission.scoring_result = {
                    "base_score": scoring_result.get("base_score", 0),
                    "bonus_score": scoring_result.get("bonus_score", 0),
                    "final_score": scoring_result.get("final_score", 0),
                    "grade": scoring_result.get("grade", ""),
                    "veto_triggered": scoring_result.get("veto_triggered", False),
                    "veto_reason": scoring_result.get("veto_reason", ""),
                    "score_details": scoring_result.get("score_details", []),
                    "summary": scoring_result.get("summary", ""),
                    "scored_at": datetime.utcnow().isoformat()
                }
                
                results.append({
                    "submission_id": submission_id,
                    "success": True,
                    "scoring_result": submission.scoring_result
                })
                success_count += 1
                
            except Exception as e:
                logger.error(f"批量评分异常: {str(e)}")
                results.append({
                    "submission_id": submission_id,
                    "success": False,
                    "error": f"异常: {str(e)}"
                })
                failed_count += 1
        
        # 提交所有更改
        db.commit()
        
        return {
            "total": len(submission_ids),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"批量评分异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量评分异常: {str(e)}"
        )


@router.get("/records/{submission_id}")
async def get_scoring_record(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取评分记录
    
    Args:
        submission_id: 提交记录 ID
        
    Returns:
        评分记录
    """
    try:
        submission = db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提交记录不存在"
            )
        
        return {
            "submission_id": submission.submission_id,
            "teacher_id": submission.teacher_id,
            "teacher_name": submission.teacher_name,
            "review_status": submission.review_status,
            "scoring_result": submission.scoring_result or {},
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评分记录异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评分记录异常: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {
        "status": "ok",
        "message": "评分系统正常运行"
    }
