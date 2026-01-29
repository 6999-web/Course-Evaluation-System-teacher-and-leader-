from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.schemas.feedback import FeedbackItem


class FeedbackService:
    """反馈服务"""
    
    def get_feedback_list(self, db: Session, skip: int = 0, limit: int = 10, type: Optional[str] = None) -> List[FeedbackItem]:
        """获取反馈列表"""
        # 这里简化实现，实际项目中需要从数据库查询
        # 模拟数据
        feedbacks = [
            FeedbackItem(
                id=1,
                evaluation_id=1,
                course_name="高等数学",
                content="老师讲课很生动，容易理解",
                feedback_type="positive",
                status="处理中",
                submit_date=datetime.now() - timedelta(days=1)
            ),
            FeedbackItem(
                id=2,
                evaluation_id=2,
                course_name="大学英语",
                content="希望老师能多安排一些口语练习",
                feedback_type="suggestion",
                status="已处理",
                submit_date=datetime.now() - timedelta(days=2),
                process_date=datetime.now() - timedelta(days=1),
                process_by="管理员"
            )
        ]
        
        return feedbacks
    
    def process_feedback(self, db: Session, feedback_id: int, action: str) -> dict:
        """处理反馈"""
        # 这里简化实现，实际项目中需要更新数据库
        return {
            "status": "success",
            "message": f"反馈 {feedback_id} 已{action}"
        }
