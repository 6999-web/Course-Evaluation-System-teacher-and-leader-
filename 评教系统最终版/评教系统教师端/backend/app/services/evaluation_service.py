from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.evaluation_task import EvaluationTask
from app.models.evaluation_data import EvaluationData
from app.schemas.evaluation import EvaluationTask as EvaluationTaskSchema
from app.schemas.evaluation import EvaluationData as EvaluationDataSchema


class EvaluationService:
    """评估服务"""
    
    def get_evaluation_tasks(self, db: Session, skip: int = 0, limit: int = 10) -> List[EvaluationTaskSchema]:
        """获取评估任务列表"""
        tasks = db.query(EvaluationTask).offset(skip).limit(limit).all()
        
        result = []
        for task in tasks:
            task_schema = EvaluationTaskSchema(
                id=task.id,
                task_name=task.task_name,
                start_date=task.start_date,
                end_date=task.end_date,
                status=task.status,
                total_students=task.total_students,
                completed_students=task.completed_students,
                completion_rate=round((task.completed_students / task.total_students * 100), 2) if task.total_students > 0 else 0.0
            )
            result.append(task_schema)
        
        return result
    
    def get_evaluation_task(self, db: Session, task_id: int) -> EvaluationTaskSchema:
        """获取评估任务详情"""
        task = db.query(EvaluationTask).filter(EvaluationTask.id == task_id).first()
        
        if not task:
            raise ValueError(f"Task with id {task_id} not found")
        
        return EvaluationTaskSchema(
            id=task.id,
            task_name=task.task_name,
            start_date=task.start_date,
            end_date=task.end_date,
            status=task.status,
            total_students=task.total_students,
            completed_students=task.completed_students,
            completion_rate=round((task.completed_students / task.total_students * 100), 2) if task.total_students > 0 else 0.0
        )
    
    def get_evaluation_data(self, db: Session, task_id: Optional[int] = None, skip: int = 0, limit: int = 10) -> List[EvaluationDataSchema]:
        """获取评估数据列表"""
        query = db.query(EvaluationData)
        
        if task_id:
            query = query.filter(EvaluationData.task_id == task_id)
        
        evaluations = query.offset(skip).limit(limit).all()
        
        result = []
        for eval_data in evaluations:
            eval_schema = EvaluationDataSchema(
                id=eval_data.id,
                task_id=eval_data.task_id,
                course_id=eval_data.course_id,
                course_name=eval_data.course_name,
                teacher_id=eval_data.teacher_id,
                teacher_name=eval_data.teacher_name,
                score=eval_data.score,
                feedback=eval_data.feedback,
                evaluation_date=eval_data.evaluation_date,
                student_id=eval_data.student_id,
                student_name=eval_data.student_name
            )
            result.append(eval_schema)
        
        return result
