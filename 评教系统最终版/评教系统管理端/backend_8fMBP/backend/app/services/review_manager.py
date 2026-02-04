"""
复核管理器

负责处理评分结果的复核流程，包括：
- 异议提交和处理
- 人工复核
- 随机抽查
- 一致性统计
- 评分确认和公示
"""

import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models import (
    ScoringRecord, ScoringAppeal, ReviewRecord, BonusItem,
    ScoringLog, MaterialSubmission, EvaluationAssignmentTask,
    User
)

logger = logging.getLogger(__name__)


class ReviewManagerError(Exception):
    """复核管理器异常基类"""
    pass


class AppealNotFoundError(ReviewManagerError):
    """异议未找到异常"""
    pass


class ScoringRecordNotFoundError(ReviewManagerError):
    """评分记录未找到异常"""
    pass


class InvalidAppealError(ReviewManagerError):
    """无效异议异常"""
    pass


class ReviewManager:
    """
    复核管理器
    
    负责评分结果的复核流程管理
    """
    
    def __init__(self, db: Session):
        """
        初始化复核管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        logger.info("复核管理器初始化完成")
    
    def submit_appeal(self, scoring_record_id: int, teacher_id: str, 
                     teacher_name: str, reason: str) -> int:
        """
        提交异议申请
        
        Args:
            scoring_record_id: 评分记录ID
            teacher_id: 教师ID
            teacher_name: 教师姓名
            reason: 异议理由
        
        Returns:
            int: 异议ID
        
        Raises:
            ScoringRecordNotFoundError: 评分记录不存在
            InvalidAppealError: 异议无效（如异议理由为空）
        """
        try:
            # 验证异议理由
            if not reason or reason.strip() == "":
                raise InvalidAppealError("异议理由不能为空")
            
            # 验证评分记录是否存在
            scoring_record = self.db.query(ScoringRecord).filter(
                ScoringRecord.id == scoring_record_id
            ).first()
            
            if not scoring_record:
                raise ScoringRecordNotFoundError(f"评分记录不存在: {scoring_record_id}")
            
            # 检查是否已经提交过异议
            existing_appeal = self.db.query(ScoringAppeal).filter(
                and_(
                    ScoringAppeal.scoring_record_id == scoring_record_id,
                    ScoringAppeal.status.in_(["pending", "reviewing"])
                )
            ).first()
            
            if existing_appeal:
                raise InvalidAppealError("该评分记录已有待处理的异议")
            
            # 创建异议记录
            appeal = ScoringAppeal(
                scoring_record_id=scoring_record_id,
                teacher_id=teacher_id,
                teacher_name=teacher_name,
                appeal_reason=reason.strip(),
                status="pending",
                created_at=datetime.utcnow()
            )
            
            self.db.add(appeal)
            self.db.commit()
            self.db.refresh(appeal)
            
            # 记录日志
            self._log_activity(
                action="appeal_submitted",
                scoring_record_id=scoring_record_id,
                details={
                    "appeal_id": appeal.id,
                    "teacher_id": teacher_id,
                    "teacher_name": teacher_name,
                    "reason_length": len(reason)
                }
            )
            
            # 通知管理员（这里可以扩展为发送邮件或系统通知）
            self._notify_admin_about_appeal(appeal)
            
            logger.info(f"异议提交成功: ID {appeal.id}, 评分记录: {scoring_record_id}, 教师: {teacher_name}")
            
            return appeal.id
            
        except (ScoringRecordNotFoundError, InvalidAppealError) as e:
            raise e
        except Exception as e:
            self.db.rollback()
            logger.error(f"提交异议失败: {str(e)}")
            raise ReviewManagerError(f"提交异议失败: {str(e)}")
    
    def get_pending_appeals(self, status: str = "pending") -> List[Dict]:
        """
        获取待处理的异议列表
        
        Args:
            status: 异议状态，默认为 "pending"
        
        Returns:
            list: 异议列表
        """
        try:
            appeals = self.db.query(ScoringAppeal).filter(
                ScoringAppeal.status == status
            ).order_by(ScoringAppeal.created_at.desc()).all()
            
            result = []
            for appeal in appeals:
                # 获取关联的评分记录
                scoring_record = self.db.query(ScoringRecord).filter(
                    ScoringRecord.id == appeal.scoring_record_id
                ).first()
                
                appeal_data = {
                    "id": appeal.id,
                    "scoring_record_id": appeal.scoring_record_id,
                    "teacher_id": appeal.teacher_id,
                    "teacher_name": appeal.teacher_name,
                    "appeal_reason": appeal.appeal_reason,
                    "status": appeal.status,
                    "created_at": appeal.created_at.isoformat() if appeal.created_at else None,
                    "reviewed_at": appeal.reviewed_at.isoformat() if appeal.reviewed_at else None,
                    "review_result": appeal.review_result
                }
                
                # 添加评分记录信息
                if scoring_record:
                    appeal_data.update({
                        "file_type": scoring_record.file_type,
                        "file_name": scoring_record.file_name,
                        "current_score": scoring_record.final_score,
                        "current_grade": scoring_record.grade,
                        "submission_id": scoring_record.submission_id
                    })
                
                result.append(appeal_data)
            
            logger.info(f"获取异议列表成功: 状态 {status}, 数量 {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"获取异议列表失败: {str(e)}")
            raise ReviewManagerError(f"获取异议列表失败: {str(e)}")
    
    def manual_review(self, scoring_record_id: int, admin_id: int, 
                     new_score_data: Dict) -> bool:
        """
        管理员人工复核并调整评分
        
        Args:
            scoring_record_id: 评分记录ID
            admin_id: 管理员ID
            new_score_data: 新的评分数据
        
        Returns:
            bool: 是否复核成功
        
        Raises:
            ScoringRecordNotFoundError: 评分记录不存在
        """
        try:
            # 获取原评分记录
            scoring_record = self.db.query(ScoringRecord).filter(
                ScoringRecord.id == scoring_record_id
            ).first()
            
            if not scoring_record:
                raise ScoringRecordNotFoundError(f"评分记录不存在: {scoring_record_id}")
            
            # 保存原始评分信息
            original_score = scoring_record.final_score
            original_grade = scoring_record.grade
            
            # 更新评分记录
            scoring_record.base_score = new_score_data.get('base_score', scoring_record.base_score)
            scoring_record.bonus_score = new_score_data.get('bonus_score', scoring_record.bonus_score)
            scoring_record.final_score = new_score_data.get('final_score', scoring_record.final_score)
            scoring_record.grade = new_score_data.get('grade', scoring_record.grade)
            scoring_record.score_details = new_score_data.get('score_details', scoring_record.score_details)
            scoring_record.scoring_type = "manual"
            scoring_record.scored_by = admin_id
            scoring_record.scored_at = datetime.utcnow()
            scoring_record.updated_at = datetime.utcnow()
            
            # 如果有否决项相关的调整
            if 'veto_triggered' in new_score_data:
                scoring_record.veto_triggered = new_score_data['veto_triggered']
                scoring_record.veto_reason = new_score_data.get('veto_reason', '')
            
            self.db.commit()
            
            # 记录复核记录
            review_record = ReviewRecord(
                scoring_record_id=scoring_record_id,
                review_type="appeal",  # 假设这是异议复核
                original_score=original_score,
                reviewed_score=scoring_record.final_score,
                is_consistent=(abs(original_score - scoring_record.final_score) < 0.1),
                difference_reason=new_score_data.get('review_reason', ''),
                reviewed_by=admin_id,
                reviewed_at=datetime.utcnow()
            )
            
            self.db.add(review_record)
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="manual_review",
                scoring_record_id=scoring_record_id,
                details={
                    "admin_id": admin_id,
                    "original_score": original_score,
                    "new_score": scoring_record.final_score,
                    "original_grade": original_grade,
                    "new_grade": scoring_record.grade
                }
            )
            
            # 更新相关异议状态
            appeal = self.db.query(ScoringAppeal).filter(
                and_(
                    ScoringAppeal.scoring_record_id == scoring_record_id,
                    ScoringAppeal.status.in_(["pending", "reviewing"])
                )
            ).first()
            
            if appeal:
                appeal.status = "resolved"
                appeal.reviewed_by = admin_id
                appeal.reviewed_at = datetime.utcnow()
                appeal.review_result = new_score_data.get('review_reason', '人工复核完成')
                self.db.commit()
            
            logger.info(f"人工复核完成: 评分记录 {scoring_record_id}, 管理员 {admin_id}")
            return True
            
        except ScoringRecordNotFoundError as e:
            raise e
        except Exception as e:
            self.db.rollback()
            logger.error(f"人工复核失败: {str(e)}")
            raise ReviewManagerError(f"人工复核失败: {str(e)}")
    
    def random_sample(self, sample_rate: float, task_id: Optional[str] = None) -> List[Dict]:
        """
        随机抽取样本进行复核
        
        Args:
            sample_rate: 抽查比例 (0.0-1.0)
            task_id: 可选的任务ID，限制抽查范围
        
        Returns:
            list: 抽查样本列表
        
        Raises:
            ReviewManagerError: 抽查失败
        """
        try:
            if not 0 <= sample_rate <= 1:
                raise ReviewManagerError("抽查比例必须在0-1之间")
            
            # 构建查询条件
            query = self.db.query(ScoringRecord).filter(
                and_(
                    ScoringRecord.scoring_type == "auto",  # 只抽查自动评分的记录
                    ScoringRecord.is_confirmed == True  # 只抽查已确认的记录
                )
            )
            
            # 如果指定了任务ID，则限制范围
            if task_id:
                # 通过submission_id关联到任务
                query = query.join(
                    MaterialSubmission, ScoringRecord.submission_id == MaterialSubmission.submission_id
                ).join(
                    EvaluationAssignmentTask, MaterialSubmission.teacher_id == EvaluationAssignmentTask.teacher_id
                ).filter(
                    EvaluationAssignmentTask.task_id == task_id
                )
            
            # 获取所有符合条件的记录
            all_records = query.all()
            
            if not all_records:
                logger.warning("没有找到符合抽查条件的评分记录")
                return []
            
            # 计算抽查数量
            sample_count = max(1, int(len(all_records) * sample_rate))
            
            # 随机抽取
            sampled_records = random.sample(all_records, sample_count)
            
            # 标记为待复核状态并返回结果
            result = []
            for record in sampled_records:
                # 检查是否已经有复核记录
                existing_review = self.db.query(ReviewRecord).filter(
                    and_(
                        ReviewRecord.scoring_record_id == record.id,
                        ReviewRecord.review_type == "random"
                    )
                ).first()
                
                if not existing_review:
                    # 创建复核记录占位符
                    review_record = ReviewRecord(
                        scoring_record_id=record.id,
                        review_type="random",
                        original_score=record.final_score,
                        reviewed_score=0,  # 待复核
                        is_consistent=False,  # 待确定
                        reviewed_by=0,  # 待分配
                        reviewed_at=datetime.utcnow()
                    )
                    self.db.add(review_record)
                
                # 获取提交信息
                submission = self.db.query(MaterialSubmission).filter(
                    MaterialSubmission.submission_id == record.submission_id
                ).first()
                
                record_data = {
                    "scoring_record_id": record.id,
                    "submission_id": record.submission_id,
                    "teacher_id": submission.teacher_id if submission else "",
                    "teacher_name": submission.teacher_name if submission else "",
                    "file_type": record.file_type,
                    "file_name": record.file_name,
                    "current_score": record.final_score,
                    "current_grade": record.grade,
                    "scored_at": record.scored_at.isoformat() if record.scored_at else None,
                    "status": "待复核"
                }
                
                result.append(record_data)
            
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="random_sample",
                details={
                    "sample_rate": sample_rate,
                    "total_records": len(all_records),
                    "sampled_count": len(result),
                    "task_id": task_id
                }
            )
            
            logger.info(f"随机抽查完成: 抽查比例 {sample_rate}, 总数 {len(all_records)}, 抽中 {len(result)}")
            return result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"随机抽查失败: {str(e)}")
            raise ReviewManagerError(f"随机抽查失败: {str(e)}")
    
    def record_review_result(self, scoring_record_id: int, reviewed_score: float,
                           is_consistent: bool, difference_reason: str = "",
                           reviewed_by: int = 0) -> bool:
        """
        记录复核结果
        
        Args:
            scoring_record_id: 评分记录ID
            reviewed_score: 复核后得分
            is_consistent: 是否一致
            difference_reason: 差异原因
            reviewed_by: 复核人ID
        
        Returns:
            bool: 是否记录成功
        """
        try:
            # 查找对应的复核记录
            review_record = self.db.query(ReviewRecord).filter(
                ReviewRecord.scoring_record_id == scoring_record_id
            ).order_by(ReviewRecord.created_at.desc()).first()
            
            if not review_record:
                raise ReviewManagerError(f"未找到评分记录 {scoring_record_id} 的复核记录")
            
            # 更新复核记录
            review_record.reviewed_score = reviewed_score
            review_record.is_consistent = is_consistent
            review_record.difference_reason = difference_reason
            review_record.reviewed_by = reviewed_by
            review_record.reviewed_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="review_result_recorded",
                scoring_record_id=scoring_record_id,
                details={
                    "reviewed_score": reviewed_score,
                    "is_consistent": is_consistent,
                    "difference_reason": difference_reason,
                    "reviewed_by": reviewed_by
                }
            )
            
            logger.info(f"复核结果记录成功: 评分记录 {scoring_record_id}, 一致性 {is_consistent}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"记录复核结果失败: {str(e)}")
            raise ReviewManagerError(f"记录复核结果失败: {str(e)}")
    
    def calculate_consistency_rate(self, start_date: str, end_date: str,
                                 task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        计算一致性比例
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            task_id: 可选的任务ID
        
        Returns:
            dict: 一致性统计结果
        """
        try:
            # 解析日期
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            
            # 构建查询条件
            query = self.db.query(ReviewRecord).filter(
                and_(
                    ReviewRecord.reviewed_at >= start_dt,
                    ReviewRecord.reviewed_at < end_dt,
                    ReviewRecord.reviewed_by > 0  # 已完成复核
                )
            )
            
            # 如果指定了任务ID，则限制范围
            if task_id:
                query = query.join(
                    ScoringRecord, ReviewRecord.scoring_record_id == ScoringRecord.id
                ).join(
                    MaterialSubmission, ScoringRecord.submission_id == MaterialSubmission.submission_id
                ).join(
                    EvaluationAssignmentTask, MaterialSubmission.teacher_id == EvaluationAssignmentTask.teacher_id
                ).filter(
                    EvaluationAssignmentTask.task_id == task_id
                )
            
            # 获取所有复核记录
            review_records = query.all()
            
            if not review_records:
                return {
                    "total_reviews": 0,
                    "consistent_count": 0,
                    "inconsistent_count": 0,
                    "consistency_rate": 0.0,
                    "difference_reasons": {},
                    "review_types": {"random": 0, "appeal": 0}
                }
            
            # 统计结果
            total_reviews = len(review_records)
            consistent_count = sum(1 for r in review_records if r.is_consistent)
            inconsistent_count = total_reviews - consistent_count
            consistency_rate = consistent_count / total_reviews if total_reviews > 0 else 0.0
            
            # 统计差异原因
            difference_reasons = {}
            review_types = {"random": 0, "appeal": 0}
            
            for record in review_records:
                # 统计复核类型
                if record.review_type in review_types:
                    review_types[record.review_type] += 1
                
                # 统计差异原因
                if not record.is_consistent and record.difference_reason:
                    reason = record.difference_reason.strip()
                    if reason:
                        difference_reasons[reason] = difference_reasons.get(reason, 0) + 1
            
            result = {
                "total_reviews": total_reviews,
                "consistent_count": consistent_count,
                "inconsistent_count": inconsistent_count,
                "consistency_rate": round(consistency_rate, 4),
                "difference_reasons": difference_reasons,
                "review_types": review_types,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            logger.info(f"一致性统计完成: {start_date} 到 {end_date}, 一致性比例 {consistency_rate:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"计算一致性比例失败: {str(e)}")
            raise ReviewManagerError(f"计算一致性比例失败: {str(e)}")
    
    def confirm_score(self, scoring_record_id: int, teacher_id: str) -> bool:
        """
        教师确认评分结果
        
        Args:
            scoring_record_id: 评分记录ID
            teacher_id: 教师ID
        
        Returns:
            bool: 是否确认成功
        """
        try:
            # 获取评分记录
            scoring_record = self.db.query(ScoringRecord).filter(
                ScoringRecord.id == scoring_record_id
            ).first()
            
            if not scoring_record:
                raise ScoringRecordNotFoundError(f"评分记录不存在: {scoring_record_id}")
            
            # 验证教师权限（确保只能确认自己的评分）
            submission = self.db.query(MaterialSubmission).filter(
                MaterialSubmission.submission_id == scoring_record.submission_id
            ).first()
            
            if not submission or submission.teacher_id != teacher_id:
                raise ReviewManagerError("无权限确认此评分记录")
            
            # 检查是否已经确认
            if scoring_record.is_confirmed:
                logger.warning(f"评分记录 {scoring_record_id} 已经确认过")
                return True
            
            # 确认评分
            scoring_record.is_confirmed = True
            scoring_record.confirmed_at = datetime.utcnow()
            scoring_record.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录日志
            self._log_activity(
                action="score_confirmed",
                scoring_record_id=scoring_record_id,
                details={
                    "teacher_id": teacher_id,
                    "final_score": scoring_record.final_score,
                    "grade": scoring_record.grade
                }
            )
            
            logger.info(f"评分确认成功: 记录 {scoring_record_id}, 教师 {teacher_id}")
            return True
            
        except (ScoringRecordNotFoundError, ReviewManagerError) as e:
            raise e
        except Exception as e:
            self.db.rollback()
            logger.error(f"确认评分失败: {str(e)}")
            raise ReviewManagerError(f"确认评分失败: {str(e)}")
    
    def publish_results(self, task_id: str, admin_id: int) -> Dict[str, Any]:
        """
        公示整体评分结果
        
        Args:
            task_id: 任务ID
            admin_id: 管理员ID
        
        Returns:
            dict: 公示结果统计
        """
        try:
            # 获取任务信息
            task = self.db.query(EvaluationAssignmentTask).filter(
                EvaluationAssignmentTask.task_id == task_id
            ).first()
            
            if not task:
                raise ReviewManagerError(f"任务不存在: {task_id}")
            
            # 获取该任务下所有的评分记录
            scoring_records = self.db.query(ScoringRecord).join(
                MaterialSubmission, ScoringRecord.submission_id == MaterialSubmission.submission_id
            ).join(
                EvaluationAssignmentTask, MaterialSubmission.teacher_id == EvaluationAssignmentTask.teacher_id
            ).filter(
                EvaluationAssignmentTask.task_id == task_id
            ).all()
            
            if not scoring_records:
                raise ReviewManagerError(f"任务 {task_id} 下没有评分记录")
            
            # 检查是否所有教师都已确认评分
            unconfirmed_records = [r for r in scoring_records if not r.is_confirmed]
            
            if unconfirmed_records:
                unconfirmed_teachers = []
                for record in unconfirmed_records:
                    submission = self.db.query(MaterialSubmission).filter(
                        MaterialSubmission.submission_id == record.submission_id
                    ).first()
                    if submission:
                        unconfirmed_teachers.append(submission.teacher_name)
                
                raise ReviewManagerError(f"以下教师尚未确认评分结果，无法公示: {', '.join(set(unconfirmed_teachers))}")
            
            # 统计公示结果
            total_teachers = len(set(r.submission_id for r in scoring_records))
            grade_distribution = {}
            score_stats = {
                "max_score": 0,
                "min_score": 100,
                "avg_score": 0,
                "total_score": 0
            }
            
            for record in scoring_records:
                # 统计等级分布
                grade = record.grade
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
                
                # 统计分数
                score = record.final_score
                score_stats["max_score"] = max(score_stats["max_score"], score)
                score_stats["min_score"] = min(score_stats["min_score"], score)
                score_stats["total_score"] += score
            
            score_stats["avg_score"] = round(score_stats["total_score"] / len(scoring_records), 2) if scoring_records else 0
            
            # 更新任务状态为已公示
            # 这里可以添加一个字段来标记任务已公示，或者在任务表中添加相应字段
            
            # 记录公示日志
            self._log_activity(
                action="results_published",
                details={
                    "task_id": task_id,
                    "admin_id": admin_id,
                    "total_teachers": total_teachers,
                    "total_records": len(scoring_records),
                    "grade_distribution": grade_distribution,
                    "score_stats": score_stats
                }
            )
            
            result = {
                "task_id": task_id,
                "published_at": datetime.utcnow().isoformat(),
                "published_by": admin_id,
                "total_teachers": total_teachers,
                "total_records": len(scoring_records),
                "grade_distribution": grade_distribution,
                "score_statistics": score_stats,
                "status": "published"
            }
            
            logger.info(f"评分结果公示成功: 任务 {task_id}, 涉及 {total_teachers} 名教师")
            return result
            
        except ReviewManagerError as e:
            raise e
        except Exception as e:
            logger.error(f"公示评分结果失败: {str(e)}")
            raise ReviewManagerError(f"公示评分结果失败: {str(e)}")
    
    def get_task_confirmation_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务的确认状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            dict: 确认状态统计
        """
        try:
            # 获取该任务下所有的评分记录
            scoring_records = self.db.query(ScoringRecord).join(
                MaterialSubmission, ScoringRecord.submission_id == MaterialSubmission.submission_id
            ).join(
                EvaluationAssignmentTask, MaterialSubmission.teacher_id == EvaluationAssignmentTask.teacher_id
            ).filter(
                EvaluationAssignmentTask.task_id == task_id
            ).all()
            
            if not scoring_records:
                return {
                    "task_id": task_id,
                    "total_records": 0,
                    "confirmed_count": 0,
                    "unconfirmed_count": 0,
                    "confirmation_rate": 0.0,
                    "can_publish": False,
                    "unconfirmed_teachers": []
                }
            
            confirmed_count = sum(1 for r in scoring_records if r.is_confirmed)
            unconfirmed_count = len(scoring_records) - confirmed_count
            confirmation_rate = confirmed_count / len(scoring_records) if scoring_records else 0.0
            
            # 获取未确认的教师列表
            unconfirmed_teachers = []
            for record in scoring_records:
                if not record.is_confirmed:
                    submission = self.db.query(MaterialSubmission).filter(
                        MaterialSubmission.submission_id == record.submission_id
                    ).first()
                    if submission:
                        unconfirmed_teachers.append({
                            "teacher_id": submission.teacher_id,
                            "teacher_name": submission.teacher_name,
                            "file_type": record.file_type,
                            "score": record.final_score,
                            "grade": record.grade
                        })
            
            return {
                "task_id": task_id,
                "total_records": len(scoring_records),
                "confirmed_count": confirmed_count,
                "unconfirmed_count": unconfirmed_count,
                "confirmation_rate": round(confirmation_rate, 4),
                "can_publish": unconfirmed_count == 0,
                "unconfirmed_teachers": unconfirmed_teachers
            }
            
        except Exception as e:
            logger.error(f"获取任务确认状态失败: {str(e)}")
            raise ReviewManagerError(f"获取任务确认状态失败: {str(e)}")
    
    def _notify_admin_about_appeal(self, appeal: ScoringAppeal) -> None:
        """
        通知管理员有新的异议申请
        
        Args:
            appeal: 异议记录
        """
        try:
            # 这里可以实现具体的通知逻辑，比如：
            # 1. 发送邮件
            # 2. 系统内消息通知
            # 3. 推送通知
            # 目前只记录日志
            logger.info(f"通知管理员: 新异议申请 {appeal.id}, 教师: {appeal.teacher_name}")
            
            # 可以在这里添加具体的通知实现
            # send_email_to_admin(appeal)
            # create_system_notification(appeal)
            
        except Exception as e:
            logger.error(f"通知管理员失败: {str(e)}")
            # 通知失败不应该影响主流程，所以不抛出异常
    
    def _log_activity(self, action: str, scoring_record_id: Optional[int] = None,
                     details: Optional[Dict] = None) -> None:
        """
        记录活动日志
        
        Args:
            action: 操作类型
            scoring_record_id: 评分记录ID
            details: 详细信息
        """
        try:
            import json
            
            log_entry = ScoringLog(
                scoring_record_id=scoring_record_id,
                action=action,
                action_by=None,  # 这里可以从上下文获取当前用户ID
                action_details=json.dumps(details, ensure_ascii=False) if details else None,
                created_at=datetime.utcnow()
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"记录活动日志失败: {str(e)}")
            # 日志记录失败不应该影响主流程
         