"""
任务管理器 (Task Manager)

职责: 管理考评任务的创建、配置和分发
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import (
    EvaluationAssignmentTask,
    ScoringRecord,
    MaterialSubmission,
    BonusItem,
    ScoringLog,
    User
)

logger = logging.getLogger(__name__)


class TaskManager:
    """
    任务管理器
    
    职责:
    - 创建和配置考评任务
    - 管理文件类型配置
    - 管理加分项配置
    - 检查截止时间并自动否决
    - 自动分发任务给教师
    """
    
    def __init__(self, db: Session):
        """
        初始化任务管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        创建考评任务
        
        Args:
            task_data: 任务数据，包含:
                - template_id: 模板ID
                - teacher_id: 教师ID
                - teacher_name: 教师姓名
                - required_file_types: 必需文件类型列表 ["教案", "教学反思", ...]
                - bonus_enabled: 是否启用加分项
                - max_bonus_score: 最大加分值
                - auto_scoring_enabled: 是否启用自动评分
                - deadline: 截止时间
        
        Returns:
            任务ID
            
        Raises:
            ValueError: 如果任务数据不完整
        """
        try:
            # 验证必需字段
            required_fields = ['template_id', 'teacher_id', 'teacher_name', 'deadline']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"缺少必需字段: {field}")
            
            # 创建任务
            task = EvaluationAssignmentTask(
                template_id=task_data['template_id'],
                teacher_id=task_data['teacher_id'],
                teacher_name=task_data['teacher_name'],
                required_file_types=task_data.get('required_file_types', []),
                bonus_enabled=task_data.get('bonus_enabled', True),
                max_bonus_score=task_data.get('max_bonus_score', 10),
                auto_scoring_enabled=task_data.get('auto_scoring_enabled', True),
                deadline=task_data['deadline'],
                status='pending'
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"任务创建成功: {task.task_id}")
            
            # 记录日志
            self._log_action(
                action='create',
                related_id=task.task_id,
                related_type='task',
                action_details={
                    'task_id': task.task_id,
                    'teacher_id': task.teacher_id,
                    'required_file_types': task.required_file_types,
                    'deadline': task.deadline.isoformat() if task.deadline else None
                }
            )
            
            return task.task_id
            
        except Exception as e:
            logger.error(f"任务创建失败: {str(e)}")
            self.db.rollback()
            raise
    
    def update_task_config(self, task_id: str, config_data: Dict[str, Any]) -> bool:
        """
        更新任务配置
        
        Args:
            task_id: 任务ID
            config_data: 配置数据，可包含:
                - required_file_types: 必需文件类型列表
                - bonus_enabled: 是否启用加分项
                - max_bonus_score: 最大加分值
                - auto_scoring_enabled: 是否启用自动评分
                - deadline: 截止时间
        
        Returns:
            是否更新成功
        """
        try:
            task = self.db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.task_id == task_id
            ).first()
            
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            # 更新配置
            if 'required_file_types' in config_data:
                task.required_file_types = config_data['required_file_types']
            
            if 'bonus_enabled' in config_data:
                task.bonus_enabled = config_data['bonus_enabled']
            
            if 'max_bonus_score' in config_data:
                task.max_bonus_score = config_data['max_bonus_score']
            
            if 'auto_scoring_enabled' in config_data:
                task.auto_scoring_enabled = config_data['auto_scoring_enabled']
            
            if 'deadline' in config_data:
                task.deadline = config_data['deadline']
            
            task.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"任务配置更新成功: {task_id}")
            
            # 记录日志
            self._log_action(
                action='update',
                related_id=task_id,
                related_type='task',
                action_details=config_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"任务配置更新失败: {str(e)}")
            self.db.rollback()
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务详情字典，如果任务不存在则返回None
        """
        try:
            task = self.db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.task_id == task_id
            ).first()
            
            if not task:
                return None
            
            return {
                'task_id': task.task_id,
                'template_id': task.template_id,
                'teacher_id': task.teacher_id,
                'teacher_name': task.teacher_name,
                'status': task.status,
                'required_file_types': task.required_file_types or [],
                'bonus_enabled': task.bonus_enabled,
                'max_bonus_score': task.max_bonus_score,
                'auto_scoring_enabled': task.auto_scoring_enabled,
                'deadline': task.deadline.isoformat() if task.deadline else None,
                'submitted_at': task.submitted_at.isoformat() if task.submitted_at else None,
                'scored_at': task.scored_at.isoformat() if task.scored_at else None,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"获取任务详情失败: {str(e)}")
            return None
    
    def assign_task(self, task_id: str, teacher_ids: List[str]) -> bool:
        """
        分配任务给教师
        
        Args:
            task_id: 任务ID
            teacher_ids: 教师ID列表
        
        Returns:
            是否分配成功
        """
        try:
            # 获取原始任务
            original_task = self.db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.task_id == task_id
            ).first()
            
            if not original_task:
                logger.warning(f"任务不存在: {task_id}")
                return False
            
            # 为每个教师创建任务副本
            for teacher_id in teacher_ids:
                # 检查是否已存在
                existing_task = self.db.query(EvaluationAssignmentTask).filter(
                    and_(
                        EvaluationAssignmentTask.template_id == original_task.template_id,
                        EvaluationAssignmentTask.teacher_id == teacher_id
                    )
                ).first()
                
                if existing_task:
                    logger.info(f"任务已存在: {existing_task.task_id}")
                    continue
                
                # 创建新任务
                new_task = EvaluationAssignmentTask(
                    template_id=original_task.template_id,
                    teacher_id=teacher_id,
                    teacher_name=teacher_id,  # 这里应该从用户表获取真实名称
                    required_file_types=original_task.required_file_types,
                    bonus_enabled=original_task.bonus_enabled,
                    max_bonus_score=original_task.max_bonus_score,
                    auto_scoring_enabled=original_task.auto_scoring_enabled,
                    deadline=original_task.deadline,
                    status='pending'
                )
                
                self.db.add(new_task)
            
            self.db.commit()
            
            logger.info(f"任务分配成功: {task_id} -> {len(teacher_ids)} 位教师")
            
            # 记录日志
            self._log_action(
                action='assign',
                related_id=task_id,
                related_type='task',
                action_details={'teacher_ids': teacher_ids}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"任务分配失败: {str(e)}")
            self.db.rollback()
            return False
    
    def check_deadline(self) -> List[Dict[str, Any]]:
        """
        检查截止时间，返回超时未提交的记录
        
        Returns:
            超时未提交的任务列表
        """
        try:
            now = datetime.utcnow()
            
            # 查询所有超时未提交的任务
            overdue_tasks = self.db.query(EvaluationAssignmentTask).filter(
                and_(
                    EvaluationAssignmentTask.deadline < now,
                    EvaluationAssignmentTask.status == 'pending'
                )
            ).all()
            
            result = []
            for task in overdue_tasks:
                result.append({
                    'task_id': task.task_id,
                    'teacher_id': task.teacher_id,
                    'teacher_name': task.teacher_name,
                    'deadline': task.deadline.isoformat() if task.deadline else None,
                    'status': task.status
                })
            
            logger.info(f"检查截止时间: 发现 {len(result)} 个超时未提交的任务")
            
            return result
            
        except Exception as e:
            logger.error(f"检查截止时间失败: {str(e)}")
            return []
    
    def trigger_veto_for_overdue(self, task_ids: List[str]) -> bool:
        """
        对超时未提交的任务触发一票否决
        
        Args:
            task_ids: 任务ID列表
        
        Returns:
            是否触发成功
        """
        try:
            for task_id in task_ids:
                task = self.db.query(EvaluationAssignmentTask).filter(
                    EvaluationAssignmentTask.task_id == task_id
                ).first()
                
                if not task:
                    logger.warning(f"任务不存在: {task_id}")
                    continue
                
                # 创建否决评分记录
                # 首先需要找到或创建对应的提交记录
                submission = self.db.query(MaterialSubmission).filter(
                    and_(
                        MaterialSubmission.teacher_id == task.teacher_id,
                        MaterialSubmission.submitted_at.is_(None)  # 未提交
                    )
                ).first()
                
                if not submission:
                    # 创建一个虚拟的提交记录用于记录否决
                    submission = MaterialSubmission(
                        teacher_id=task.teacher_id,
                        teacher_name=task.teacher_name,
                        files=[],
                        review_status='pending',
                        scoring_status='scored'
                    )
                    self.db.add(submission)
                    self.db.flush()
                
                # 创建否决评分记录
                veto_record = ScoringRecord(
                    submission_id=submission.submission_id,
                    file_id=task.task_id,
                    file_type='task_submission',
                    file_name=f"Task_{task.task_id}",
                    base_score=0,
                    bonus_score=0,
                    final_score=0,
                    grade='不合格',
                    veto_triggered=True,
                    veto_reason='超时未提交，触发一票否决',
                    scoring_type='auto',
                    scored_at=datetime.utcnow()
                )
                
                self.db.add(veto_record)
                
                # 更新任务状态
                task.status = 'scored'
                task.total_score = 0
                task.scored_at = datetime.utcnow()
                
                logger.info(f"为超时任务触发否决: {task_id}")
                
                # 记录日志
                self._log_action(
                    action='veto',
                    related_id=task_id,
                    related_type='task',
                    action_details={'reason': '超时未提交'}
                )
            
            self.db.commit()
            
            logger.info(f"为 {len(task_ids)} 个超时任务触发否决成功")
            
            return True
            
        except Exception as e:
            logger.error(f"触发否决失败: {str(e)}")
            self.db.rollback()
            return False
    
    def get_tasks_by_teacher(self, teacher_id: str) -> List[Dict[str, Any]]:
        """
        获取教师的所有任务
        
        Args:
            teacher_id: 教师ID
        
        Returns:
            任务列表
        """
        try:
            tasks = self.db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.teacher_id == teacher_id
            ).all()
            
            result = []
            for task in tasks:
                result.append({
                    'task_id': task.task_id,
                    'template_id': task.template_id,
                    'status': task.status,
                    'required_file_types': task.required_file_types or [],
                    'deadline': task.deadline.isoformat() if task.deadline else None,
                    'submitted_at': task.submitted_at.isoformat() if task.submitted_at else None,
                    'scored_at': task.scored_at.isoformat() if task.scored_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取教师任务列表失败: {str(e)}")
            return []
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有待处理的任务
        
        Returns:
            待处理任务列表
        """
        try:
            tasks = self.db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.status == 'pending'
            ).all()
            
            result = []
            for task in tasks:
                result.append({
                    'task_id': task.task_id,
                    'teacher_id': task.teacher_id,
                    'teacher_name': task.teacher_name,
                    'deadline': task.deadline.isoformat() if task.deadline else None,
                    'required_file_types': task.required_file_types or []
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取待处理任务列表失败: {str(e)}")
            return []
    
    def _log_action(self, action: str, related_id: str, related_type: str, 
                   action_details: Dict[str, Any], action_by: Optional[int] = None) -> None:
        """
        记录操作日志
        
        Args:
            action: 操作类型
            related_id: 关联ID
            related_type: 关联类型
            action_details: 操作详情
            action_by: 操作人ID
        """
        try:
            log = ScoringLog(
                action=action,
                action_by=action_by,
                action_details=str(action_details),
                related_id=related_id,
                related_type=related_type
            )
            
            self.db.add(log)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"记录操作日志失败: {str(e)}")
