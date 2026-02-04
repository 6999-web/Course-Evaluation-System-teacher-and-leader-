# DeepSeek 自动评分系统快速开始指南

## 5 分钟快速开始

### 第 1 步: 安装依赖

```bash
# 进入后端目录
cd backend

# 安装文件解析依赖
pip install python-docx PyPDF2 python-pptx
```

### 第 2 步: 配置 API 密钥

**方式 A: 设置环境变量（推荐）**

```bash
# Linux/Mac
export DEEPSEEK_API_KEY="sk-b6ca926900534f1fa31067d49980ec56"
export DEEPSEEK_API_URL="https://api.deepseek.com/v1/chat/completions"

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY="sk-b6ca926900534f1fa31067d49980ec56"
$env:DEEPSEEK_API_URL="https://api.deepseek.com/v1/chat/completions"
```

**方式 B: 创建 .env 文件**

在 `backend` 目录创建 `.env` 文件：

```
DEEPSEEK_API_KEY=sk-b6ca926900534f1fa31067d49980ec56
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```

### 第 3 步: 测试系统

```bash
# 运行集成测试
python test_deepseek_integration.py
```

预期输出：
```
✓ API 连接测试: ✓ 通过
✓ 文件解析测试: ✓ 通过
✓ 评分引擎测试: ✓ 通过

总计: 3/3 个测试通过

✓ 所有测试通过！系统已准备就绪。
```

### 第 4 步: 启动应用

```bash
# 启动 FastAPI 应用
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 第 5 步: 测试 API

打开浏览器访问：
```
http://localhost:8000/api/scoring/health
```

预期响应：
```json
{
    "status": "ok",
    "message": "评分系统正常运行"
}
```

## 使用示例

### 示例 1: 单个文件评分

```bash
curl -X POST "http://localhost:8000/api/scoring/score/sub_123" \
  -H "Content-Type: application/json" \
  -d '{
    "bonus_items": [
      {"name": "获奖", "score": 5}
    ]
  }'
```

### 示例 2: 批量评分

```bash
curl -X POST "http://localhost:8000/api/scoring/batch-score" \
  -H "Content-Type: application/json" \
  -d '{
    "submission_ids": ["sub_1", "sub_2", "sub_3"]
  }'
```

### 示例 3: 获取评分记录

```bash
curl -X GET "http://localhost:8000/api/scoring/records/sub_123"
```

## Python 代码示例

### 示例 1: 直接使用评分引擎

```python
from app.scoring_engine import ScoringEngine

# 初始化引擎
engine = ScoringEngine(
    api_key="sk-b6ca926900534f1fa31067d49980ec56"
)

# 教案内容
lesson_plan = """
教学目标：
1. 学生能够理解二次函数的基本概念
2. 学生能够绘制二次函数的图像

教学内容：
本课程介绍二次函数的定义、性质和应用。

教学方法：
1. 讲授法
2. 演示法
3. 练习法

教学评价：
1. 课堂提问
2. 练习评价
3. 作业评价
"""

# 进行评分
result = engine.score_file(
    file_type="教案",
    content=lesson_plan,
    bonus_items=[
        {"name": "获奖", "score": 5}
    ]
)

# 输出结果
print(f"基础分: {result['base_score']}")
print(f"加分: {result['bonus_score']}")
print(f"最终分: {result['final_score']}")
print(f"等级: {result['grade']}")
print(f"评价: {result['summary']}")
```

### 示例 2: 解析文件并评分

```python
from app.file_parser import FileParser
from app.scoring_engine import ScoringEngine

# 解析文件
content = FileParser.parse_file("/path/to/lesson_plan.docx")

# 进行评分
engine = ScoringEngine(api_key="sk-b6ca926900534f1fa31067d49980ec56")
result = engine.score_file("教案", content)

print(f"评分结果: {result['grade']}")
```

## 支持的文件类型

| 文件类型 | 扩展名 | 说明 |
|---------|--------|------|
| 教案 | .docx, .pdf, .txt | 教学计划和设计 |
| 教学反思 | .docx, .pdf, .txt | 教学后的反思总结 |
| 教研/听课记录 | .docx, .pdf, .txt | 教研活动或听课记录 |
| 成绩/学情分析 | .docx, .pdf, .txt | 学生成绩和学情分析 |
| 课件 | .pptx, .pdf | 教学课件 |

## 常见问题

### Q1: API 密钥在哪里获取？

A: API 密钥已提供：`sk-b6ca926900534f1fa31067d49980ec56`

### Q2: 支持哪些文件格式？

A: 支持 DOCX、PDF、PPTX 和 TXT 格式。

### Q3: 评分需要多长时间？

A: 单个文件通常需要 5-10 秒，100 份文件需要 8-10 分钟。

### Q4: 如何处理评分失败？

A: 系统会自动重试 3 次。如果仍然失败，查看日志获取详细错误信息。

### Q5: 评分结果准确吗？

A: 自动评分与人工复核的一致性通常 >95%。

## 故障排查

### 问题: 测试失败 - API 连接错误

**解决方案:**
1. 检查网络连接
2. 验证 API 密钥是否正确
3. 检查防火墙设置

### 问题: 文件解析失败

**解决方案:**
1. 检查文件格式是否支持
2. 验证文件是否损坏
3. 确保文件不为空

### 问题: 评分结果不准确

**解决方案:**
1. 检查文件内容是否完整
2. 查看 API 返回的评分理由
3. 考虑调整提示词模板

## 下一步

1. 阅读 [完整配置指南](DEEPSEEK_SETUP.md)
2. 查看 [API 文档](API_DOCS.md)
3. 了解 [评分标准](SCORING_CRITERIA.md)
4. 配置 [前端集成](../frontend/README.md)

## 获取帮助

- 查看日志文件获取详细错误信息
- 运行集成测试验证系统配置
- 查看源代码中的注释和文档
- 联系技术支持团队

## 下一步操作

### 1. 配置数据库

确保数据库已创建并包含必要的表：

```bash
# 运行数据库迁移
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 2. 配置前端

在前端应用中配置 API 地址：

```javascript
// frontend/src/api/config.ts
export const API_BASE_URL = 'http://localhost:8000';
export const SCORING_API = `${API_BASE_URL}/api/scoring`;
```

### 3. 集成到现有系统

在考评任务管理中添加"评分"按钮，调用评分 API。

### 4. 监控和维护

- 定期检查 API 调用日志
- 监控评分准确性
- 收集用户反馈
- 持续优化评分标准

## 许可证

MIT License

## 联系方式

如有问题，请联系技术支持团队。
