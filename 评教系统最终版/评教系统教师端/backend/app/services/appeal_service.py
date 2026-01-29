from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.schemas.appeal import AppealItem


class AppealService:
    """申诉服务"""
    
    def get_appeal_list(self, db: Session, skip: int = 0, limit: int = 10) -> List[AppealItem]:
        """获取申诉列表"""
        # 这里简化实现，实际项目中需要从数据库查询
        # 模拟数据
        appeals = [
            AppealItem(
                id=1,
                evaluation_id=1,
                course_name="高等数学",
                appeal_reason="评分过低，与实际教学情况不符",
                status="处理中",
                submit_date=datetime.now() - timedelta(days=2)
            ),
            AppealItem(
                id=2,
                evaluation_id=3,
                course_name="大学物理",
                appeal_reason="评估系统出现错误",
                status="已处理",
                submit_date=datetime.now() - timedelta(days=5),
                process_date=datetime.now() - timedelta(days=2),
                process_result="申诉成功，已重新评估",
                process_by="管理员"
            )
        ]
        
        return appeals
    
    def submit_appeal(self, db: Session, appeal_data: dict) -> dict:
        """提交申诉"""
        # 这里简化实现，实际项目中需要保存到数据库
        return {
            "status": "success",
            "message": "申诉提交成功",
            "appeal_id": 3
        }
    
    def process_appeal(self, db: Session, appeal_id: int, action: str) -> dict:
        """处理申诉"""
        # 这里简化实现，实际项目中需要更新数据库
        return {
            "status": "success",
            "message": f"申诉 {appeal_id} 已{action}"
        }
