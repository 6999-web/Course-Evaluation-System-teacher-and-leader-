from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, JSON
from database import Base
import enum
import uuid
from datetime import datetime

class StatusEnum(str, enum.Enum):
    enable = "enable"
    disable = "disable"

class ReportTypeEnum(str, enum.Enum):
    school = "school"
    department = "department"
    personal = "personal"

class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"

# 用户表 - 用于认证和授权
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.teacher)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class SystemConfig(Base):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String, index=True)
    evaluation_plan = Column(JSON)
    time_windows = Column(JSON)
    status = Column(Enum(StatusEnum))

class EvaluationTask(Base):
    __tablename__ = "evaluation_tasks"
    task_id = Column(String, primary_key=True, index=True)
    course_id = Column(String, index=True)
    teacher_id = Column(String, index=True)
    student_count = Column(Integer)
    completed_count = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)


class EvaluationData(Base):
    __tablename__ = "evaluation_data"
    record_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, index=True)
    student_hash = Column(String, index=True)
    dimension_scores = Column(JSON)
    text_feedback = Column(Text)
    submission_time = Column(DateTime, default=datetime.utcnow)
    validity_flag = Column(Boolean, default=True)

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"
    report_id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum(ReportTypeEnum))
    target_scope = Column(JSON)
    data_period = Column(String)
    generated_time = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String)
    access_log = Column(JSON)

class Course(Base):
    __tablename__ = "courses"
    course_id = Column(String, primary_key=True, index=True)
    course_name = Column(String)
    department_id = Column(String, index=True)

class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(String, primary_key=True, index=True)
    teacher_name = Column(String)
    department_id = Column(String, index=True)

class Department(Base):
    __tablename__ = "departments"
    department_id = Column(String, primary_key=True, index=True)
    department_name = Column(String)


# ==================== 材料分发与回收相关模型 ====================

class EvaluationForm(Base):
    """考评表模型"""
    __tablename__ = "evaluation_forms"
    
    form_id = Column(String, primary_key=True, default=lambda: f"form_{uuid.uuid4().hex[:8]}")
    name = Column(String(200), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    dimensions = Column(JSON, nullable=False)  # ["teaching_attitude", "teaching_content", ...]
    participants = Column(JSON, nullable=False)  # ["teacher_id_1", "teacher_id_2", ...]
    form_data = Column(JSON, nullable=False)  # 考评表数据
    created_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default="draft")  # draft, published, archived


class DistributionRecord(Base):
    """分发记录模型"""
    __tablename__ = "distribution_records"
    
    distribution_id = Column(String, primary_key=True, default=lambda: f"dist_{uuid.uuid4().hex[:8]}")
    material_id = Column(String, nullable=False)  # 文件ID或考评表ID
    material_type = Column(String(20), nullable=False)  # "file" or "evaluation_form"
    material_name = Column(String(200), nullable=False)
    distribution_type = Column(String(20), nullable=False)  # "batch" or "targeted"
    target_teachers = Column(JSON, nullable=False)  # [{"teacher_id": "xxx", "teacher_name": "xxx"}, ...]
    distributed_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    distributed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="completed")  # pending, completed, failed


class MaterialSubmission(Base):
    """材料提交模型"""
    __tablename__ = "material_submissions"
    
    submission_id = Column(String, primary_key=True, default=lambda: f"sub_{uuid.uuid4().hex[:8]}")
    teacher_id = Column(String, nullable=False, index=True)
    teacher_name = Column(String(100), nullable=False)
    files = Column(JSON, nullable=False)  # [{"file_id": "xxx", "file_name": "xxx", "file_size": 123, "file_url": "xxx"}, ...]
    notes = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    review_status = Column(String(20), default="pending")  # pending, approved, rejected, needs_revision
    review_feedback = Column(Text)
    reviewed_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    reviewed_at = Column(DateTime, nullable=True)


# ==================== 考评表相关模型 ====================

class EvaluationTemplate(Base):
    """考评表模板"""
    __tablename__ = "evaluation_templates"
    
    template_id = Column(String, primary_key=True, default=lambda: f"tpl_{uuid.uuid4().hex[:8]}")
    name = Column(String(200), nullable=False)  # 考评表名称
    description = Column(Text)  # 描述
    file_url = Column(String(500), nullable=False)  # 考评表文件路径
    file_name = Column(String(200), nullable=False)  # 原始文件名
    file_type = Column(String(20), nullable=False)  # pdf, excel, word
    file_size = Column(Integer)  # 文件大小
    
    # 评分标准
    scoring_criteria = Column(JSON, nullable=False)  # [{"name": "完成度", "max_score": 10}, ...]
    total_score = Column(Integer, default=100)  # 总分
    
    # 提交要求
    submission_requirements = Column(JSON, nullable=False)  # {"file_types": ["pdf", "excel"], "max_files": 3, "description": "..."}
    deadline = Column(DateTime, nullable=False)  # 截止时间
    
    # 分配信息
    target_teachers = Column(JSON, nullable=False)  # [{"teacher_id": "xxx", "teacher_name": "xxx"}, ...]
    distribution_type = Column(String(20), default="batch")  # batch, targeted
    
    # 状态
    status = Column(String(20), default="draft")  # draft, published, closed
    created_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvaluationAssignmentTask(Base):
    """考评任务（分配给教师的考评表）"""
    __tablename__ = "evaluation_assignment_tasks"
    
    task_id = Column(String, primary_key=True, default=lambda: f"task_{uuid.uuid4().hex[:8]}")
    template_id = Column(String, nullable=False, index=True)  # ForeignKey("evaluation_templates.template_id")
    teacher_id = Column(String, nullable=False, index=True)
    teacher_name = Column(String(100), nullable=False)
    
    # 任务状态
    status = Column(String(20), default="pending")  # pending, submitted, scored, completed
    
    # 提交信息
    submitted_files = Column(JSON)  # [{"file_id": "xxx", "file_name": "xxx", "file_size": 123, "file_url": "xxx"}, ...]
    submitted_at = Column(DateTime, nullable=True)
    submission_notes = Column(Text)
    
    # 评分信息
    scores = Column(JSON)  # {"完成度": 8, "准确性": 9, "规范性": 7}
    total_score = Column(Float, nullable=True)
    scoring_feedback = Column(Text)
    scored_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    scored_at = Column(DateTime, nullable=True)
    
    # 修改记录
    score_history = Column(JSON)  # [{"old_score": 20, "new_score": 25, "reason": "...", "changed_at": "...", "changed_by": "..."}, ...]
    
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
