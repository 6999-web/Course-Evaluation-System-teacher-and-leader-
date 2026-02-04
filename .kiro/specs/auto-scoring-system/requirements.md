# Requirements Document

## Introduction

本文档定义了将学校评教系统从纯手动评分模式升级为基于 Deepseek API 的自动评分系统的需求。系统需要实现5类教学文件的自动评分，同时保留人工复核功能，确保评分准确性和可追溯性。

## Glossary

- **System**: 评教系统自动评分模块
- **Scoring_Engine**: 自动评分引擎，负责调用 Deepseek API 并处理评分逻辑
- **Template_Manager**: 提示词模板管理器，管理5类文件的评分标准模板
- **File_Parser**: 文件解析器，提取文档文本内容
- **Review_Module**: 复核模块，处理异议和人工复核
- **Task_Manager**: 考评任务管理器，管理考评任务的创建和分发
- **Veto_Item**: 一票否决项，触发后直接判定为不合格
- **Core_Indicator**: 核心指标，用于评分的主要维度
- **Bonus_Item**: 加分项，额外加分的项目
- **Grade_Level**: 等级，包括优秀、良好、合格、不合格

## Requirements

### Requirement 1: 自动评分引擎实现

**User Story:** 作为系统管理员，我希望系统能够自动对教师提交的教学文件进行评分，以减少人工评分工作量并提高评分效率。

#### Acceptance Criteria

1. WHEN 教师提交教学文件后，THE Scoring_Engine SHALL 自动触发评分流程
2. WHEN 评分流程启动时，THE File_Parser SHALL 提取文件的文本内容
3. WHEN 文本内容提取完成后，THE Scoring_Engine SHALL 根据文件类型选择对应的提示词模板
4. WHEN 提示词模板选择完成后，THE Scoring_Engine SHALL 调用 Deepseek API 进行评分
5. WHEN API 返回评分结果后，THE System SHALL 解析得分、等级、扣分理由并存储
6. WHEN 单个文件评分时，THE System SHALL 在10秒内完成响应
7. WHEN 批量评分100份文件时，THE System SHALL 在10分钟内完成所有评分

### Requirement 2: Deepseek API 集成

**User Story:** 作为开发人员，我需要正确集成 Deepseek API，以确保评分功能的稳定性和准确性。

#### Acceptance Criteria

1. THE System SHALL 使用 API 地址 https://api.deepseek.com/v1/chat/completions
2. THE System SHALL 使用 API 密钥 sk-b6ca926900534f1fa31067d49980ec56 进行认证
3. THE System SHALL 使用模型 deepseek-chat 进行评分
4. THE System SHALL 设置 temperature 参数为 0.1 以降低随机性
5. WHEN API 调用失败时，THE System SHALL 记录错误日志并标记文件为"评分失败"状态
6. WHEN API 返回结果时，THE System SHALL 验证返回格式的完整性
7. WHEN API 响应超时（超过30秒）时，THE System SHALL 重试最多3次

### Requirement 3: 提示词模板管理

**User Story:** 作为系统管理员，我需要管理和配置5类教学文件的评分标准模板，以确保评分规则的准确性和可维护性。

#### Acceptance Criteria

1. THE Template_Manager SHALL 支持5类文件类型：教案、教学反思、教研/听课记录、成绩/学情分析、课件
2. WHEN 创建提示词模板时，THE Template_Manager SHALL 包含等级划分标准（优秀90-100、良好80-89、合格60-79、不合格＜60）
3. WHEN 创建提示词模板时，THE Template_Manager SHALL 包含核心指标定义
4. WHEN 创建提示词模板时，THE Template_Manager SHALL 包含专项否决项规则
5. WHEN 创建提示词模板时，THE Template_Manager SHALL 包含通用一票否决项（造假、师德失范、未提交核心文件）
6. WHEN 创建提示词模板时，THE Template_Manager SHALL 包含加分项规则（总分加分≤10分）
7. WHEN 创建提示词模板时，THE Template_Manager SHALL 定义固定输出格式（得分明细、否决项校验结果、等级、总结）
8. WHERE 管理员需要调整评分标准时，THE Template_Manager SHALL 支持修改指标分值
9. WHERE 管理员需要启用或禁用否决项时，THE Template_Manager SHALL 支持配置否决项开关

### Requirement 4: 文件解析功能

**User Story:** 作为系统，我需要准确提取不同格式文件的文本内容，以便进行自动评分。

#### Acceptance Criteria

1. THE File_Parser SHALL 支持解析 docx 格式文件
2. THE File_Parser SHALL 支持解析 pdf 格式文件
3. THE File_Parser SHALL 支持解析 ppt/pptx 格式文件
4. WHEN 文件格式不支持时，THE File_Parser SHALL 返回错误信息并标记文件为"解析失败"
5. WHEN 文件内容为空时，THE File_Parser SHALL 触发"未提交核心文件"否决项
6. WHEN 文件解析失败时，THE System SHALL 记录错误日志并通知管理员

### Requirement 5: 评分规则执行

**User Story:** 作为系统，我需要严格按照既定规则执行评分逻辑，确保评分的准确性和一致性。

#### Acceptance Criteria

1. WHEN 开始评分时，THE Scoring_Engine SHALL 首先校验通用否决项
2. WHEN 通用否决项被触发时，THE Scoring_Engine SHALL 直接判定为不合格并终止评分
3. WHEN 通用否决项未触发时，THE Scoring_Engine SHALL 校验专项否决项
4. WHEN 专项否决项被触发时，THE Scoring_Engine SHALL 直接判定为不合格并终止评分
5. WHEN 所有否决项均未触发时，THE Scoring_Engine SHALL 按核心指标进行评分
6. WHEN 核心指标评分完成后，THE Scoring_Engine SHALL 计算加分项
7. WHEN 加分项超过10分时，THE Scoring_Engine SHALL 限制加分为10分
8. WHEN 最终得分计算完成后，THE Scoring_Engine SHALL 根据分数映射等级
9. WHEN 最终得分≥90时，THE System SHALL 判定等级为"优秀"
10. WHEN 最终得分在80-89之间时，THE System SHALL 判定等级为"良好"
11. WHEN 最终得分在60-79之间时，THE System SHALL 判定等级为"合格"
12. WHEN 最终得分＜60时，THE System SHALL 判定等级为"不合格"

### Requirement 6: 考评任务管理改造

**User Story:** 作为系统管理员，我需要创建考评任务并配置评分规则，以便教师按要求提交文件并自动评分。

#### Acceptance Criteria

1. WHEN 创建考评任务时，THE Task_Manager SHALL 支持选择需要上传的文件类型（支持多选）
2. WHEN 创建考评任务时，THE Task_Manager SHALL 支持配置加分项规则（是否启用、分值上限）
3. WHEN 创建考评任务时，THE Task_Manager SHALL 支持设置截止时间
4. WHEN 考评任务创建完成后，THE System SHALL 自动推送任务给相关教师
5. WHEN 截止时间到达且教师未提交文件时，THE System SHALL 自动触发"一票否决"并判定为不合格

### Requirement 7: 教师文件提交优化

**User Story:** 作为教师，我需要按照任务要求上传指定类型的文件，并能够查看评分结果。

#### Acceptance Criteria

1. WHEN 教师上传文件时，THE System SHALL 校验文件类型是否符合任务要求
2. WHEN 文件类型不符合要求时，THE System SHALL 拒绝上传并提示错误信息
3. WHEN 文件上传成功后，THE System SHALL 显示"待评分"状态
4. WHEN 截止时间前时，THE System SHALL 允许教师重新上传文件
5. WHEN 教师重新上传文件时，THE System SHALL 覆盖之前的文件并重新评分
6. WHEN 自动评分完成后，THE System SHALL 显示评分明细（得分、等级、扣分理由）

### Requirement 8: 结果复核与异议处理

**User Story:** 作为教师，我需要能够对自动评分结果提出异议，并由管理员进行人工复核，在确认结果后才能公示。

#### Acceptance Criteria

1. WHEN 教师查看评分结果时，THE System SHALL 显示完整的评分明细
2. WHERE 教师对评分结果有异议时，THE Review_Module SHALL 支持提交异议申请
3. WHEN 教师提交异议时，THE Review_Module SHALL 要求填写异议理由
4. WHEN 异议提交成功后，THE System SHALL 通知管理员进行复核
5. WHEN 管理员进行复核时，THE Review_Module SHALL 支持人工重新评分
6. WHEN 管理员调整评分后，THE System SHALL 覆盖自动评分结果
7. WHEN 管理员完成评分（自动或人工调整）后，THE System SHALL 将评分结果返回给教师个人
8. WHEN 评分结果返回给教师后，THE System SHALL 要求教师确认评分结果
9. WHEN 教师确认评分结果后，THE System SHALL 标记该评分为"已确认"状态
10. WHEN 所有教师确认评分后，THE System SHALL 允许管理员公示整体评分结果
11. WHEN 评分被调整时，THE System SHALL 记录调整记录（调整人、调整时间、调整理由）
12. WHEN 管理员需要追溯评分历史时，THE System SHALL 提供完整的评分记录和调整记录
13. WHEN 管理员收到异议申请时，THE System SHALL 在3个工作日内完成复核

### Requirement 9: 随机抽查复核

**User Story:** 作为系统管理员，我需要对自动评分结果进行随机抽查，以验证自动评分的准确性。

#### Acceptance Criteria

1. WHERE 管理员需要验证评分准确性时，THE Review_Module SHALL 支持随机抽取评分结果
2. WHEN 执行随机抽查时，THE Review_Module SHALL 支持设置抽查比例（如10%）
3. WHEN 抽查样本选定后，THE System SHALL 标记这些记录为"待复核"状态
4. WHEN 管理员完成人工复核后，THE System SHALL 记录复核结果（一致/不一致）
5. WHEN 自动评分与人工复核不一致时，THE System SHALL 记录差异原因
6. WHEN 一致性统计时，THE System SHALL 计算自动评分与人工复核的一致性比例

### Requirement 10: 评分结果导出

**User Story:** 作为系统管理员，我需要导出评分结果，以便进行数据分析和存档。

#### Acceptance Criteria

1. WHEN 管理员需要导出评分结果时，THE System SHALL 支持导出为 Excel 格式
2. WHEN 导出评分结果时，THE System SHALL 包含教师姓名、文件类型、得分、等级、扣分理由、加分项、评分时间
3. WHEN 导出评分结果时，THE System SHALL 支持按时间范围筛选
4. WHEN 导出评分结果时，THE System SHALL 支持按文件类型筛选
5. WHEN 导出评分结果时，THE System SHALL 支持按等级筛选

### Requirement 11: 数据安全与权限控制

**User Story:** 作为系统管理员，我需要确保教师上传的文件安全存储，并且只有授权人员可以访问。

#### Acceptance Criteria

1. WHEN 教师上传文件时，THE System SHALL 加密存储文件内容
2. WHEN 存储文件时，THE System SHALL 记录文件的上传者、上传时间、文件哈希值
3. WHEN 用户访问文件时，THE System SHALL 验证用户权限
4. WHEN 教师访问文件时，THE System SHALL 仅允许访问自己上传的文件
5. WHEN 管理员访问文件时，THE System SHALL 允许访问所有文件
6. WHEN 文件被下载时，THE System SHALL 记录下载日志（下载人、下载时间）

### Requirement 12: 系统可扩展性

**User Story:** 作为开发人员，我需要预留接口，以便未来对接其他系统。

#### Acceptance Criteria

1. THE System SHALL 提供 API 接口用于查询评分结果
2. THE System SHALL 提供 API 接口用于同步教师信息
3. THE System SHALL 提供 API 接口用于同步获奖公示信息
4. WHEN 外部系统调用 API 时，THE System SHALL 验证 API 密钥
5. WHEN 外部系统调用 API 时，THE System SHALL 记录调用日志

### Requirement 13: 验收标准

**User Story:** 作为项目负责人，我需要明确的验收标准，以确保系统满足业务需求。

#### Acceptance Criteria

1. THE System SHALL 支持5类文件的自动评分（教案、教学反思、教研/听课记录、成绩/学情分析、课件）
2. WHEN 触发否决项时，THE System SHALL 准确判定为不合格
3. WHEN 计算加分项时，THE System SHALL 准确计算加分（≤10分）
4. WHEN 单个文件评分时，THE System SHALL 在10秒内完成响应
5. WHEN 批量评分100份文件时，THE System SHALL 在10分钟内完成所有评分
6. WHEN 进行一致性验证时，THE System SHALL 达到自动评分与人工复核一致性≥95%
7. THE System SHALL 支持主流文件格式（docx/pdf/ppt）
8. THE System SHALL 兼容 Chrome、Edge、Firefox 浏览器

### Requirement 14: 过渡期试运行

**User Story:** 作为项目负责人，我需要在正式上线前进行试运行，以验证系统的稳定性和准确性。

#### Acceptance Criteria

1. WHERE 系统处于试运行期时，THE System SHALL 对所有自动评分结果进行人工全复核
2. WHEN 试运行期间时，THE System SHALL 记录所有自动评分与人工复核的差异
3. WHEN 试运行期为1个月时，THE System SHALL 在试运行结束后生成一致性报告
4. WHEN 一致性报告生成后，THE System SHALL 统计一致性比例、差异原因分布
5. WHEN 试运行结束且一致性≥95%时，THE System SHALL 允许切换到正式运行模式
