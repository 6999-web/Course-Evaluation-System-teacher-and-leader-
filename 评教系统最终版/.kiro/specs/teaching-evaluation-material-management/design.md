# Design Document: Teaching Evaluation Material Management System

## Overview

本设计文档描述了评教系统材料分发与回收功能的技术实现方案。该功能在现有评教系统基础上，新增材料管理能力，实现管理端向教师端分发评教材料（文件和考评表），以及教师端提交材料并由管理端回收审核的完整流程。

系统采用前后端分离架构：
- 前端：Vue 3 + TypeScript + Element Plus
- 后端：Python FastAPI
- 数据库：SQLite（管理端）/ MySQL（教师端）
- 通信：RESTful API + WebSocket（实时同步）

设计遵循以下原则：
1. 在现有系统基础上扩展，保持原有功能不变
2. 复用现有组件和数据模型
3. 保持代码风格和架构一致性
4. 确保数据安全和权限隔离

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      管理端 (Admin)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Frontend (Vue 3 + TypeScript + Element Plus)        │  │
│  │  - SystemConfig.vue (扩展)                           │  │
│  │  - MaterialDistribution.vue (新增)                   │  │
│  │  - MaterialCollection.vue (新增)                     │  │
│  │  - EvaluationFormGenerator.vue (新增)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕ HTTP/WebSocket                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Backend (FastAPI + SQLAlchemy)                      │  │
│  │  - Material Distribution API                         │  │
│  │  - Evaluation Form Generation API                    │  │
│  │  - Material Collection API                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database (SQLite)                                   │  │
│  │  - evaluation_forms                                  │  │
│  │  - distribution_records                              │  │
│  │  - material_submissions                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                      教师端 (Teacher)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Frontend (Vue 3 + TypeScript + Element Plus)        │  │
│  │  - MaterialView.vue (新增)                           │  │
│  │  - MaterialSubmission.vue (新增)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕ HTTP/WebSocket                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Backend (FastAPI)                                   │  │
│  │  - Material Viewing API                              │  │
│  │  - Material Submission API                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database (MySQL)                                    │  │
│  │  - distributed_materials                             │  │
│  │  - teacher_submissions                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```


### Data Flow

#### Material Distribution Flow
```
1. 管理员上传文件 → 存储到 uploads/ 目录
2. 管理员生成考评表 → 存储到 evaluation_forms 表
3. 管理员选择材料和目标教师 → 创建分发记录
4. 系统将分发信息写入 distribution_records 表
5. 系统通过 API 将分发信息同步到教师端数据库
6. 教师端接收 WebSocket 通知，更新材料列表
```

#### Material Submission Flow
```
1. 教师上传文件 → 存储到教师端 uploads/ 目录
2. 教师点击提交 → 创建提交记录
3. 系统将提交信息写入 teacher_submissions 表
4. 系统通过 API 将提交信息同步到管理端数据库
5. 管理端接收 WebSocket 通知，更新回收列表
6. 管理员审核并标记状态 → 状态同步回教师端
```

## Components and Interfaces

### Frontend Components

#### 管理端组件

**1. SystemConfig.vue (扩展现有组件)**
- 功能：在现有三个标签页基础上保持不变
- 扩展：
  - "分发材料"标签页：添加分发目标选择功能
  - "生成考评表"标签页：添加考评表保存和分发功能
- 新增方法：
  - `selectDistributionTargets()`: 选择分发目标（批量/定向）
  - `saveEvaluationForm()`: 保存生成的考评表
  - `distributeEvaluationForm()`: 分发考评表

**2. MaterialDistribution.vue (新增组件)**
- 功能：材料分发管理和分发记录查看
- 主要功能：
  - 显示可分发材料列表（文件 + 考评表）
  - 选择分发目标（批量/定向）
  - 执行分发操作
  - 查看分发记录和状态
- 数据：
  - `availableMaterials`: 可分发材料列表
  - `distributionRecords`: 分发记录列表
  - `selectedTeachers`: 选中的教师列表
- 方法：
  - `loadMaterials()`: 加载可分发材料
  - `selectTeachers()`: 选择目标教师
  - `distributeMaterials()`: 执行分发
  - `viewDistributionHistory()`: 查看分发历史

**3. MaterialCollection.vue (新增组件)**
- 功能：材料回收管理和审核
- 主要功能：
  - 显示教师提交的材料列表
  - 下载提交的材料
  - 标记审核状态
  - 筛选和搜索提交记录
- 数据：
  - `submissions`: 提交材料列表
  - `filterOptions`: 筛选选项
- 方法：
  - `loadSubmissions()`: 加载提交列表
  - `downloadMaterial()`: 下载材料
  - `updateReviewStatus()`: 更新审核状态
  - `filterSubmissions()`: 筛选提交记录


#### 教师端组件

**1. MaterialView.vue (新增组件)**
- 功能：查看管理端分发的材料
- 主要功能：
  - 显示分发材料列表
  - 在线预览材料（PDF、图片）
  - 下载材料到本地
  - 显示材料分发时间和状态
- 数据：
  - `materials`: 分发材料列表
  - `selectedMaterial`: 当前选中的材料
- 方法：
  - `loadMaterials()`: 加载分发材料
  - `previewMaterial()`: 在线预览
  - `downloadMaterial()`: 下载材料

**2. MaterialSubmission.vue (新增组件)**
- 功能：上传和提交评教材料
- 主要功能：
  - 上传评分表、反馈文档等文件
  - 显示已上传文件列表
  - 提交材料到管理端
  - 查看提交状态和审核反馈
- 数据：
  - `uploadedFiles`: 已上传文件列表
  - `submissionStatus`: 提交状态
  - `reviewFeedback`: 审核反馈
- 方法：
  - `uploadFile()`: 上传文件
  - `removeFile()`: 删除文件
  - `submitMaterials()`: 提交材料
  - `checkSubmissionStatus()`: 查看提交状态

### Backend API Endpoints

#### 管理端 API

**考评表生成 API**
```python
POST /api/evaluation-forms/generate
Request:
{
  "name": "2024年度教师教学质量考评",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "dimensions": ["teaching_attitude", "teaching_content", "teaching_method"],
  "participants": ["teacher_id_1", "teacher_id_2"]
}
Response:
{
  "form_id": "form_123",
  "message": "考评表生成成功",
  "preview_data": [...]
}
```

**材料分发 API**
```python
POST /api/materials/distribute
Request:
{
  "material_ids": ["file_1", "form_123"],
  "material_types": ["file", "evaluation_form"],
  "distribution_type": "targeted",  // "batch" or "targeted"
  "target_teachers": ["teacher_id_1", "teacher_id_2"]
}
Response:
{
  "distribution_id": "dist_456",
  "message": "材料分发成功",
  "distributed_count": 2
}
```

**分发记录查询 API**
```python
GET /api/materials/distribution-records
Query Parameters:
  - start_date: 开始日期
  - end_date: 结束日期
  - teacher_id: 教师ID（可选）
Response:
{
  "records": [
    {
      "distribution_id": "dist_456",
      "material_name": "2024年度考评表",
      "material_type": "evaluation_form",
      "distributed_to": ["张三", "李四"],
      "distribution_time": "2024-01-15T10:00:00",
      "status": "completed"
    }
  ]
}
```

**材料回收查询 API**
```python
GET /api/materials/submissions
Query Parameters:
  - status: 审核状态（可选）
  - teacher_id: 教师ID（可选）
Response:
{
  "submissions": [
    {
      "submission_id": "sub_789",
      "teacher_id": "teacher_id_1",
      "teacher_name": "张三",
      "files": [
        {
          "file_id": "file_001",
          "file_name": "评分表.xlsx",
          "file_size": 102400,
          "file_url": "/uploads/submissions/file_001.xlsx"
        }
      ],
      "submission_time": "2024-01-20T14:30:00",
      "review_status": "pending"
    }
  ]
}
```

**审核状态更新 API**
```python
PUT /api/materials/submissions/{submission_id}/review
Request:
{
  "status": "approved",  // "approved", "rejected", "needs_revision"
  "feedback": "材料完整，审核通过"
}
Response:
{
  "message": "审核状态更新成功"
}
```

**材料下载 API**
```python
GET /api/materials/download/{file_id}
Response: File stream
```


#### 教师端 API

**分发材料查询 API**
```python
GET /api/teacher/materials
Headers:
  Authorization: Bearer <token>
Response:
{
  "materials": [
    {
      "material_id": "mat_001",
      "material_name": "2024年度考评表",
      "material_type": "evaluation_form",
      "file_url": "/materials/form_123.xlsx",
      "distributed_time": "2024-01-15T10:00:00",
      "is_viewed": false
    },
    {
      "material_id": "mat_002",
      "material_name": "评教指南.pdf",
      "material_type": "file",
      "file_url": "/materials/guide.pdf",
      "distributed_time": "2024-01-15T10:00:00",
      "is_viewed": true
    }
  ]
}
```

**材料预览/下载 API**
```python
GET /api/teacher/materials/{material_id}/download
Headers:
  Authorization: Bearer <token>
Response: File stream
```

**材料上传 API**
```python
POST /api/teacher/materials/upload
Headers:
  Authorization: Bearer <token>
  Content-Type: multipart/form-data
Request:
  file: <binary>
Response:
{
  "file_id": "file_001",
  "file_name": "评分表.xlsx",
  "file_size": 102400,
  "upload_time": "2024-01-20T14:30:00"
}
```

**材料提交 API**
```python
POST /api/teacher/materials/submit
Headers:
  Authorization: Bearer <token>
Request:
{
  "file_ids": ["file_001", "file_002"],
  "notes": "已完成评教材料填写"
}
Response:
{
  "submission_id": "sub_789",
  "message": "材料提交成功",
  "submission_time": "2024-01-20T14:35:00"
}
```

**提交状态查询 API**
```python
GET /api/teacher/materials/submissions
Headers:
  Authorization: Bearer <token>
Response:
{
  "submissions": [
    {
      "submission_id": "sub_789",
      "files": [
        {
          "file_name": "评分表.xlsx",
          "file_size": 102400
        }
      ],
      "submission_time": "2024-01-20T14:35:00",
      "review_status": "approved",
      "review_feedback": "材料完整，审核通过",
      "review_time": "2024-01-21T09:00:00"
    }
  ]
}
```

## Data Models

### 管理端数据模型

**EvaluationForm (考评表)**
```python
class EvaluationForm(Base):
    __tablename__ = "evaluation_forms"
    
    form_id = Column(String, primary_key=True, default=lambda: f"form_{uuid.uuid4().hex[:8]}")
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    dimensions = Column(JSON, nullable=False)  # ["teaching_attitude", "teaching_content", ...]
    participants = Column(JSON, nullable=False)  # ["teacher_id_1", "teacher_id_2", ...]
    form_data = Column(JSON, nullable=False)  # 考评表数据
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default="draft")  # draft, published, archived
```

**DistributionRecord (分发记录)**
```python
class DistributionRecord(Base):
    __tablename__ = "distribution_records"
    
    distribution_id = Column(String, primary_key=True, default=lambda: f"dist_{uuid.uuid4().hex[:8]}")
    material_id = Column(String, nullable=False)  # 文件ID或考评表ID
    material_type = Column(String(20), nullable=False)  # "file" or "evaluation_form"
    material_name = Column(String(200), nullable=False)
    distribution_type = Column(String(20), nullable=False)  # "batch" or "targeted"
    target_teachers = Column(JSON, nullable=False)  # [{"teacher_id": "xxx", "teacher_name": "xxx"}, ...]
    distributed_by = Column(Integer, ForeignKey("users.id"))
    distributed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="completed")  # pending, completed, failed
```

**MaterialSubmission (材料提交)**
```python
class MaterialSubmission(Base):
    __tablename__ = "material_submissions"
    
    submission_id = Column(String, primary_key=True, default=lambda: f"sub_{uuid.uuid4().hex[:8]}")
    teacher_id = Column(String, nullable=False)
    teacher_name = Column(String(100), nullable=False)
    files = Column(JSON, nullable=False)  # [{"file_id": "xxx", "file_name": "xxx", "file_size": 123, "file_url": "xxx"}, ...]
    notes = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    review_status = Column(String(20), default="pending")  # pending, approved, rejected, needs_revision
    review_feedback = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
```


### 教师端数据模型

**DistributedMaterial (分发材料)**
```python
class DistributedMaterial(Base):
    __tablename__ = "distributed_materials"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String(50), nullable=False, index=True)
    teacher_id = Column(String(50), nullable=False, index=True)
    material_name = Column(String(200), nullable=False)
    material_type = Column(String(20), nullable=False)  # "file" or "evaluation_form"
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer)
    distributed_at = Column(DateTime, nullable=False)
    is_viewed = Column(Boolean, default=False)
    viewed_at = Column(DateTime, nullable=True)
```

**TeacherSubmission (教师提交)**
```python
class TeacherSubmission(Base):
    __tablename__ = "teacher_submissions"
    
    submission_id = Column(String, primary_key=True)
    teacher_id = Column(String(50), nullable=False, index=True)
    files = Column(JSON, nullable=False)
    notes = Column(Text)
    submitted_at = Column(DateTime, nullable=False)
    review_status = Column(String(20), default="pending")
    review_feedback = Column(Text)
    reviewed_at = Column(DateTime, nullable=True)
    synced_to_admin = Column(Boolean, default=False)  # 是否已同步到管理端
```

### Database Schema Diagram

```
管理端数据库 (SQLite):
┌─────────────────────────┐
│ users                   │
│ - id (PK)              │
│ - username             │
│ - email                │
│ - role                 │
└─────────────────────────┘
         ↑
         │
┌─────────────────────────┐
│ evaluation_forms        │
│ - form_id (PK)         │
│ - name                 │
│ - dimensions (JSON)    │
│ - participants (JSON)  │
│ - created_by (FK)      │
└─────────────────────────┘
         ↑
         │
┌─────────────────────────┐
│ distribution_records    │
│ - distribution_id (PK) │
│ - material_id          │
│ - material_type        │
│ - target_teachers (JSON)│
│ - distributed_by (FK)  │
└─────────────────────────┘
         ↑
         │
┌─────────────────────────┐
│ material_submissions    │
│ - submission_id (PK)   │
│ - teacher_id           │
│ - files (JSON)         │
│ - review_status        │
│ - reviewed_by (FK)     │
└─────────────────────────┘

教师端数据库 (MySQL):
┌─────────────────────────┐
│ distributed_materials   │
│ - id (PK)              │
│ - material_id          │
│ - teacher_id           │
│ - material_name        │
│ - file_url             │
└─────────────────────────┘
         ↑
         │
┌─────────────────────────┐
│ teacher_submissions     │
│ - submission_id (PK)   │
│ - teacher_id           │
│ - files (JSON)         │
│ - review_status        │
└─────────────────────────┘
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

经过对需求的分析，我识别出以下需要合并或消除的冗余属性：

**冗余组1：考评表生成和列表更新**
- 属性 1.2（创建考评表并存储）和属性 1.3（添加到可分发列表）可以合并为一个属性：创建考评表后应该能够在可分发列表中查询到。

**冗余组2：分发记录创建和列表更新**
- 属性 2.3（创建分发记录）和属性 2.4（更新分发记录列表）可以合并为一个属性：分发操作后应该能够在分发记录列表中查询到。

**冗余组3：文件上传和列表更新**
- 属性 6.2（上传文件）和属性 6.3（显示已上传文件列表）可以合并为一个属性：上传文件后应该能够在已上传文件列表中查询到。

**冗余组4：数据持久化验证**
- 属性 7.1、7.2、7.3 都是测试数据持久化，可以合并为一个通用的 round-trip 属性：任何数据操作后，重新查询应该能获取到相同的数据。

**冗余组5：文件验证**
- 属性 8.1 和 8.3 可以合并：对于任何文件，如果类型不被允许，则应该被拒绝。
- 属性 8.2 和 8.4 可以合并：对于任何文件，如果大小超过限制，则应该被拒绝。

经过反思，我将保留以下核心属性，每个属性提供独特的验证价值：

### Core Properties

**Property 1: Evaluation Form Creation Round-Trip**
*For any* valid evaluation form configuration (name, dates, dimensions, participants), creating the form and then querying the available materials list should return a material entry containing that form.
**Validates: Requirements 1.2, 1.3**

**Property 2: Invalid Evaluation Form Rejection**
*For any* evaluation form configuration with missing required fields or invalid data (e.g., end_date before start_date, empty dimensions), the system should reject the creation request and return an error.
**Validates: Requirements 1.4**

**Property 3: Material Distribution Round-Trip**
*For any* valid material (file or evaluation form) and any non-empty list of target teachers, distributing the material should create a distribution record that can be queried from the distribution records list.
**Validates: Requirements 2.3, 2.4**

**Property 4: Batch Distribution Completeness**
*For any* material and batch distribution mode, all teachers in the system should receive the material (i.e., the material should appear in each teacher's distributed materials list).
**Validates: Requirements 2.5**

**Property 5: Targeted Distribution Exclusivity**
*For any* material and targeted distribution mode with a selected subset of teachers, only the selected teachers should receive the material, and non-selected teachers should not have access to it.
**Validates: Requirements 2.6**

**Property 6: Distribution Record Filtering**
*For any* filter criteria (date range, teacher ID, material type), all returned distribution records should satisfy the filter criteria.
**Validates: Requirements 3.2**

**Property 7: Submission Display Completeness**
*For any* teacher submission, the submission should appear in the admin's material collection list with all required information (teacher name, submission time, files, review status).
**Validates: Requirements 4.1**

**Property 8: Material Download Integrity**
*For any* submitted material file, downloading the file should return the exact same content that was originally uploaded (file size and content hash should match).
**Validates: Requirements 4.2**

**Property 9: Review Status Synchronization Round-Trip**
*For any* submission and any valid review status update (approved, rejected, needs_revision), updating the status on the admin side should synchronize to the teacher side such that querying the submission status from the teacher side returns the updated status.
**Validates: Requirements 4.3, 7.3**

**Property 10: Real-Time Submission Notification**
*For any* teacher submission, the admin's material collection list should be updated to include the new submission within a reasonable time window (e.g., 5 seconds).
**Validates: Requirements 4.4**

**Property 11: Teacher Material Isolation**
*For any* teacher, querying their distributed materials should return only materials that were explicitly distributed to that teacher, and should not include materials distributed to other teachers.
**Validates: Requirements 5.1, 9.5**

**Property 12: Material Preview Availability**
*For any* distributed material with a previewable file type (PDF, PNG, JPG), the teacher should be able to successfully preview the material content.
**Validates: Requirements 5.2**

**Property 13: Material Download Availability**
*For any* distributed material, the teacher should be able to successfully download the material file.
**Validates: Requirements 5.3**

**Property 14: Real-Time Distribution Notification**
*For any* material distribution to a teacher, the teacher's material list should be updated to include the new material within a reasonable time window (e.g., 5 seconds).
**Validates: Requirements 5.5**

**Property 15: File Upload Round-Trip**
*For any* valid file (within size and type limits), uploading the file should add it to the uploaded files list, and the file should be retrievable with the same content.
**Validates: Requirements 6.2, 6.3**

**Property 16: Material Submission Synchronization Round-Trip**
*For any* non-empty list of uploaded files, submitting the materials should create a submission record on the teacher side that synchronizes to the admin side such that querying submissions from the admin side returns the submission with all file information.
**Validates: Requirements 6.4, 6.5, 7.2**

**Property 17: Submission Status Display**
*For any* teacher submission, querying the submission status from the teacher side should return the current review status and feedback set by the admin.
**Validates: Requirements 6.7**

**Property 18: Data Persistence Round-Trip**
*For any* data operation (create evaluation form, distribute material, submit material, update review status), the data should be persisted such that querying the data after a page refresh or re-login returns the same data.
**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

**Property 19: Database Transaction Atomicity**
*For any* database operation that fails (e.g., due to constraint violation or connection error), the system should roll back the transaction and maintain data consistency (no partial updates).
**Validates: Requirements 7.4**

**Property 20: File Type Validation**
*For any* file with a disallowed file type (not in the allowed list: PDF, DOCX, XLSX, PNG, JPG), the upload should be rejected with an appropriate error message.
**Validates: Requirements 8.1, 8.3**

**Property 21: File Size Validation**
*For any* file with size exceeding the limit (e.g., 50MB), the upload should be rejected with an appropriate error message.
**Validates: Requirements 8.2, 8.4**

**Property 22: Authentication Requirement**
*For any* protected API endpoint (all material management endpoints), requests without valid authentication tokens should be rejected with a 401 Unauthorized error.
**Validates: Requirements 9.1**

**Property 23: Admin Permission Verification**
*For any* admin-only endpoint (material distribution, evaluation form generation, material collection), requests from non-admin users should be rejected with a 403 Forbidden error.
**Validates: Requirements 9.2, 9.4**

**Property 24: Teacher Permission Verification**
*For any* teacher-only endpoint (material viewing, material submission), requests from non-teacher users should be rejected with a 403 Forbidden error.
**Validates: Requirements 9.3, 9.4**

**Property 25: Admin Material Access Completeness**
*For any* admin user, querying the material collection should return submissions from all teachers, not just a subset.
**Validates: Requirements 9.6**

**Property 26: List Pagination Correctness**
*For any* paginated list (distribution records, material submissions) with page size N, each page should contain at most N items, and the union of all pages should equal the complete dataset.
**Validates: Requirements 10.4**

**Property 27: List Sorting Correctness**
*For any* sortable list (distribution records, material submissions) sorted by a field (e.g., submission_time), the returned items should be in the correct order according to the sort criteria.
**Validates: Requirements 10.4**

**Property 28: List Filtering Correctness**
*For any* filterable list (distribution records, material submissions) with filter criteria, all returned items should satisfy the filter criteria, and no items satisfying the criteria should be excluded.
**Validates: Requirements 10.4**


## Error Handling

### Error Categories

**1. Validation Errors (400 Bad Request)**
- 缺少必填字段
- 无效的数据格式（日期、邮箱等）
- 文件类型不支持
- 文件大小超过限制
- 空文件列表提交

**2. Authentication Errors (401 Unauthorized)**
- 缺少认证令牌
- 令牌过期
- 令牌无效

**3. Authorization Errors (403 Forbidden)**
- 用户角色权限不足
- 尝试访问其他用户的数据

**4. Resource Not Found Errors (404 Not Found)**
- 材料ID不存在
- 考评表ID不存在
- 提交记录ID不存在
- 用户ID不存在

**5. Conflict Errors (409 Conflict)**
- 重复分发相同材料给相同教师
- 重复提交相同材料

**6. Server Errors (500 Internal Server Error)**
- 数据库连接失败
- 文件系统错误
- 外部服务调用失败

### Error Response Format

所有错误响应遵循统一格式：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "文件大小超过限制",
    "details": {
      "field": "file",
      "max_size": "50MB",
      "actual_size": "75MB"
    },
    "timestamp": "2024-01-20T10:30:00Z"
  }
}
```

### Error Handling Strategies

**Frontend Error Handling:**
1. 显示用户友好的错误提示
2. 对于网络错误，提供重试选项
3. 对于验证错误，高亮显示错误字段
4. 记录错误日志到控制台（开发环境）

**Backend Error Handling:**
1. 捕获所有异常并返回适当的HTTP状态码
2. 记录详细错误日志（包括堆栈跟踪）
3. 对于数据库错误，回滚事务
4. 对于文件操作错误，清理临时文件
5. 对于外部服务错误，实现重试机制（带指数退避）

### Transaction Management

**数据库事务规则：**
1. 所有写操作必须在事务中执行
2. 事务失败时自动回滚
3. 长事务应该拆分为多个短事务
4. 使用乐观锁处理并发更新

**示例：材料分发事务**
```python
async def distribute_material(material_id: str, teacher_ids: List[str], db: Session):
    try:
        # 开始事务
        # 1. 创建分发记录
        distribution = DistributionRecord(...)
        db.add(distribution)
        
        # 2. 为每个教师创建材料记录
        for teacher_id in teacher_ids:
            material = DistributedMaterial(...)
            db.add(material)
        
        # 3. 提交事务
        db.commit()
        
        # 4. 发送WebSocket通知（事务外）
        await notify_teachers(teacher_ids, material_id)
        
        return distribution
    except Exception as e:
        # 回滚事务
        db.rollback()
        logger.error(f"Distribution failed: {e}")
        raise HTTPException(status_code=500, detail="分发失败")
```

## Testing Strategy

### Dual Testing Approach

本系统采用单元测试和属性测试相结合的策略：

**单元测试（Unit Tests）：**
- 测试具体的示例和边缘情况
- 测试错误处理逻辑
- 测试UI组件的渲染和交互
- 测试API端点的基本功能

**属性测试（Property-Based Tests）：**
- 测试通用的正确性属性
- 使用随机生成的输入进行大量测试
- 验证系统在各种输入下的行为一致性
- 每个属性测试至少运行100次迭代

### Testing Tools

**Frontend Testing:**
- **Framework**: Vitest
- **Component Testing**: Vue Test Utils
- **E2E Testing**: Playwright (可选)
- **Property Testing**: fast-check

**Backend Testing:**
- **Framework**: pytest
- **Property Testing**: Hypothesis
- **API Testing**: httpx (FastAPI TestClient)
- **Database Testing**: SQLite in-memory database

### Test Organization

**Frontend Test Structure:**
```
frontend/src/
├── components/
│   ├── MaterialDistribution.vue
│   └── __tests__/
│       ├── MaterialDistribution.spec.ts  # 单元测试
│       └── MaterialDistribution.property.spec.ts  # 属性测试
├── api/
│   └── __tests__/
│       └── materials.spec.ts
└── utils/
    └── __tests__/
        └── validation.spec.ts
```

**Backend Test Structure:**
```
backend/app/
├── routes/
│   └── materials.py
├── tests/
│   ├── unit/
│   │   ├── test_materials_api.py
│   │   └── test_validation.py
│   └── properties/
│       ├── test_distribution_properties.py
│       └── test_submission_properties.py
```

### Property Test Configuration

每个属性测试必须：
1. 运行至少100次迭代
2. 使用注释标记对应的设计属性
3. 使用合适的数据生成器

**示例：属性测试标记**
```python
# Feature: teaching-evaluation-material-management, Property 1: Evaluation Form Creation Round-Trip
@given(evaluation_form_config())
def test_evaluation_form_creation_roundtrip(form_config):
    # 创建考评表
    response = client.post("/api/evaluation-forms/generate", json=form_config)
    assert response.status_code == 200
    form_id = response.json()["form_id"]
    
    # 查询可分发材料列表
    response = client.get("/api/materials/available")
    materials = response.json()["materials"]
    
    # 验证考评表在列表中
    assert any(m["material_id"] == form_id for m in materials)
```

### Test Coverage Goals

- **Backend API**: 90%+ 代码覆盖率
- **Frontend Components**: 80%+ 代码覆盖率
- **Critical Paths**: 100% 覆盖率（认证、权限、数据同步）

### Integration Testing

**跨系统集成测试：**
1. 管理端分发 → 教师端接收
2. 教师端提交 → 管理端回收
3. 管理端审核 → 教师端状态更新

**WebSocket实时同步测试：**
1. 模拟管理端分发，验证教师端实时收到通知
2. 模拟教师端提交，验证管理端实时收到通知
3. 测试连接断开和重连场景

### Performance Testing

**性能指标：**
- API响应时间 < 500ms (P95)
- 文件上传速度 > 1MB/s
- 页面加载时间 < 2s
- WebSocket消息延迟 < 100ms

**负载测试场景：**
1. 100个并发教师同时查看材料
2. 50个教师同时上传文件
3. 管理员批量分发给1000个教师

### Security Testing

**安全测试项：**
1. SQL注入防护
2. XSS攻击防护
3. CSRF防护
4. 文件上传漏洞（恶意文件、路径遍历）
5. 权限绕过测试
6. 敏感数据泄露测试

## Implementation Notes

### File Storage Strategy

**管理端文件存储：**
- 路径：`backend/app/uploads/`
- 命名规则：`{timestamp}_{uuid}_{original_filename}`
- 子目录：按日期组织 `uploads/2024/01/20/`

**教师端文件存储：**
- 路径：`backend/uploads/submissions/`
- 命名规则：`{teacher_id}_{timestamp}_{uuid}_{original_filename}`
- 子目录：按教师ID组织 `uploads/submissions/{teacher_id}/`

### WebSocket Communication

**消息格式：**
```json
{
  "type": "material_distributed",
  "data": {
    "material_id": "mat_001",
    "material_name": "2024年度考评表",
    "distributed_at": "2024-01-20T10:00:00Z"
  },
  "timestamp": "2024-01-20T10:00:00Z"
}
```

**消息类型：**
- `material_distributed`: 材料已分发
- `material_submitted`: 材料已提交
- `review_status_updated`: 审核状态已更新

### Database Migration Strategy

**管理端迁移：**
1. 创建新表：`evaluation_forms`, `distribution_records`, `material_submissions`
2. 保持现有表不变
3. 使用Alembic管理迁移

**教师端迁移：**
1. 创建新表：`distributed_materials`, `teacher_submissions`
2. 使用MySQL迁移脚本

### Deployment Considerations

**环境变量配置：**
```env
# 管理端
DATABASE_URL=sqlite:///./evaluation_system.db
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=pdf,docx,xlsx,png,jpg,jpeg

# 教师端
DATABASE_URL=mysql://user:pass@localhost/teacher_db
UPLOAD_DIR=./uploads/submissions
ADMIN_API_URL=http://admin-backend:8000
```

**跨域配置：**
- 管理端允许教师端域名
- 教师端允许管理端域名
- 生产环境使用具体域名，避免使用 `*`

### Monitoring and Logging

**日志级别：**
- DEBUG: 详细的调试信息
- INFO: 一般信息（API调用、文件上传）
- WARNING: 警告信息（文件大小接近限制）
- ERROR: 错误信息（API失败、数据库错误）
- CRITICAL: 严重错误（系统崩溃）

**监控指标：**
- API请求数和响应时间
- 文件上传成功率
- WebSocket连接数
- 数据库查询性能
- 磁盘使用率

**日志格式：**
```json
{
  "timestamp": "2024-01-20T10:00:00Z",
  "level": "INFO",
  "service": "admin-backend",
  "endpoint": "/api/materials/distribute",
  "user_id": 123,
  "message": "Material distributed successfully",
  "duration_ms": 245
}
```
