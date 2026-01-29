from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.schemas.review import ReviewItem


class ReviewService:
    """审核服务"""
    
    def get_review_list(self, db: Session, skip: int = 0, limit: int = 10) -> List[ReviewItem]:
        """获取审核列表"""
        # 这里简化实现，实际项目中需要从数据库查询
        # 模拟数据
        reviews = [
            ReviewItem(
                id=1,
                item_type="申诉",
                item_id=1,
                content="高等数学课程评分申诉",
                status="待审核",
                submit_date=datetime.now() - timedelta(days=2)
            ),
            ReviewItem(
                id=2,
                item_type="评估任务",
                item_id=1,
                content="2024年第一学期评估任务",
                status="已审核",
                submit_date=datetime.now() - timedelta(days=15),
                review_date=datetime.now() - timedelta(days=10),
                review_result="审核通过",
                review_by="管理员"
            )
        ]
        
        return reviews
    
    def process_review(self, db: Session, review_id: int, action: str) -> dict:
        """处理审核"""
        # 这里简化实现，实际项目中需要更新数据库
        return {
            "status": "success",
            "message": f"审核 {review_id} 已{action}"
        }
