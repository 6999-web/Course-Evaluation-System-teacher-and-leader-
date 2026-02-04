from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, JSON
from app.database import Base
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
    
    # 自动评分系统扩展字段
    scoring_status = Column(String(20), default="pending")  # pending, scoring, scored, failed
    parsed_content = Column(Text)  # 解析后的文本内容
    file_hash = Column(String(64))  # 文件哈希值
    encrypted_path = Column(String(500))  # 加密后的文件路径
    scoring_result = Column(JSON)  # 评分结果 {"base_score": 85, "bonus_score": 5, "final_score": 90, "grade": "优秀", ...}


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
    
    # 查收状态
    is_viewed = Column(Boolean, default=False)  # 是否已查收（教师点击查看）
    viewed_at = Column(DateTime, nullable=True)  # 查收时间
    
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
    
    # 自动评分系统扩展字段
    required_file_types = Column(JSON)  # JSON格式的必需文件类型列表 ["教案", "教学反思", ...]
    bonus_enabled = Column(Boolean, default=True)  # 是否启用加分项
    max_bonus_score = Column(Float, default=10)  # 最大加分值
    auto_scoring_enabled = Column(Boolean, default=True)  # 是否启用自动评分
    
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



# ==================== 自动评分系统相关模型 ====================

class ScoringTemplate(Base):
    """评分模板表 - 管理5类文件的提示词模板"""
    __tablename__ = "scoring_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    file_type = Column(String(50), nullable=False, unique=True, index=True)  # 文件类型：教案、教学反思、教研/听课记录、成绩/学情分析、课件
    template_content = Column(Text, nullable=False)  # JSON格式的模板内容
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # ForeignKey("users.id")


class ScoringRecord(Base):
    """评分记录表 - 存储每次评分的详细结果"""
    __tablename__ = "scoring_records"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String, nullable=False, index=True)  # 关联 material_submissions.submission_id
    file_id = Column(String, nullable=False)  # 具体文件ID
    file_type = Column(String(50), nullable=False)  # 文件类型
    file_name = Column(String(200), nullable=False)  # 文件名
    
    # 评分结果
    base_score = Column(Float, nullable=False)  # 基础分
    bonus_score = Column(Float, default=0)  # 加分
    final_score = Column(Float, nullable=False)  # 最终得分
    grade = Column(String(20), nullable=False)  # 等级：优秀、良好、合格、不合格
    
    # 评分详情
    score_details = Column(Text)  # JSON格式的得分明细
    veto_triggered = Column(Boolean, default=False)  # 是否触发否决项
    veto_reason = Column(Text)  # 否决原因
    
    # 评分元信息
    scoring_type = Column(String(20), default="auto")  # auto/manual
    scored_by = Column(Integer, nullable=True)  # ForeignKey("users.id") - 评分人（自动评分时为系统）
    scored_at = Column(DateTime, default=datetime.utcnow)
    
    # 确认状态
    is_confirmed = Column(Boolean, default=False)  # 教师是否确认
    confirmed_at = Column(DateTime, nullable=True)  # 确认时间
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScoringAppeal(Base):
    """评分异议表 - 处理教师对评分结果的异议"""
    __tablename__ = "scoring_appeals"
    
    id = Column(Integer, primary_key=True, index=True)
    scoring_record_id = Column(Integer, nullable=False, index=True)  # ForeignKey("scoring_records.id")
    teacher_id = Column(String, nullable=False, index=True)  # 教师ID
    teacher_name = Column(String(100), nullable=False)  # 教师姓名
    
    # 异议内容
    appeal_reason = Column(Text, nullable=False)  # 异议理由
    status = Column(String(20), default="pending")  # pending/reviewing/resolved
    
    # 复核信息
    reviewed_by = Column(Integer, nullable=True)  # ForeignKey("users.id") - 复核人
    review_result = Column(Text)  # 复核结果
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReviewRecord(Base):
    """复核记录表 - 记录人工复核的详细信息"""
    __tablename__ = "review_records"
    
    id = Column(Integer, primary_key=True, index=True)
    scoring_record_id = Column(Integer, nullable=False, index=True)  # ForeignKey("scoring_records.id")
    review_type = Column(String(20), nullable=False)  # random/appeal - 随机抽查/异议复核
    
    # 复核对比
    original_score = Column(Float, nullable=False)  # 原始得分
    reviewed_score = Column(Float, nullable=False)  # 复核后得分
    is_consistent = Column(Boolean, nullable=False)  # 是否一致
    difference_reason = Column(Text)  # 差异原因
    
    # 复核人信息
    reviewed_by = Column(Integer, nullable=False)  # ForeignKey("users.id")
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class BonusItem(Base):
    """加分项表 - 管理教师的加分项"""
    __tablename__ = "bonus_items"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String, nullable=False, index=True)  # 关联 material_submissions.submission_id
    teacher_id = Column(String, nullable=False, index=True)  # 教师ID
    
    # 加分项信息
    item_name = Column(String(100), nullable=False)  # 加分项名称：获奖、论文、创新等
    score = Column(Float, nullable=False)  # 加分值
    evidence = Column(Text)  # 佐证材料描述
    evidence_files = Column(JSON)  # 佐证文件列表
    
    # 审核状态
    status = Column(String(20), default="pending")  # pending/approved/rejected
    
    # 添加人信息
    added_by = Column(Integer, nullable=False)  # ForeignKey("users.id")
    added_at = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScoringLog(Base):
    """评分日志表 - 记录所有评分相关操作"""
    __tablename__ = "scoring_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    scoring_record_id = Column(Integer, nullable=True, index=True)  # ForeignKey("scoring_records.id")
    
    # 操作信息
    action = Column(String(50), nullable=False)  # create/update/appeal/review/confirm/publish
    action_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    action_details = Column(Text)  # JSON格式的详细信息
    
    # 关联信息
    related_id = Column(String)  # 关联的其他记录ID（如异议ID、复核ID等）
    related_type = Column(String(50))  # 关联类型
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemScoringConfig(Base):
    """系统评分配置表 - 管理系统级别的评分配置"""
    __tablename__ = "system_scoring_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), nullable=False, unique=True, index=True)  # 配置键
    config_value = Column(Text, nullable=False)  # 配置值（JSON格式）
    description = Column(Text)  # 配置描述
    
    # 试运行模式配置
    is_trial_mode = Column(Boolean, default=True)  # 是否为试运行模式
    
    updated_by = Column(Integer, nullable=True)  # ForeignKey("users.id")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
