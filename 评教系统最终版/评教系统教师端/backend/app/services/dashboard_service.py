from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.models.evaluation_task import EvaluationTask
from app.models.evaluation_data import EvaluationData
from app.schemas.dashboard import DashboardStats, RecentEvaluation


class DashboardService:
    """仪表盘服务"""
    
    def get_dashboard_stats(self, db: Session) -> DashboardStats:
        """获取仪表盘统计数据"""
        # 获取总评估次数
        total_evaluations = db.query(EvaluationData).count()
        
        # 获取平均评分
        avg_score_result = db.query(
            db.func.avg(EvaluationData.score)
        ).scalar()
        average_score = round(float(avg_score_result), 2) if avg_score_result else 0.0
        
        # 获取完成率
        total_tasks = db.query(EvaluationTask).count()
        completed_tasks = db.query(EvaluationTask).filter(
            EvaluationTask.status == "completed"
        ).count()
        completion_rate = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0.0
        
        # 获取最近趋势
        # 这里简单实现，实际项目中可能需要更复杂的逻辑
        recent_trend = "上升" if average_score > 4.0 else "下降"
        
        # 获取正面、负面、中性评价比例
        # 这里简单实现，实际项目中可能需要根据具体的评价内容进行分析
        positive_rate = 65.5
        negative_rate = 15.3
        neutral_rate = 19.2
        
        return DashboardStats(
            total_evaluations=total_evaluations,
            average_score=average_score,
            completion_rate=completion_rate,
            recent_trend=recent_trend,
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            neutral_rate=neutral_rate
        )
    
    def get_recent_evaluations(self, db: Session, limit: int = 5) -> List[RecentEvaluation]:
        """获取最近的评估记录"""
        recent_evaluations = db.query(EvaluationData).order_by(
            EvaluationData.evaluation_date.desc()
        ).limit(limit).all()
        
        result = []
        for eval_data in recent_evaluations:
            recent_eval = RecentEvaluation(
                id=eval_data.id,
                course_name=eval_data.course_name,
                evaluation_date=eval_data.evaluation_date,
                score=eval_data.score,
                feedback_count=1 if eval_data.feedback else 0,
                status="已完成"
            )
            result.append(recent_eval)
        
        return result
