# Implementation Plan: Teaching Evaluation Material Management System

## Overview

本实现计划将评教系统的材料分发与回收功能分解为离散的编码任务。实现将在现有系统基础上扩展，保持原有功能不变，使用 Python FastAPI（后端）和 Vue 3 + TypeScript（前端）。

实现策略：
1. 先实现后端数据模型和API
2. 再实现前端组件和界面
3. 最后实现跨系统同步和实时通知
4. 每个阶段都包含相应的测试任务

## Tasks

- [-] 1. 管理端后端：数据模型和数据库迁移
  - 在 `评教系统管理端/backend_8fMBP/backend/app/models.py` 中添加新的数据模型
  - 创建 `EvaluationForm`、`DistributionRecord`、`MaterialSubmission` 模型
  - 确保模型包含所有必需字段和关系
  - 运行数据库迁移创建新表
  - _Requirements: 1.2, 2.3, 4.1, 7.1_

- [ ] 1.1 为数据模型编写单元测试
  - 测试模型创建和字段验证
  - 测试模型关系和外键约束
  - _Requirements: 1.2, 2.3, 4.1_

- [ ] 2. 管理端后端：考评表生成API
  - [x] 2.1 实现考评表生成端点 `POST /api/evaluation-forms/generate`
    - 接收考评表配置（名称、日期、维度、参与者）
    - 验证输入数据（日期范围、必填字段）
    - 生成考评表数据并存储到数据库
    - 返回考评表ID和预览数据
    - _Requirements: 1.2, 1.3, 1.4_

  - [ ] 2.2 编写属性测试：考评表创建 round-trip
    - **Property 1: Evaluation Form Creation Round-Trip**
    - **Validates: Requirements 1.2, 1.3**

  - [ ] 2.3 编写属性测试：无效考评表拒绝
    - **Property 2: Invalid Evaluation Form Rejection**
    - **Validates: Requirements 1.4**

- [ ] 3. 管理端后端：材料分发API
  - [x] 3.1 实现材料分发端点 `POST /api/materials/distribute`
    - 接收材料ID列表、材料类型、分发类型、目标教师列表
    - 验证材料存在性和教师ID有效性
    - 创建分发记录
    - 调用教师端API同步分发信息
    - _Requirements: 2.3, 2.4, 2.5, 2.6_

  - [x] 3.2 实现分发记录查询端点 `GET /api/materials/distribution-records`
    - 支持日期范围筛选
    - 支持教师ID筛选
    - 返回分发记录列表
    - _Requirements: 3.1, 3.2_

  - [ ] 3.3 编写属性测试：材料分发 round-trip
    - **Property 3: Material Distribution Round-Trip**
    - **Validates: Requirements 2.3, 2.4**

  - [ ] 3.4 编写属性测试：批量分发完整性
    - **Property 4: Batch Distribution Completeness**
    - **Validates: Requirements 2.5**

  - [ ] 3.5 编写属性测试：定向分发排他性
    - **Property 5: Targeted Distribution Exclusivity**
    - **Validates: Requirements 2.6**

  - [ ] 3.6 编写属性测试：分发记录筛选
    - **Property 6: Distribution Record Filtering**
    - **Validates: Requirements 3.2**

- [ ] 4. 管理端后端：材料回收API
  - [x] 4.1 实现提交材料查询端点 `GET /api/materials/submissions`
    - 支持审核状态筛选
    - 支持教师ID筛选
    - 返回提交材料列表
    - _Requirements: 4.1_

  - [x] 4.2 实现审核状态更新端点 `PUT /api/materials/submissions/{submission_id}/review`
    - 接收审核状态和反馈
    - 更新提交记录
    - 调用教师端API同步审核状态
    - _Requirements: 4.3_

  - [x] 4.3 实现材料下载端点 `GET /api/materials/download/{file_id}`
    - 验证文件存在性
    - 返回文件流
    - _Requirements: 4.2_

  - [ ] 4.4 编写属性测试：提交显示完整性
    - **Property 7: Submission Display Completeness**
    - **Validates: Requirements 4.1**

  - [ ] 4.5 编写属性测试：材料下载完整性
    - **Property 8: Material Download Integrity**
    - **Validates: Requirements 4.2**

  - [ ] 4.6 编写属性测试：审核状态同步 round-trip
    - **Property 9: Review Status Synchronization Round-Trip**
    - **Validates: Requirements 4.3, 7.3**


- [ ] 5. 教师端后端：数据模型和数据库迁移
  - 在 `评教系统教师端/backend/app/models/` 中创建新的数据模型文件
  - 创建 `DistributedMaterial`、`TeacherSubmission` 模型
  - 编写MySQL迁移脚本
  - 运行迁移创建新表
  - _Requirements: 5.1, 6.4, 7.2_

- [ ] 5.1 为数据模型编写单元测试
  - 测试模型创建和字段验证
  - _Requirements: 5.1, 6.4_

- [ ] 6. 教师端后端：材料查看API
  - [x] 6.1 实现分发材料查询端点 `GET /api/teacher/materials`
    - 从数据库查询当前教师的分发材料
    - 验证教师身份（JWT token）
    - 返回材料列表
    - _Requirements: 5.1, 9.5_

  - [x] 6.2 实现材料下载端点 `GET /api/teacher/materials/{material_id}/download`
    - 验证教师权限（只能下载分发给自己的材料）
    - 返回文件流
    - _Requirements: 5.3_

  - [ ] 6.3 编写属性测试：教师材料隔离
    - **Property 11: Teacher Material Isolation**
    - **Validates: Requirements 5.1, 9.5**

  - [ ] 6.4 编写属性测试：材料下载可用性
    - **Property 13: Material Download Availability**
    - **Validates: Requirements 5.3**

- [ ] 7. 教师端后端：材料提交API
  - [x] 7.1 实现文件上传端点 `POST /api/teacher/materials/upload`
    - 接收文件上传（multipart/form-data）
    - 验证文件类型和大小
    - 保存文件到服务器
    - 返回文件ID和元信息
    - _Requirements: 6.2, 8.1, 8.2_

  - [x] 7.2 实现材料提交端点 `POST /api/teacher/materials/submit`
    - 接收文件ID列表和备注
    - 验证文件列表非空
    - 创建提交记录
    - 调用管理端API同步提交信息
    - _Requirements: 6.4, 6.5, 6.6_

  - [x] 7.3 实现提交状态查询端点 `GET /api/teacher/materials/submissions`
    - 查询当前教师的提交记录
    - 返回提交列表和审核状态
    - _Requirements: 6.7_

  - [ ] 7.4 编写属性测试：文件上传 round-trip
    - **Property 15: File Upload Round-Trip**
    - **Validates: Requirements 6.2, 6.3**

  - [ ] 7.5 编写属性测试：材料提交同步 round-trip
    - **Property 16: Material Submission Synchronization Round-Trip**
    - **Validates: Requirements 6.4, 6.5, 7.2**

  - [ ] 7.6 编写属性测试：文件类型验证
    - **Property 20: File Type Validation**
    - **Validates: Requirements 8.1, 8.3**

  - [ ] 7.7 编写属性测试：文件大小验证
    - **Property 21: File Size Validation**
    - **Validates: Requirements 8.2, 8.4**

- [ ] 8. Checkpoint - 后端API测试
  - 确保所有后端API端点正常工作
  - 运行所有单元测试和属性测试
  - 验证跨系统API调用（管理端 ↔ 教师端）
  - 如有问题，请向用户报告

- [ ] 9. 管理端前端：扩展SystemConfig组件
  - [ ] 9.1 修改 `评教系统管理端/frontend_Fn8hD/frontend/src/components/SystemConfig.vue`
    - 在"分发材料"标签页添加分发目标选择功能
    - 添加批量分发和定向分发选项
    - 添加教师选择器（多选）
    - 实现分发API调用
    - _Requirements: 2.1, 2.2, 2.5, 2.6_

  - [ ] 9.2 在"生成考评表"标签页添加保存和分发功能
    - 添加"保存考评表"按钮
    - 添加"分发考评表"按钮
    - 实现考评表生成API调用
    - 实现考评表分发API调用
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 9.3 编写组件单元测试
    - 测试分发目标选择交互
    - 测试考评表生成和分发流程
    - _Requirements: 1.1, 2.1, 2.2_

- [ ] 10. 管理端前端：材料分发管理组件
  - [ ] 10.1 创建 `MaterialDistribution.vue` 组件
    - 显示可分发材料列表（文件 + 考评表）
    - 实现材料选择功能
    - 实现教师选择功能（批量/定向）
    - 实现分发操作
    - 显示分发记录列表
    - 实现分发记录筛选和搜索
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2_

  - [ ] 10.2 添加路由配置
    - 在 `router/index.ts` 中添加材料分发页面路由
    - 配置权限保护（仅管理员可访问）
    - _Requirements: 9.2_

  - [ ] 10.3 编写组件单元测试
    - 测试材料列表显示
    - 测试分发操作交互
    - 测试分发记录筛选
    - _Requirements: 2.1, 3.1, 3.2_

- [ ] 11. 管理端前端：材料回收管理组件
  - [x] 11.1 创建 `MaterialCollection.vue` 组件
    - 显示教师提交的材料列表
    - 实现材料下载功能
    - 实现审核状态标记功能
    - 实现筛选和搜索功能
    - 显示审核状态和反馈
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 11.2 添加路由配置
    - 在 `router/index.ts` 中添加材料回收页面路由
    - 配置权限保护（仅管理员可访问）
    - _Requirements: 9.2_

  - [ ] 11.3 编写组件单元测试
    - 测试提交列表显示
    - 测试下载和审核操作
    - 测试筛选功能
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 12. 教师端前端：材料查看组件
  - [x] 12.1 创建 `MaterialView.vue` 组件
    - 显示分发材料列表
    - 实现在线预览功能（PDF、图片）
    - 实现材料下载功能
    - 显示材料分发时间和状态
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 12.2 添加路由配置
    - 在 `评教系统教师端/frontend/src/router/index.ts` 中添加材料查看页面路由
    - 配置权限保护（需要登录）
    - _Requirements: 9.3_

  - [ ] 12.3 编写组件单元测试
    - 测试材料列表显示
    - 测试预览和下载功能
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 13. 教师端前端：材料提交组件
  - [x] 13.1 创建 `MaterialSubmission.vue` 组件
    - 实现文件上传功能（拖拽 + 选择）
    - 显示已上传文件列表
    - 实现文件删除功能
    - 实现材料提交功能
    - 显示提交状态和审核反馈
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7_

  - [x] 13.2 添加路由配置
    - 在 `router/index.ts` 中添加材料提交页面路由
    - 配置权限保护（需要登录）
    - _Requirements: 9.3_

  - [ ] 13.3 编写组件单元测试
    - 测试文件上传交互
    - 测试提交流程
    - 测试状态显示
    - _Requirements: 6.1, 6.2, 6.4, 6.5_

- [ ] 14. Checkpoint - 前端组件测试
  - 确保所有前端组件正常渲染和交互
  - 运行所有组件单元测试
  - 手动测试用户流程
  - 如有问题，请向用户报告

- [ ] 15. WebSocket实时通知实现
  - [ ] 15.1 管理端：实现WebSocket消息发送
    - 在材料分发后发送 `material_distributed` 消息
    - 在审核状态更新后发送 `review_status_updated` 消息
    - _Requirements: 4.4, 5.5_

  - [ ] 15.2 教师端：实现WebSocket消息发送
    - 在材料提交后发送 `material_submitted` 消息
    - _Requirements: 4.4_

  - [ ] 15.3 管理端前端：实现WebSocket消息接收
    - 监听 `material_submitted` 消息
    - 更新材料回收列表
    - _Requirements: 4.4_

  - [ ] 15.4 教师端前端：实现WebSocket消息接收
    - 监听 `material_distributed` 消息
    - 监听 `review_status_updated` 消息
    - 更新材料列表和提交状态
    - _Requirements: 5.5_

  - [ ] 15.5 编写属性测试：实时提交通知
    - **Property 10: Real-Time Submission Notification**
    - **Validates: Requirements 4.4**

  - [ ] 15.6 编写属性测试：实时分发通知
    - **Property 14: Real-Time Distribution Notification**
    - **Validates: Requirements 5.5**

- [ ] 16. 权限和认证集成
  - [ ] 16.1 管理端：添加权限验证中间件
    - 验证管理员角色
    - 保护所有管理端API端点
    - _Requirements: 9.1, 9.2_

  - [ ] 16.2 教师端：添加权限验证中间件
    - 验证教师身份
    - 保护所有教师端API端点
    - 验证教师只能访问自己的数据
    - _Requirements: 9.1, 9.3, 9.5_

  - [ ] 16.3 编写属性测试：认证要求
    - **Property 22: Authentication Requirement**
    - **Validates: Requirements 9.1**

  - [ ] 16.4 编写属性测试：管理员权限验证
    - **Property 23: Admin Permission Verification**
    - **Validates: Requirements 9.2, 9.4**

  - [ ] 16.5 编写属性测试：教师权限验证
    - **Property 24: Teacher Permission Verification**
    - **Validates: Requirements 9.3, 9.4**

- [ ] 17. 数据持久化和事务管理
  - [ ] 17.1 实现事务包装器
    - 为所有写操作添加事务支持
    - 实现自动回滚机制
    - _Requirements: 7.4_

  - [ ] 17.2 实现数据持久化验证
    - 确保所有数据操作正确保存到数据库
    - 实现页面刷新后数据恢复
    - _Requirements: 7.1, 7.5_

  - [ ] 17.3 编写属性测试：数据持久化 round-trip
    - **Property 18: Data Persistence Round-Trip**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**

  - [ ] 17.4 编写属性测试：数据库事务原子性
    - **Property 19: Database Transaction Atomicity**
    - **Validates: Requirements 7.4**

- [ ] 18. 列表功能实现（分页、排序、筛选）
  - [ ] 18.1 后端：实现通用列表查询工具
    - 支持分页参数（page, page_size）
    - 支持排序参数（sort_by, order）
    - 支持筛选参数（动态字段筛选）
    - _Requirements: 10.4_

  - [ ] 18.2 前端：实现列表组件
    - 添加分页控件
    - 添加排序功能
    - 添加筛选表单
    - _Requirements: 10.4_

  - [ ] 18.3 编写属性测试：列表分页正确性
    - **Property 26: List Pagination Correctness**
    - **Validates: Requirements 10.4**

  - [ ] 18.4 编写属性测试：列表排序正确性
    - **Property 27: List Sorting Correctness**
    - **Validates: Requirements 10.4**

  - [ ] 18.5 编写属性测试：列表筛选正确性
    - **Property 28: List Filtering Correctness**
    - **Validates: Requirements 10.4**

- [ ] 19. 错误处理和用户反馈
  - [ ] 19.1 后端：实现统一错误处理
    - 创建自定义异常类
    - 实现全局异常处理器
    - 返回统一的错误响应格式
    - _Requirements: 1.4, 6.6, 8.3, 8.4_

  - [ ] 19.2 前端：实现错误提示组件
    - 显示API错误信息
    - 显示验证错误
    - 提供重试选项（网络错误）
    - _Requirements: 10.2_

  - [ ] 19.3 编写单元测试：错误处理
    - 测试各种错误场景
    - 验证错误响应格式
    - _Requirements: 1.4, 6.6, 8.3, 8.4_

- [ ] 20. 集成测试和端到端测试
  - [ ] 20.1 编写集成测试：管理端分发 → 教师端接收
    - 测试完整的分发流程
    - 验证数据同步
    - _Requirements: 2.3, 5.1, 7.2_

  - [ ] 20.2 编写集成测试：教师端提交 → 管理端回收
    - 测试完整的提交流程
    - 验证数据同步
    - _Requirements: 4.1, 6.4, 7.2_

  - [ ] 20.3 编写集成测试：管理端审核 → 教师端状态更新
    - 测试完整的审核流程
    - 验证状态同步
    - _Requirements: 4.3, 6.7, 7.3_

- [ ] 21. 最终检查点 - 完整系统测试
  - 运行所有单元测试、属性测试和集成测试
  - 手动测试所有用户流程
  - 验证所有需求已实现
  - 检查代码质量和文档完整性
  - 如有问题，请向用户报告

## Notes

- 所有任务都是必需的，包括单元测试、属性测试和集成测试
- 每个任务都引用了具体的需求编号，便于追溯
- Checkpoint任务用于阶段性验证，确保增量进展
- 属性测试每个至少运行100次迭代
- 所有代码应保持与现有系统的风格一致
- 实现过程中如遇到问题，应及时向用户报告
