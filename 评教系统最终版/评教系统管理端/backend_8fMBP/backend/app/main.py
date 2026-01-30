from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import redis
import json
import os
import shutil
import uuid
from datetime import datetime, timedelta
from app.services import sync_distribution_to_teacher, sync_review_status_to_teacher

from app.database import get_db, engine, Base
from app.models import (
    SystemConfig, EvaluationTask, EvaluationData, AnalysisReport, User,
    EvaluationForm, DistributionRecord, MaterialSubmission,
    Teacher, Course, Department, EvaluationTemplate, EvaluationAssignmentTask
)
from app.schemas import (
    UserRegister, UserLogin, LoginResponse, RegisterResponse, 
    MessageResponse, UserResponse, Token,
    EvaluationFormCreate, EvaluationFormResponse,
    MaterialDistributeRequest, DistributionRecordResponse,
    MaterialSubmissionResponse, ReviewStatusUpdate
)
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

# 创建所有数据表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 从环境变量读取允许的源
origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = origins_env.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端域名列表
    allow_credentials=True,  # ⚠️ 必须为 True，否则前端无法携带 Cookie/Session 登录
    allow_methods=["*"],      # 允许的方法：GET, POST, PUT, DELETE 等
    allow_headers=["*"],      # 允许的请求头：Authorization, Content-Type 等
)

# 配置静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 暂时禁用Redis，使用内存存储
redis_client = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, department_id: str):
        await websocket.accept()
        if department_id not in self.active_connections:
            self.active_connections[department_id] = []
        self.active_connections[department_id].append(websocket)

    def disconnect(self, websocket: WebSocket, department_id: str):
        if department_id in self.active_connections:
            self.active_connections[department_id].remove(websocket)
            if not self.active_connections[department_id]:
                del self.active_connections[department_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, department_id: str = None):
        if department_id:
            if department_id in self.active_connections:
                for connection in self.active_connections[department_id]:
                    await connection.send_text(message)
        else:
            for dept_connections in self.active_connections.values():
                for connection in dept_connections:
                    await connection.send_text(message)

manager = ConnectionManager()

# ==================== 认证接口 ====================

@app.post("/api/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - 验证用户名和邮箱是否已存在
    - 密码使用 bcrypt 加密
    - 创建新用户记录
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被注册"
            )
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role="teacher",  # 默认角色为教师
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return RegisterResponse(
            message="注册成功",
            user=UserResponse.from_orm(new_user)
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@app.post("/api/login", response_model=LoginResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - 支持用户名或邮箱登录
    - 验证密码
    - 返回 JWT 令牌
    """
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        message="登录成功",
        token=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        user=UserResponse.from_orm(user)
    )


@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    
    需要在请求头中携带 JWT 令牌：
    Authorization: Bearer <token>
    """
    return UserResponse.from_orm(current_user)


@app.post("/api/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用户登出接口
    
    注意：JWT 是无状态的，实际的登出由前端删除令牌实现
    此接口主要用于记录登出日志或执行其他清理操作
    """
    return MessageResponse(
        message="登出成功",
        detail=f"用户 {current_user.username} 已登出"
    )


# ==================== 教师管理接口 ====================

@app.post("/api/teachers", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建教师记录
    
    - 接收教师ID、教师名称、部门ID等信息
    - 创建教师记录
    """
    try:
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")
        department_id = data.get("department_id", "dept_001")
        
        if not teacher_id or not teacher_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师ID和教师名称不能为空"
            )
        
        # 检查教师是否已存在
        existing = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师已存在"
            )
        
        # 创建教师记录
        teacher = Teacher(
            teacher_id=teacher_id,
            teacher_name=teacher_name,
            department_id=department_id
        )
        
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        return {
            "message": "教师创建成功",
            "teacher_id": teacher.teacher_id,
            "teacher_name": teacher.teacher_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建教师失败: {str(e)}"
        )


@app.get("/api/teachers", response_model=dict)
async def get_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有教师列表
    """
    try:
        teachers = db.query(Teacher).all()
        
        teachers_data = []
        for teacher in teachers:
            teachers_data.append({
                "teacher_id": teacher.teacher_id,
                "teacher_name": teacher.teacher_name,
                "department_id": teacher.department_id
            })
        
        return {
            "teachers": teachers_data,
            "total": len(teachers_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教师列表失败: {str(e)}"
        )


# ==================== 原有接口（需要认证） ====================

@app.websocket("/ws/monitoring/{department_id}")
async def websocket_endpoint(websocket: WebSocket, department_id: str):
    await manager.connect(websocket, department_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, department_id)

@app.post("/config/evaluation-plan")
async def create_evaluation_plan(plan_data: dict, db: Session = Depends(get_db)):
    new_plan = SystemConfig(
        academic_year=plan_data.get("academic_year"),
        evaluation_plan=plan_data.get("evaluation_plan"),
        time_windows=plan_data.get("time_windows"),
        status=plan_data.get("status", "disable")
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return {"message": "Evaluation plan created successfully", "plan_id": new_plan.id}

@app.get("/monitoring/dashboard")
async def get_dashboard_data(academic_year: str, department_id: str = None, db: Session = Depends(get_db)):
    try:
        tasks = db.query(EvaluationTask).all()
        total_students = sum(task.student_count for task in tasks)
        completed_students = sum(task.completed_count for task in tasks)
        overall_progress = (completed_students / total_students * 100) if total_students > 0 else 0
    except Exception as e:
        # 如果表不存在或查询失败，返回默认数据
        overall_progress = 0
    
    return {
        "overall_progress": overall_progress,
        "department_ranking": [],
        "warning_courses": []
    }

@app.post("/upload/materials")
async def upload_materials(file: UploadFile = File(...)):
    """上传分发材料"""
    try:
        # 创建uploads目录
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 验证文件类型
        allowed_types = ['pdf', 'docx', 'xlsx', 'png', 'jpg', 'jpeg']
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型。允许的类型: {', '.join(allowed_types)}"
            )
        
        # 验证文件大小（50MB限制）
        max_size = 50 * 1024 * 1024  # 50MB
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（最大50MB）"
            )
        
        # 生成唯一文件名
        import uuid
        file_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}_{file.filename}"
        
        # 保存文件
        file_location = os.path.join(upload_dir, file_id)
        with open(file_location, "wb+") as file_object:
            content = await file.read()
            file_object.write(content)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_id": file_id,
            "file_size": file_size,
            "url": f"/uploads/{file_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )

@app.post("/distribute/materials")
async def distribute_materials(data: dict):
    """分发材料给教师"""
    try:
        files = data.get("files", [])
        recipients = data.get("recipients", [])
        
        # 这里应该实现实际的分发逻辑
        # 例如：发送邮件、推送通知等
        
        return {
            "message": "Materials distributed successfully",
            "count": len(files),
            "recipients": len(recipients)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluation/generate-table")
async def generate_evaluation_table(data: dict):
    """生成考评表"""
    try:
        name = data.get("name")
        participants = data.get("participants", [])
        dimensions = data.get("dimensions", [])
        
        # 生成考评表数据
        table_data = []
        # 这里应该从数据库获取实际数据
        
        return {
            "message": "Evaluation table generated successfully",
            "data": table_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 材料分发与回收 API ====================

@app.post("/api/evaluation-forms/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_evaluation_form(
    form_data: EvaluationFormCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成考评表
    
    - 接收考评表配置（名称、日期、维度、参与者）
    - 验证输入数据（日期范围、必填字段）
    - 生成考评表数据并存储到数据库
    - 返回考评表ID和预览数据
    """
    try:
        # 生成考评表数据结构
        form_data_dict = {
            "dimensions": form_data.dimensions,
            "participants": form_data.participants,
            "structure": {
                "headers": ["教师姓名", "教师ID"] + form_data.dimensions + ["总分", "备注"],
                "rows": []
            }
        }
        
        # 为每个参与者创建一行
        for participant_id in form_data.participants:
            row = {
                "teacher_id": participant_id,
                "teacher_name": f"教师_{participant_id}",  # 实际应从数据库查询
                "scores": {dim: 0 for dim in form_data.dimensions},
                "total_score": 0,
                "notes": ""
            }
            form_data_dict["structure"]["rows"].append(row)
        
        # 创建考评表记录
        new_form = EvaluationForm(
            name=form_data.name,
            start_date=datetime.combine(form_data.start_date, datetime.min.time()),
            end_date=datetime.combine(form_data.end_date, datetime.min.time()),
            dimensions=form_data.dimensions,
            participants=form_data.participants,
            form_data=form_data_dict,
            created_by=current_user.id,
            status="published"
        )
        
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        
        return {
            "form_id": new_form.form_id,
            "message": "考评表生成成功",
            "preview_data": form_data_dict
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成考评表失败: {str(e)}"
        )


@app.get("/api/evaluation-forms", response_model=List[EvaluationFormResponse])
async def get_evaluation_forms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取所有考评表列表
    """
    forms = db.query(EvaluationForm).order_by(EvaluationForm.created_at.desc()).all()
    return forms


@app.get("/api/evaluation-forms/{form_id}", response_model=EvaluationFormResponse)
async def get_evaluation_form(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单个考评表详情
    """
    form = db.query(EvaluationForm).filter(EvaluationForm.form_id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考评表不存在"
        )
    return form


@app.post("/api/materials/distribute", response_model=dict, status_code=status.HTTP_201_CREATED)
async def distribute_materials(
    distribute_data: MaterialDistributeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分发材料给教师
    
    - 接收材料ID列表、材料类型、分发类型、目标教师列表
    - 验证材料存在性和教师ID有效性
    - 创建分发记录
    - 调用教师端API同步分发信息（TODO）
    """
    try:
        # 验证材料数量和类型数量匹配
        if len(distribute_data.material_ids) != len(distribute_data.material_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="材料ID和材料类型数量不匹配"
            )
        
        # 获取目标教师列表
        target_teachers = []
        if distribute_data.distribution_type == "batch":
            # 批量分发：获取所有教师
            teachers = db.query(Teacher).all()
            target_teachers = [
                {"teacher_id": t.teacher_id, "teacher_name": t.teacher_name}
                for t in teachers
            ]
        else:
            # 定向分发：获取指定教师
            for teacher_id in distribute_data.target_teachers:
                teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
                if teacher:
                    target_teachers.append({
                        "teacher_id": teacher.teacher_id,
                        "teacher_name": teacher.teacher_name
                    })
        
        if not target_teachers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未找到目标教师"
            )
        
        # 为每个材料创建分发记录
        distribution_records = []
        for material_id, material_type in zip(distribute_data.material_ids, distribute_data.material_types):
            # 获取材料名称
            material_name = ""
            if material_type == "evaluation_form":
                form = db.query(EvaluationForm).filter(EvaluationForm.form_id == material_id).first()
                if not form:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"考评表 {material_id} 不存在"
                    )
                material_name = form.name
            else:
                # 文件类型，从文件名获取
                material_name = material_id  # 简化处理，实际应从文件系统获取
            
            # 创建分发记录
            distribution = DistributionRecord(
                material_id=material_id,
                material_type=material_type,
                material_name=material_name,
                distribution_type=distribute_data.distribution_type,
                target_teachers=target_teachers,
                distributed_by=current_user.id,
                status="completed"
            )
            
            db.add(distribution)
            distribution_records.append(distribution)
        
        db.commit()
        
        print(f"开始同步分发信息，材料数量: {len(distribute_data.material_ids)}, 教师数量: {len(target_teachers)}")
        
        # 同步到教师端
        for material_id, material_type in zip(distribute_data.material_ids, distribute_data.material_types):
            # 获取材料名称
            material_name = ""
            if material_type == "evaluation_form":
                form = db.query(EvaluationForm).filter(EvaluationForm.form_id == material_id).first()
                if form:
                    material_name = form.name
            else:
                material_name = material_id
            
            print(f"准备同步材料: {material_name} ({material_id})")
            
            # 为每个教师同步
            for teacher in target_teachers:
                print(f"调用sync_distribution_to_teacher for {teacher['teacher_id']}")
                await sync_distribution_to_teacher(
                    material_id=material_id,
                    material_name=material_name,
                    material_type=material_type,
                    file_url=f"/uploads/{material_id}",
                    teacher_ids=[teacher["teacher_id"]],
                    distributed_at=datetime.now().isoformat()
                )
        
        print("同步完成")
        
        return {
            "distribution_id": distribution_records[0].distribution_id if distribution_records else "",
            "message": "材料分发成功",
            "distributed_count": len(target_teachers)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分发材料失败: {str(e)}"
        )


@app.get("/api/materials/distribution-records", response_model=dict)
async def get_distribution_records(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    teacher_id: Optional[str] = Query(None, description="教师ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    查询分发记录
    
    - 支持日期范围筛选
    - 支持教师ID筛选
    - 返回分发记录列表
    """
    try:
        query = db.query(DistributionRecord)
        
        # 日期范围筛选
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(DistributionRecord.distributed_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            # 包含结束日期的整天
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(DistributionRecord.distributed_at <= end_dt)
        
        # 教师ID筛选
        if teacher_id:
            # 由于target_teachers是JSON字段，需要特殊处理
            # SQLite的JSON查询支持有限，这里先获取所有记录再过滤
            all_records = query.order_by(DistributionRecord.distributed_at.desc()).all()
            filtered_records = [
                record for record in all_records
                if any(t.get("teacher_id") == teacher_id for t in record.target_teachers)
            ]
            records = filtered_records
        else:
            records = query.order_by(DistributionRecord.distributed_at.desc()).all()
        
        # 转换为响应格式
        records_data = []
        for record in records:
            records_data.append({
                "distribution_id": record.distribution_id,
                "material_name": record.material_name,
                "material_type": record.material_type,
                "distributed_to": [t.get("teacher_name") for t in record.target_teachers],
                "distribution_time": record.distributed_at.isoformat(),
                "status": record.status
            })
        
        return {
            "records": records_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询分发记录失败: {str(e)}"
        )


@app.get("/api/materials/submissions", response_model=dict)
async def get_material_submissions(
    status_filter: Optional[str] = Query(None, alias="status", description="审核状态筛选"),
    teacher_id: Optional[str] = Query(None, description="教师ID筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    查询提交材料列表
    
    - 支持审核状态筛选
    - 支持教师ID筛选
    - 返回提交材料列表（按提交时间倒序）
    """
    try:
        query = db.query(MaterialSubmission)
        
        # 审核状态筛选
        if status_filter:
            query = query.filter(MaterialSubmission.review_status == status_filter)
        
        # 教师ID筛选
        if teacher_id:
            query = query.filter(MaterialSubmission.teacher_id == teacher_id)
        
        # 按提交时间倒序排列，最新的在前
        submissions = query.order_by(MaterialSubmission.submitted_at.desc()).all()
        
        print(f"查询提交材料: 总数={len(submissions)}")
        if submissions:
            print(f"最新提交: {submissions[0].submission_id} - {submissions[0].submitted_at}")
        
        # 转换为响应格式
        submissions_data = []
        for submission in submissions:
            submissions_data.append({
                "submission_id": submission.submission_id,
                "teacher_id": submission.teacher_id,
                "teacher_name": submission.teacher_name,
                "files": submission.files,
                "submission_time": submission.submitted_at.isoformat() if submission.submitted_at else "",
                "review_status": submission.review_status
            })
        
        return {
            "submissions": submissions_data,
            "total": len(submissions_data)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询提交材料失败: {str(e)}"
        )


@app.post("/api/materials/submissions/sync", response_model=dict, status_code=status.HTTP_201_CREATED)
async def sync_teacher_submission(
    sync_data: dict,
    db: Session = Depends(get_db)
):
    """
    同步教师端提交的材料
    
    - 接收教师端提交的材料信息
    - 创建材料提交记录
    """
    try:
        # 创建提交记录
        submission = MaterialSubmission(
            submission_id=sync_data.get("submission_id"),
            teacher_id=sync_data.get("teacher_id"),
            teacher_name=sync_data.get("teacher_name"),
            files=sync_data.get("files", []),
            notes=sync_data.get("notes"),
            submitted_at=datetime.fromisoformat(sync_data.get("submitted_at")),
            review_status=sync_data.get("review_status", "pending")
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        return {
            "message": "材料提交同步成功",
            "submission_id": submission.submission_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步材料提交失败: {str(e)}"
        )


@app.post("/api/materials/submissions/{submission_id}/review", response_model=dict)
async def update_review_status(
    submission_id: str,
    review_data: ReviewStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新审核状态
    
    - 接收审核状态和反馈
    - 更新提交记录
    - 调用教师端API同步审核状态（TODO）
    """
    try:
        # 查找提交记录
        submission = db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提交记录不存在"
            )
        
        # 更新审核状态
        submission.review_status = review_data.status
        submission.review_feedback = review_data.feedback
        submission.reviewed_by = current_user.id
        submission.reviewed_at = datetime.utcnow()
        
        db.commit()
        
        # 同步审核状态到教师端
        await sync_review_status_to_teacher(
            submission_id=submission_id,
            status=review_data.status,
            feedback=review_data.feedback or "",
            reviewed_at=submission.reviewed_at.isoformat()
        )
        
        return {
            "message": "审核状态更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新审核状态失败: {str(e)}"
        )


@app.get("/api/materials/download/{file_id}")
async def download_material(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    下载材料文件
    
    - 验证文件存在性
    - 返回文件流
    """
    try:
        # 构建文件路径
        upload_dir = "uploads"
        file_path = os.path.join(upload_dir, file_id)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


# ==================== 教师端同步接口 ====================

from pydantic import BaseModel as PydanticBaseModel

class SubmissionSyncRequest(PydanticBaseModel):
    """教师端提交同步请求"""
    submission_id: str
    teacher_id: str
    teacher_name: str
    files: List[dict]
    notes: Optional[str] = None
    submitted_at: str


@app.post("/api/teacher/sync-submission", response_model=dict)
async def sync_teacher_submission(
    data: SubmissionSyncRequest,
    db: Session = Depends(get_db)
):
    """
    接收教师端的材料提交信息
    """
    try:
        print(f"接收教师提交: {data.submission_id}")
        print(f"提交时间字符串: {data.submitted_at}")
        print(f"提交时间类型: {type(data.submitted_at)}")
        
        # 检查是否已存在
        existing = db.query(MaterialSubmission).filter(
            MaterialSubmission.submission_id == data.submission_id
        ).first()
        
        if existing:
            print(f"提交记录已存在: {data.submission_id}")
            return {"message": "提交记录已存在"}
        
        # 解析提交时间 - 支持多种格式
        submitted_at = None
        try:
            # 尝试标准ISO格式
            submitted_at = datetime.fromisoformat(data.submitted_at.replace('Z', '+00:00'))
            print(f"使用ISO格式解析成功: {submitted_at}")
        except Exception as e1:
            print(f"ISO格式解析失败: {e1}")
            try:
                # 尝试去掉微秒的格式
                if '.' in data.submitted_at:
                    base_time = data.submitted_at.split('.')[0]
                    submitted_at = datetime.fromisoformat(base_time)
                    print(f"使用简化格式解析成功: {submitted_at}")
                else:
                    submitted_at = datetime.fromisoformat(data.submitted_at)
                    print(f"使用基础格式解析成功: {submitted_at}")
            except Exception as e2:
                print(f"简化格式解析失败: {e2}")
                # 如果都失败，使用当前时间
                submitted_at = datetime.utcnow()
                print(f"所有格式都失败，使用当前时间: {submitted_at}")
        
        # 检查时间戳是否合理（如果时间戳太早，使用当前时间）
        # 这是为了处理时区问题：教师端可能发送UTC时间，但管理端使用本地时间
        now = datetime.now()
        if submitted_at and (now - submitted_at).total_seconds() > 3600:  # 如果超过1小时
            print(f"时间戳异常（早于当前时间超过1小时），使用当前时间")
            submitted_at = now
        
        print(f"最终提交时间: {submitted_at}")
        
        # 创建提交记录
        submission = MaterialSubmission(
            submission_id=data.submission_id,
            teacher_id=data.teacher_id,
            teacher_name=data.teacher_name,
            files=data.files,
            notes=data.notes,
            submitted_at=submitted_at,
            review_status="pending"
        )
        
        print(f"创建提交记录: {data.submission_id}, 时间: {submission.submitted_at}")
        
        db.add(submission)
        db.commit()
        
        print(f"提交记录已保存: {data.submission_id}")
        
        return {"message": "同步成功"}
        
    except Exception as e:
        db.rollback()
        print(f"同步失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )

@app.get("/api/evaluation-templates/{template_id}/download")
async def download_evaluation_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    下载考评表模板文件
    """
    try:
        # 查找模板
        template = db.query(EvaluationTemplate).filter(
            EvaluationTemplate.template_id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评表模板不存在"
            )
        
        # 检查文件是否存在
        if not os.path.exists(template.file_url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板文件不存在"
            )
        
        # 返回文件
        return FileResponse(
            path=template.file_url,
            filename=template.file_name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


# ==================== 考评表相关接口 ====================

@app.post("/api/evaluation-templates/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_evaluation_template(
    file: UploadFile = File(...),
    name: str = Query(..., description="考评表名称"),
    description: str = Query("", description="考评表描述"),
    scoring_criteria: str = Query(..., description="评分标准JSON"),
    total_score: int = Query(100, description="总分"),
    submission_requirements: str = Query(..., description="提交要求JSON"),
    deadline_days: int = Query(7, description="截止天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传考评表
    
    - 支持 PDF、Excel、Word 格式
    - 设置评分标准和提交要求
    - 创建考评表模板
    """
    try:
        # 验证文件类型
        allowed_types = ['pdf', 'xlsx', 'xls', 'docx', 'doc']
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型。允许的类型: {', '.join(allowed_types)}"
            )
        
        # 验证文件大小（100MB限制）
        max_size = 100 * 1024 * 1024
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过限制（最大100MB）"
            )
        
        # 生成文件ID
        file_id = f"tpl_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # 创建上传目录
        upload_dir = "uploads/evaluation_templates"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 解析JSON参数
        import json
        scoring_criteria_list = json.loads(scoring_criteria)
        submission_reqs = json.loads(submission_requirements)
        
        # 计算截止时间
        deadline = datetime.now() + timedelta(days=deadline_days)
        
        # 创建考评表模板
        template = EvaluationTemplate(
            name=name,
            description=description,
            file_url=file_path,
            file_name=file.filename,
            file_type=file_ext,
            file_size=file_size,
            scoring_criteria=scoring_criteria_list,
            total_score=total_score,
            submission_requirements=submission_reqs,
            deadline=deadline,
            target_teachers=[],  # 稍后分配
            created_by=current_user.id,
            status="draft"
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "message": "考评表上传成功",
            "template_id": template.template_id,
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传考评表失败: {str(e)}"
        )


@app.post("/api/evaluation-templates/{template_id}/distribute", response_model=dict, status_code=status.HTTP_201_CREATED)
async def distribute_evaluation_template(
    template_id: str,
    distribution_type: str = Query("targeted", description="分发类型: batch 或 targeted"),
    target_teachers: List[str] = Query(None, description="目标教师ID列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分配考评表给教师
    
    - 创建考评任务
    - 同步到教师端
    """
    try:
        # 查找考评表模板
        template = db.query(EvaluationTemplate).filter(
            EvaluationTemplate.template_id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评表模板不存在"
            )
        
        # 获取目标教师
        if distribution_type == "batch":
            teachers = db.query(Teacher).all()
            target_teacher_ids = [t.teacher_id for t in teachers]
        else:
            if not target_teachers:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="指定分配时必须选择至少一个教师"
                )
            target_teacher_ids = target_teachers
        
        # 为每个教师创建考评任务
        created_tasks = []
        for teacher_id in target_teacher_ids:
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                continue
            
            # 生成任务ID：template_id_teacher_id
            task_id = f"{template_id}_{teacher_id}"
            
            task = EvaluationAssignmentTask(
                task_id=task_id,
                template_id=template_id,
                teacher_id=teacher_id,
                teacher_name=teacher.teacher_name,
                deadline=template.deadline,
                status="pending"
            )
            
            db.add(task)
            created_tasks.append(task)
        
        db.commit()
        
        # 更新模板状态
        template.status = "published"
        template.target_teachers = [
            {"teacher_id": t.teacher_id, "teacher_name": t.teacher_name}
            for t in db.query(Teacher).filter(Teacher.teacher_id.in_(target_teacher_ids)).all()
        ]
        db.commit()
        
        # 同步到教师端
        await sync_evaluation_tasks_to_teacher(template, target_teacher_ids)
        
        return {
            "message": "考评表分配成功",
            "distributed_count": len(created_tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分配考评表失败: {str(e)}"
        )


@app.get("/api/evaluation-templates", response_model=dict)
async def get_evaluation_templates(
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取考评表列表
    """
    try:
        query = db.query(EvaluationTemplate)
        
        if status_filter:
            query = query.filter(EvaluationTemplate.status == status_filter)
        
        templates = query.order_by(EvaluationTemplate.created_at.desc()).all()
        
        templates_data = []
        for template in templates:
            templates_data.append({
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "file_name": template.file_name,
                "file_type": template.file_type,
                "total_score": template.total_score,
                "deadline": template.deadline.isoformat(),
                "status": template.status,
                "target_count": len(template.target_teachers),
                "created_at": template.created_at.isoformat()
            })
        
        return {
            "templates": templates_data,
            "total": len(templates_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取考评表列表失败: {str(e)}"
        )


@app.get("/api/evaluation-tasks", response_model=dict)
async def get_evaluation_tasks(
    template_id: Optional[str] = Query(None, description="考评表ID筛选"),
    teacher_id: Optional[str] = Query(None, description="教师ID筛选"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取考评任务列表
    
    - 支持按考评表、教师、状态筛选
    """
    try:
        query = db.query(EvaluationAssignmentTask)
        
        if template_id:
            query = query.filter(EvaluationAssignmentTask.template_id == template_id)
        
        if teacher_id:
            query = query.filter(EvaluationAssignmentTask.teacher_id == teacher_id)
        
        if status_filter:
            query = query.filter(EvaluationAssignmentTask.status == status_filter)
        
        tasks = query.order_by(EvaluationAssignmentTask.created_at.desc()).all()
        
        tasks_data = []
        for task in tasks:
            template = db.query(EvaluationTemplate).filter(
                EvaluationTemplate.template_id == task.template_id
            ).first()
            
            tasks_data.append({
                "task_id": task.task_id,
                "template_id": task.template_id,
                "template_name": template.name if template else "",
                "teacher_id": task.teacher_id,
                "teacher_name": task.teacher_name,
                "status": task.status,  # 使用实际的任务状态
                "display_status": "viewed" if (task.is_viewed and task.status == "pending") else task.status,  # 显示状态
                "is_viewed": task.is_viewed,
                "viewed_at": task.viewed_at.isoformat() if task.viewed_at else None,
                "submitted_files": task.submitted_files,
                "submitted_at": task.submitted_at.isoformat() if task.submitted_at else None,
                "submission_notes": task.submission_notes,
                "scoring_criteria": template.scoring_criteria if template else [],
                "total_score": template.total_score if template else 0,
                "scores": task.scores,
                "score": task.total_score,
                "scoring_feedback": task.scoring_feedback,
                "scored_at": task.scored_at.isoformat() if task.scored_at else None,
                "deadline": task.deadline.isoformat(),
                "created_at": task.created_at.isoformat()
            })
        
        return {
            "tasks": tasks_data,
            "total": len(tasks_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取考评任务列表失败: {str(e)}"
        )


@app.post("/api/evaluation-tasks/{task_id}/score", response_model=dict)
async def score_evaluation_task(
    task_id: str,
    scores: str = Query(..., description="评分结果JSON字符串"),
    feedback: str = Query("", description="评分反馈"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    对考评任务进行评分
    
    - 保存评分结果
    - 记录修改历史
    """
    try:
        # 查找考评任务
        task = db.query(EvaluationAssignmentTask).filter(
            EvaluationAssignmentTask.task_id == task_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 查找考评表模板获取评分标准
        template = db.query(EvaluationTemplate).filter(
            EvaluationTemplate.template_id == task.template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评表模板不存在"
            )
        
        # 计算总分
        scores_dict = json.loads(scores) if isinstance(scores, str) else scores
        total_score = sum(scores_dict.values())
        
        # 记录修改历史
        score_history = task.score_history or []
        if task.total_score is not None:
            score_history.append({
                "old_score": task.total_score,
                "new_score": total_score,
                "reason": feedback,
                "changed_at": datetime.now().isoformat(),
                "changed_by": current_user.username
            })
        
        # 更新任务
        task.scores = scores_dict
        task.total_score = total_score
        task.scoring_feedback = feedback
        task.scored_by = current_user.id
        task.scored_at = datetime.now()
        task.score_history = score_history
        task.status = "scored"
        
        db.commit()
        
        # 同步评分结果到教师端
        await sync_evaluation_score_to_teacher(task)
        
        return {
            "message": "评分成功",
            "task_id": task_id,
            "total_score": total_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评分失败: {str(e)}"
        )


# 同步函数
async def sync_evaluation_tasks_to_teacher(template: EvaluationTemplate, teacher_ids: List[str]):
    """同步考评任务到教师端"""
    import httpx
    import json
    
    TEACHER_API_BASE = os.getenv("TEACHER_API_URL", "http://localhost:8000")
    
    for teacher_id in teacher_ids:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{TEACHER_API_BASE}/api/admin/sync-evaluation-task",
                    json={
                        "task_id": f"{template.template_id}_{teacher_id}",
                        "template_id": template.template_id,
                        "teacher_id": teacher_id,
                        "template_name": template.name,
                        "template_file_url": template.file_url,
                        "template_file_type": template.file_type,
                        "submission_requirements": template.submission_requirements,
                        "scoring_criteria": template.scoring_criteria,
                        "total_score": template.total_score,
                        "deadline": template.deadline.isoformat()
                    },
                    timeout=30.0
                )
                print(f"同步考评任务到教师 {teacher_id} 响应: {response.status_code}")
                if response.status_code not in [200, 201]:
                    print(f"同步失败: {response.text}")
        except Exception as e:
            print(f"同步考评任务到教师 {teacher_id} 异常: {str(e)}")
            import traceback
            traceback.print_exc()


async def sync_evaluation_score_to_teacher(task: EvaluationAssignmentTask):
    """同步评分结果到教师端"""
    import httpx
    
    TEACHER_API_BASE = os.getenv("TEACHER_API_URL", "http://localhost:8000")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{TEACHER_API_BASE}/api/admin/sync-evaluation-score",
                json={
                    "task_id": task.task_id,
                    "template_id": task.template_id,
                    "teacher_id": task.teacher_id,
                    "scores": task.scores,
                    "total_score": task.total_score,
                    "scoring_feedback": task.scoring_feedback,
                    "scored_at": task.scored_at.isoformat() if task.scored_at else None
                },
                timeout=30.0
            )
            print(f"同步评分结果到教师 {task.teacher_id} 响应: {response.status_code}")
            if response.status_code not in [200, 201]:
                print(f"同步失败: {response.text}")
    except Exception as e:
        print(f"同步评分结果到教师 {task.teacher_id} 异常: {str(e)}")
        import traceback
        traceback.print_exc()


@app.post("/api/evaluation-tasks/sync-submission", response_model=dict)
async def sync_evaluation_submission(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    接收教师端的考评提交信息
    """
    try:
        task_id = data.get("task_id")
        template_id = data.get("template_id")
        teacher_id = data.get("teacher_id")
        teacher_name = data.get("teacher_name")
        files = data.get("files", [])
        notes = data.get("notes")
        submitted_at = data.get("submitted_at")
        
        print(f"接收考评提交: {task_id}")
        
        # 查找考评任务
        task = db.query(EvaluationAssignmentTask).filter(
            EvaluationAssignmentTask.task_id == task_id
        ).first()
        
        if not task:
            print(f"考评任务不存在: {task_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 解析提交时间
        try:
            submitted_at_dt = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
        except:
            submitted_at_dt = datetime.now()
        
        # 更新任务
        task.submitted_files = files
        task.submitted_at = submitted_at_dt
        task.submission_notes = notes
        task.status = "submitted"
        task.updated_at = datetime.now()
        
        db.commit()
        
        print(f"考评提交已保存: {task_id}")
        
        return {"message": "同步成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"同步失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )


@app.post("/api/evaluation-tasks/sync-viewed", response_model=dict)
async def sync_evaluation_task_viewed(
    task_id: str = Query(..., description="任务ID"),
    viewed_at: str = Query(..., description="查收时间"),
    db: Session = Depends(get_db)
):
    """
    接收教师端的考评任务查收状态同步
    """
    try:
        # 查找考评任务
        task = db.query(EvaluationAssignmentTask).filter(
            EvaluationAssignmentTask.task_id == task_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评任务不存在"
            )
        
        # 解析查收时间
        try:
            viewed_time = datetime.fromisoformat(viewed_at.replace('Z', '+00:00'))
        except Exception:
            try:
                if '.' in viewed_at:
                    base_time = viewed_at.split('.')[0]
                    viewed_time = datetime.fromisoformat(base_time)
                else:
                    viewed_time = datetime.fromisoformat(viewed_at)
            except Exception:
                viewed_time = datetime.now()
        
        # 更新查收状态
        task.is_viewed = True
        task.viewed_at = viewed_time
        db.commit()
        
        print(f"考评任务查收状态已同步: {task_id}")
        return {"message": "查收状态同步成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"同步失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步失败: {str(e)}"
        )

@app.get("/api/evaluation-templates/{template_id}/download")
async def download_evaluation_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    下载考评表模板文件
    """
    try:
        # 查找模板
        template = db.query(EvaluationTemplate).filter(
            EvaluationTemplate.template_id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考评表模板不存在"
            )
        
        # 检查文件是否存在
        if not os.path.exists(template.file_url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板文件不存在"
            )
        
        # 返回文件
        return FileResponse(
            path=template.file_url,
            filename=template.file_name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)