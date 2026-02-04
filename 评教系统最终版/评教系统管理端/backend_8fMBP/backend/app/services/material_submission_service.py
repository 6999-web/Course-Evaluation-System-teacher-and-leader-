"""
材料提交服务

处理文件提交、文件类型校验、文件状态管理、文件重新上传等功能。
"""

import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import (
    MaterialSubmission, EvaluationAssignmentTask, ScoringRecord,
    ScoringLog, User
)
from app.utils.file_parser import FileParser


class MaterialSubmissionService:
    """材料提交服务类"""
    
    # 支持的文件类型
    SUPPORTED_FILE_TYPES = ['docx', 'pdf', 'pptx']
    
    # 文件类型映射到中文名称
    FILE_TYPE_NAMES = {
        'docx': '教案',
        'pdf': '成绩/学情分析',
        'pptx': '课件'
    }
    
    def __init__(self, db: Session):
        """
        初始化材料提交服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.file_parser = FileParser()
    
    def validate_file_type(
        self,
        file_extension: str,
        required_file_types: List[str]
    ) -> Tuple[bool, str]:
        """
        校验文件类型是否符合任务要求
        
        Args:
            file_extension: 文件扩展名（不含点）
            required_file_types: 任务要求的文件类型列表
        
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        
        **Validates: Requirements 7.1, 7.2**
        """
        # 转换为小写进行比较
        file_ext = file_extension.lower()
        
        # 检查是否支持该文件格式
        if file_ext not in self.SUPPORTED_FILE_TYPES:
            return False, f"不支持的文件格式: {file_extension}。支持的格式: {', '.join(self.SUPPORTED_FILE_TYPES)}"
        
        # 检查文件类型是否符合任务要求
        if required_file_types and file_ext not in required_file_types:
            return False, f"文件类型 {file_extension} 不符合任务要求。要求的类型: {', '.join(required_file_types)}"
        
        return True, ""
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 文件的 SHA256 哈希值
        
        **Validates: Requirements 11.2**
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            raise Exception(f"计算文件哈希失败: {str(e)}")
    
    def create_submission(
        self,
        teacher_id: str,
        teacher_name: str,
        task_id: str,
        files: List[Dict],
        notes: Optional[str] = None
    ) -> MaterialSubmission:
        """
        创建材料提交记录
        
        Args:
            teacher_id: 教师 ID
            teacher_name: 教师名称
            task_id: 任务 ID
            files: 文件列表，每个文件包含 file_id, file_name, file_size, file_url, file_type
            notes: 提交备注
        
        Returns:
            MaterialSubmission: 创建的提交记录
        
        **Validates: Requirements 7.3**
        """
        # 创建提交记录
        submission = MaterialSubmission(
            teacher_id=teacher_id,
            teacher_name=teacher_name,
            files=files,
            notes=notes,
            submitted_at=datetime.utcnow(),
            review_status="pending",
            scoring_status="pending"  # 初始状态为待评分
        )
        
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def update_submission_status(
        self,
        submission_id: str,
        scoring_status: str,
        parsed_content: Optional[str] = None,
        file_hash: Optional[str] = None,
        encrypted_path: Optional[str] = None
    ) -> MaterialSubmission:
        """
        更新提交记录的状态
        
        Args:
            submission_id: 提交记录 ID
            scoring_status: 新的评分状态
            parsed_content: 解析后的文本内容
            file_hash: 文件哈希值
            encrypted_path: 加密后的文件路径
        
        Returns:
            MaterialSubmission: 更新后的提交记录
        
        **Validates: Requirements 7.3**
        """
        submission = self.db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == submission_id
        ).first()
        
        if not submission:
            raise Exception(f"提交记录不存在: {submission_id}")
        
        submission.scoring_status = scoring_status
        
        if parsed_content is not None:
            submission.parsed_content = parsed_content
        
        if file_hash is not None:
            submission.file_hash = file_hash
        
        if encrypted_path is not None:
            submission.encrypted_path = encrypted_path
        
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def reupload_file(
        self,
        submission_id: str,
        new_files: List[Dict],
        notes: Optional[str] = None
    ) -> MaterialSubmission:
        """
        重新上传文件，覆盖之前的文件
        
        Args:
            submission_id: 提交记录 ID
            new_files: 新的文件列表
            notes: 新的提交备注
        
        Returns:
            MaterialSubmission: 更新后的提交记录
        
        **Validates: Requirements 7.5**
        """
        submission = self.db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == submission_id
        ).first()
        
        if not submission:
            raise Exception(f"提交记录不存在: {submission_id}")
        
        # 覆盖旧文件
        submission.files = new_files
        
        # 更新提交时间
        submission.submitted_at = datetime.utcnow()
        
        # 更新备注
        if notes is not None:
            submission.notes = notes
        
        # 重置评分状态以触发重新评分
        submission.scoring_status = "pending"
        submission.parsed_content = None
        submission.file_hash = None
        submission.encrypted_path = None
        
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def get_submission(self, submission_id: str) -> Optional[MaterialSubmission]:
        """
        获取提交记录
        
        Args:
            submission_id: 提交记录 ID
        
        Returns:
            Optional[MaterialSubmission]: 提交记录，如果不存在则返回 None
        """
        return self.db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == submission_id
        ).first()
    
    def get_submissions_by_teacher(
        self,
        teacher_id: str,
        status: Optional[str] = None
    ) -> List[MaterialSubmission]:
        """
        获取教师的所有提交记录
        
        Args:
            teacher_id: 教师 ID
            status: 筛选状态（可选）
        
        Returns:
            List[MaterialSubmission]: 提交记录列表
        """
        query = self.db.query(MaterialSubmission).filter(
            MaterialSubmission.teacher_id == teacher_id
        )
        
        if status:
            query = query.filter(MaterialSubmission.scoring_status == status)
        
        return query.order_by(MaterialSubmission.submitted_at.desc()).all()
    
    def get_submissions_by_task(
        self,
        task_id: str,
        status: Optional[str] = None
    ) -> List[MaterialSubmission]:
        """
        获取任务的所有提交记录
        
        Args:
            task_id: 任务 ID
            status: 筛选状态（可选）
        
        Returns:
            List[MaterialSubmission]: 提交记录列表
        """
        # 这里需要通过 EvaluationAssignmentTask 关联查询
        # 暂时返回所有提交记录
        query = self.db.query(MaterialSubmission)
        
        if status:
            query = query.filter(MaterialSubmission.scoring_status == status)
        
        return query.order_by(MaterialSubmission.submitted_at.desc()).all()
    
    def parse_and_store_content(
        self,
        submission_id: str,
        file_path: str,
        file_type: str
    ) -> Tuple[bool, str]:
        """
        解析文件内容并存储
        
        Args:
            submission_id: 提交记录 ID
            file_path: 文件路径
            file_type: 文件类型
        
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息或内容)
        
        **Validates: Requirements 4.1, 4.2, 4.3, 4.5**
        """
        try:
            # 解析文件内容
            content = self.file_parser.parse_file(file_path, file_type)
            
            # 检查内容是否为空
            if not content or content.strip() == "":
                return False, "文件内容为空"
            
            # 计算文件哈希
            file_hash = self.calculate_file_hash(file_path)
            
            # 更新提交记录
            self.update_submission_status(
                submission_id,
                scoring_status="pending",
                parsed_content=content,
                file_hash=file_hash
            )
            
            return True, content
        except Exception as e:
            return False, f"文件解析失败: {str(e)}"
    
    def get_submission_with_scoring_result(
        self,
        submission_id: str
    ) -> Dict:
        """
        获取提交记录及其评分结果
        
        Args:
            submission_id: 提交记录 ID
        
        Returns:
            Dict: 包含提交记录和评分结果的字典
        
        **Validates: Requirements 7.6, 8.1**
        """
        submission = self.get_submission(submission_id)
        
        if not submission:
            raise Exception(f"提交记录不存在: {submission_id}")
        
        # 获取评分记录
        scoring_records = self.db.query(ScoringRecord).filter(
            ScoringRecord.submission_id == submission_id
        ).all()
        
        # 构建返回数据
        result = {
            "submission_id": submission.submission_id,
            "teacher_id": submission.teacher_id,
            "teacher_name": submission.teacher_name,
            "files": submission.files,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "scoring_status": submission.scoring_status,
            "scoring_records": []
        }
        
        # 添加评分记录
        for record in scoring_records:
            result["scoring_records"].append({
                "id": record.id,
                "file_name": record.file_name,
                "file_type": record.file_type,
                "base_score": record.base_score,
                "bonus_score": record.bonus_score,
                "final_score": record.final_score,
                "grade": record.grade,
                "veto_triggered": record.veto_triggered,
                "veto_reason": record.veto_reason,
                "score_details": json.loads(record.score_details) if record.score_details else {},
                "is_confirmed": record.is_confirmed,
                "scoring_type": record.scoring_type,
                "scored_at": record.scored_at.isoformat() if record.scored_at else None
            })
        
        return result
    
    def validate_submission_deadline(
        self,
        task_id: str
    ) -> Tuple[bool, str]:
        """
        检查任务是否已超过截止时间
        
        Args:
            task_id: 任务 ID
        
        Returns:
            Tuple[bool, str]: (是否在截止时间内, 错误信息)
        
        **Validates: Requirements 6.5**
        """
        task = self.db.query(EvaluationAssignmentTask).filter(
            EvaluationAssignmentTask.task_id == task_id
        ).first()
        
        if not task:
            return False, f"任务不存在: {task_id}"
        
        if datetime.utcnow() > task.deadline:
            return False, f"已超过截止时间: {task.deadline.isoformat()}"
        
        return True, ""
    
    def get_file_type_from_filename(self, filename: str) -> str:
        """
        从文件名获取文件类型
        
        Args:
            filename: 文件名
        
        Returns:
            str: 文件类型（扩展名，不含点）
        """
        if '.' not in filename:
            return ""
        
        return filename.rsplit('.', 1)[-1].lower()
    
    def format_submission_for_display(
        self,
        submission: MaterialSubmission
    ) -> Dict:
        """
        格式化提交记录用于前端展示
        
        Args:
            submission: 提交记录
        
        Returns:
            Dict: 格式化后的提交记录
        """
        return {
            "submission_id": submission.submission_id,
            "teacher_id": submission.teacher_id,
            "teacher_name": submission.teacher_name,
            "files": submission.files,
            "notes": submission.notes,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "review_status": submission.review_status,
            "review_feedback": submission.review_feedback,
            "scoring_status": submission.scoring_status,
            "file_hash": submission.file_hash
        }
