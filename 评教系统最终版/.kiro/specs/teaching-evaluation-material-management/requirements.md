# Requirements Document

## Introduction

本文档定义了评教系统的材料分发与回收功能需求。该系统实现管理端向教师端分发评教材料（包括文件和考评表），以及教师端提交评教材料并由管理端回收审核的完整流程。系统采用双端架构，管理端和教师端均使用 Vue 3 + TypeScript + Element Plus 构建，后端使用 Python FastAPI，数据库使用 SQLite/MySQL。

## Glossary

- **Management_System**: 管理端系统，负责材料分发、考评表生成、材料回收和审核
- **Teacher_System**: 教师端系统，负责接收材料、查看材料和提交评教材料
- **Evaluation_Material**: 评教材料，包括分发的文件、考评表以及教师提交的评分表和反馈文档
- **Distribution_Record**: 分发记录，记录材料分发的时间、对象和内容
- **Evaluation_Form**: 考评表，由管理端生成的评教表格
- **Submission_Status**: 提交状态，包括"未提交"、"已提交"、"已审核"、"待修改"等
- **Material_Repository**: 材料仓库，存储已上传的分发材料
- **Collection_Entry**: 回收入口，管理端查看和管理教师提交材料的界面

## Requirements

### Requirement 1: 考评表生成功能

**User Story:** 作为管理员，我希望能够生成考评表，以便将其分发给教师进行评教。

#### Acceptance Criteria

1. WHEN 管理员访问"生成考评表"页面 THEN THE Management_System SHALL 显示考评表生成界面
2. WHEN 管理员填写考评表配置信息（如标题、评分项、评分标准）并点击生成 THEN THE Management_System SHALL 创建考评表并存储到系统中
3. WHEN 考评表生成成功 THEN THE Management_System SHALL 显示成功提示并将考评表添加到可分发列表
4. IF 考评表配置信息不完整或无效 THEN THE Management_System SHALL 显示错误提示并阻止生成

### Requirement 2: 材料分发功能

**User Story:** 作为管理员，我希望能够将文件和考评表分发给教师，以便教师能够查看和填写评教材料。

#### Acceptance Criteria

1. WHEN 管理员访问系统设置页面的材料分发功能 THEN THE Management_System SHALL 显示"分发材料"页面已上传的文件列表和"生成考评表"页面生成的考评表列表
2. WHEN 管理员选择要分发的材料（文件或考评表）并选择分发方式（批量或定向） THEN THE Management_System SHALL 显示教师账号选择界面
3. WHEN 管理员选择目标教师账号并确认分发 THEN THE Management_System SHALL 将选定的材料分发给指定教师并创建分发记录
4. WHEN 材料分发成功 THEN THE Management_System SHALL 显示成功提示并更新分发记录列表
5. WHEN 管理员选择批量分发 THEN THE Management_System SHALL 将材料分发给所有教师账号
6. WHEN 管理员选择定向分发 THEN THE Management_System SHALL 仅将材料分发给选定的教师账号

### Requirement 3: 分发记录查看功能

**User Story:** 作为管理员，我希望能够查看材料分发记录，以便追踪材料的分发情况。

#### Acceptance Criteria

1. WHEN 管理员访问分发记录页面 THEN THE Management_System SHALL 显示所有分发记录，包括分发时间、分发对象、分发内容和分发状态
2. WHEN 管理员筛选或搜索分发记录 THEN THE Management_System SHALL 显示符合条件的分发记录
3. WHEN 分发记录列表为空 THEN THE Management_System SHALL 显示"暂无分发记录"提示

### Requirement 4: 材料回收功能

**User Story:** 作为管理员，我希望能够查看和管理教师提交的评教材料，以便进行审核和处理。

#### Acceptance Criteria

1. WHEN 管理员访问评教材料回收入口 THEN THE Management_System SHALL 显示所有教师提交的评教材料列表，包括提交教师、提交时间、材料类型和审核状态
2. WHEN 管理员选择某个提交的材料并点击下载 THEN THE Management_System SHALL 下载该材料到本地
3. WHEN 管理员选择某个提交的材料并标记审核状态（如"已审核"、"待修改"） THEN THE Management_System SHALL 更新该材料的审核状态并同步到教师端
4. WHEN 教师提交新材料 THEN THE Management_System SHALL 实时更新回收列表并显示新提交的材料
5. WHEN 回收列表为空 THEN THE Management_System SHALL 显示"暂无提交材料"提示

### Requirement 5: 教师端材料查看功能

**User Story:** 作为教师，我希望能够查看管理端分发的材料，以便了解评教要求和填写评教表。

#### Acceptance Criteria

1. WHEN 教师登录后访问材料查看页面 THEN THE Teacher_System SHALL 显示管理端分发给该教师的所有文件和考评表
2. WHEN 教师选择某个材料并点击在线查看 THEN THE Teacher_System SHALL 在浏览器中显示该材料内容
3. WHEN 教师选择某个材料并点击下载 THEN THE Teacher_System SHALL 下载该材料到本地
4. WHEN 教师未收到任何分发材料 THEN THE Teacher_System SHALL 显示"暂无分发材料"提示
5. WHEN 管理端分发新材料 THEN THE Teacher_System SHALL 实时更新材料列表并显示新分发的材料

### Requirement 6: 教师端材料提交功能

**User Story:** 作为教师，我希望能够上传并提交评教材料，以便完成评教任务。

#### Acceptance Criteria

1. WHEN 教师访问评教材料提交页面 THEN THE Teacher_System SHALL 显示材料上传界面
2. WHEN 教师选择文件（评分表、反馈文档等）并点击上传 THEN THE Teacher_System SHALL 上传文件到服务器并显示上传进度
3. WHEN 文件上传成功 THEN THE Teacher_System SHALL 显示已上传文件列表并允许教师继续上传或提交
4. WHEN 教师点击提交按钮 THEN THE Teacher_System SHALL 将所有已上传文件提交到管理端并更新提交状态
5. WHEN 材料提交成功 THEN THE Teacher_System SHALL 显示成功提示并将提交状态同步到管理端
6. IF 教师未上传任何文件就点击提交 THEN THE Teacher_System SHALL 显示错误提示并阻止提交
7. WHEN 教师查看已提交材料的审核状态 THEN THE Teacher_System SHALL 显示管理端标记的审核状态（如"已审核"、"待修改"）

### Requirement 7: 数据持久化和同步

**User Story:** 作为系统，我需要确保所有数据正确存储并在管理端和教师端之间实时同步，以便保证数据一致性。

#### Acceptance Criteria

1. WHEN 管理端创建考评表或分发材料 THEN THE Management_System SHALL 将数据持久化到数据库
2. WHEN 教师端提交材料 THEN THE Teacher_System SHALL 将数据持久化到数据库并实时同步到管理端
3. WHEN 管理端更新审核状态 THEN THE Management_System SHALL 将更新持久化到数据库并实时同步到教师端
4. WHEN 任何数据库操作失败 THEN THE System SHALL 返回错误信息并保持数据一致性
5. WHEN 用户刷新页面或重新登录 THEN THE System SHALL 从数据库加载最新数据并显示

### Requirement 8: 文件类型和大小限制

**User Story:** 作为系统，我需要限制上传文件的类型和大小，以便保证系统安全和性能。

#### Acceptance Criteria

1. WHEN 用户上传文件 THEN THE System SHALL 验证文件类型是否为允许的类型（如 PDF、Word、Excel、图片等）
2. WHEN 用户上传文件 THEN THE System SHALL 验证文件大小是否在允许的范围内（如不超过 50MB）
3. IF 文件类型不被允许 THEN THE System SHALL 拒绝上传并显示"不支持的文件类型"错误提示
4. IF 文件大小超过限制 THEN THE System SHALL 拒绝上传并显示"文件大小超过限制"错误提示

### Requirement 9: 用户权限和访问控制

**User Story:** 作为系统，我需要确保用户只能访问其权限范围内的功能和数据，以便保证系统安全。

#### Acceptance Criteria

1. WHEN 用户访问系统功能 THEN THE System SHALL 验证用户身份和权限
2. WHEN 管理员访问管理端功能 THEN THE System SHALL 允许访问材料分发、考评表生成、材料回收等管理功能
3. WHEN 教师访问教师端功能 THEN THE System SHALL 仅允许访问材料查看和材料提交功能
4. IF 用户尝试访问无权限的功能 THEN THE System SHALL 拒绝访问并返回"无权限"错误
5. WHEN 教师查看分发材料 THEN THE System SHALL 仅显示分发给该教师的材料，不显示其他教师的材料
6. WHEN 管理员查看回收材料 THEN THE System SHALL 显示所有教师提交的材料

### Requirement 10: 用户界面和交互体验

**User Story:** 作为用户，我希望系统界面友好且操作流畅，以便高效完成任务。

#### Acceptance Criteria

1. WHEN 用户执行操作（如上传、分发、提交） THEN THE System SHALL 显示加载状态或进度指示
2. WHEN 操作成功或失败 THEN THE System SHALL 显示清晰的成功或错误提示信息
3. WHEN 用户在表单中输入数据 THEN THE System SHALL 提供实时验证和错误提示
4. WHEN 用户查看列表数据（如分发记录、回收材料） THEN THE System SHALL 提供分页、排序和筛选功能
5. WHEN 系统加载数据 THEN THE System SHALL 在合理时间内（如 3 秒内）完成加载并显示数据
