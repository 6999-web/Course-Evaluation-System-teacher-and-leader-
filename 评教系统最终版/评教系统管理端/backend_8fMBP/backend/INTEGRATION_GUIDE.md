# DeepSeek 自动评分系统集成指南

## 概述

本指南说明如何将 DeepSeek 自动评分系统集成到现有的评教系统管理端。

## 集成步骤

### 第 1 步: 安装依赖

确保所有必要的依赖已安装：

```bash
pip install -r requirements.txt
```

关键依赖：
- `python-docx` - 用于解析 DOCX 文件
- `PyPDF2` - 用于解析 PDF 文件
- `python-pptx` - 用于解析 PPTX 文件
- `requests` - 用于调用 API

### 第 2 步: 配置环境变量

在 `.env` 文件中配置 DeepSeek API：

```bash
DEEPSEEK_API_KEY=sk-b6ca926900534f1fa31067d49980ec56
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```

或者设置系统环境变量：

```bash
export DEEPSEEK_API_KEY="sk-b6ca926900534f1fa31067d49980ec56"
export DEEPSEEK_API_URL="https://api.deepseek.com/v1/chat/completions"
```

### 第 3 步: 更新数据库模型

已在 `models.py` 中添加了评分结果字段到 `MaterialSubmission` 模型：

```python
scoring_result = Column(JSON)  # 评分结果
```

运行数据库迁移：

```bash
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 第 4 步: 验证 API 路由

评分 API 路由已在 `app/routes/scoring.py` 中实现，并在 `app/main.py` 中注册：

```python
from .routes.scoring import router as scoring_router
app.include_router(scoring_router)
```

可用的 API 端点：
- `POST /api/scoring/score/{submission_id}` - 单个文件评分
- `POST /api/scoring/batch-score` - 批量评分
- `GET /api/scoring/records/{submission_id}` - 获取评分记录
- `GET /api/scoring/health` - 健康检查

### 第 5 步: 测试系统

运行集成测试验证系统配置：

```bash
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

### 第 6 步: 启动应用

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 前端集成

### 在管理端添加评分功能

#### 1. 在考评任务列表中添加"评分"按钮

在 `EvaluationTaskListAdmin.vue` 中添加评分按钮：

```vue
<template>
  <div class="task-list">
    <el-table :data="tasks">
      <!-- 其他列 -->
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" @click="handleScore(row)">评分</el-button>
          <el-button type="info" @click="handleView(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
const handleScore = async (task) => {
  // 调用评分 API
  const response = await fetch(`/api/scoring/score/${task.submission_id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bonus_items: [] })
  });
  
  const result = await response.json();
  if (result.success) {
    ElMessage.success('评分成功');
    // 刷新列表
    loadTasks();
  } else {
    ElMessage.error(`评分失败: ${result.error}`);
  }
};
</script>
```

#### 2. 创建评分结果展示组件

创建 `ScoringResultDisplay.vue` 组件：

```vue
<template>
  <div class="scoring-result">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评分结果</span>
          <el-tag :type="gradeType">{{ result.grade }}</el-tag>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="score-box">
            <div class="label">基础分</div>
            <div class="value">{{ result.base_score }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="score-box">
            <div class="label">加分</div>
            <div class="value">{{ result.bonus_score }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="score-box">
            <div class="label">最终分</div>
            <div class="value">{{ result.final_score }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="score-box">
            <div class="label">等级</div>
            <div class="value">{{ result.grade }}</div>
          </div>
        </el-col>
      </el-row>
      
      <el-divider></el-divider>
      
      <div v-if="result.veto_triggered" class="veto-warning">
        <el-alert
          title="触发否决项"
          :description="result.veto_reason"
          type="error"
          :closable="false"
        ></el-alert>
      </div>
      
      <div class="score-details">
        <h4>评分明细</h4>
        <el-table :data="result.score_details" stripe>
          <el-table-column prop="indicator" label="指标" width="150"></el-table-column>
          <el-table-column prop="score" label="得分" width="80"></el-table-column>
          <el-table-column prop="max_score" label="满分" width="80"></el-table-column>
          <el-table-column prop="reason" label="评分理由"></el-table-column>
        </el-table>
      </div>
      
      <div class="summary">
        <h4>总体评价</h4>
        <p>{{ result.summary }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
});

const gradeType = computed(() => {
  const grade = props.result.grade;
  if (grade === '优秀') return 'success';
  if (grade === '良好') return 'info';
  if (grade === '合格') return 'warning';
  return 'danger';
});
</script>

<style scoped>
.score-box {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.score-box .label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 10px;
}

.score-box .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.veto-warning {
  margin: 20px 0;
}

.score-details {
  margin: 20px 0;
}

.summary {
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
```

#### 3. 在材料提交列表中显示评分结果

在 `MaterialSubmissionList.vue` 中添加评分结果列：

```vue
<template>
  <el-table :data="submissions">
    <!-- 其他列 -->
    <el-table-column label="评分状态" width="100">
      <template #default="{ row }">
        <el-tag v-if="row.scoring_result" type="success">已评分</el-tag>
        <el-tag v-else type="info">待评分</el-tag>
      </template>
    </el-table-column>
    
    <el-table-column label="最终分" width="80">
      <template #default="{ row }">
        {{ row.scoring_result?.final_score || '-' }}
      </template>
    </el-table-column>
    
    <el-table-column label="等级" width="80">
      <template #default="{ row }">
        <el-tag v-if="row.scoring_result" :type="getGradeType(row.scoring_result.grade)">
          {{ row.scoring_result.grade }}
        </el-tag>
      </template>
    </el-table-column>
    
    <el-table-column label="操作" width="150">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="handleScore(row)">
          {{ row.scoring_result ? '重新评分' : '评分' }}
        </el-button>
        <el-button v-if="row.scoring_result" type="info" size="small" @click="handleViewResult(row)">
          查看结果
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
const getGradeType = (grade) => {
  if (grade === '优秀') return 'success';
  if (grade === '良好') return 'info';
  if (grade === '合格') return 'warning';
  return 'danger';
};

const handleScore = async (submission) => {
  // 调用评分 API
  const response = await fetch(`/api/scoring/score/${submission.submission_id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bonus_items: [] })
  });
  
  const result = await response.json();
  if (result.success) {
    ElMessage.success('评分成功');
    // 更新提交记录
    submission.scoring_result = result.scoring_result;
  } else {
    ElMessage.error(`评分失败: ${result.error}`);
  }
};

const handleViewResult = (submission) => {
  // 显示评分结果详情
  ElDialog.open({
    title: '评分结果',
    content: ScoringResultDisplay,
    props: { result: submission.scoring_result }
  });
};
</script>
```

### 在教师端显示评分结果

在教师端的材料提交记录中显示评分结果：

```vue
<template>
  <div class="submission-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>提交详情</span>
          <el-tag v-if="submission.scoring_result" :type="getGradeType(submission.scoring_result.grade)">
            {{ submission.scoring_result.grade }}
          </el-tag>
        </div>
      </template>
      
      <!-- 提交信息 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="提交时间">
          {{ formatDate(submission.submitted_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="审核状态">
          {{ submission.review_status }}
        </el-descriptions-item>
      </el-descriptions>
      
      <!-- 评分结果 -->
      <div v-if="submission.scoring_result" class="scoring-result">
        <ScoringResultDisplay :result="submission.scoring_result"></ScoringResultDisplay>
      </div>
      
      <!-- 操作按钮 -->
      <div class="actions">
        <el-button v-if="submission.scoring_result" type="primary" @click="handleAppeal">
          提交异议
        </el-button>
        <el-button v-if="submission.scoring_result && !submission.confirmed" type="success" @click="handleConfirm">
          确认评分
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
const handleAppeal = () => {
  // 打开异议申请对话框
};

const handleConfirm = async () => {
  // 确认评分
  const response = await fetch(`/api/scoring/confirm/${submission.value.scoring_result.id}`, {
    method: 'POST'
  });
  
  if (response.ok) {
    ElMessage.success('评分已确认');
    submission.value.confirmed = true;
  }
};
</script>
```

## API 集成示例

### 使用 JavaScript/TypeScript

```typescript
// api/scoring.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const scoringAPI = {
  // 单个文件评分
  scoreSubmission: (submissionId: string, bonusItems?: any[]) => {
    return axios.post(`${API_BASE_URL}/api/scoring/score/${submissionId}`, {
      bonus_items: bonusItems || []
    });
  },
  
  // 批量评分
  batchScore: (submissionIds: string[]) => {
    return axios.post(`${API_BASE_URL}/api/scoring/batch-score`, {
      submission_ids: submissionIds
    });
  },
  
  // 获取评分记录
  getScoringRecord: (submissionId: string) => {
    return axios.get(`${API_BASE_URL}/api/scoring/records/${submissionId}`);
  },
  
  // 健康检查
  healthCheck: () => {
    return axios.get(`${API_BASE_URL}/api/scoring/health`);
  }
};
```

### 使用 Python

```python
import requests

API_BASE_URL = 'http://localhost:8000'

def score_submission(submission_id, bonus_items=None):
    """单个文件评分"""
    response = requests.post(
        f'{API_BASE_URL}/api/scoring/score/{submission_id}',
        json={'bonus_items': bonus_items or []}
    )
    return response.json()

def batch_score(submission_ids):
    """批量评分"""
    response = requests.post(
        f'{API_BASE_URL}/api/scoring/batch-score',
        json={'submission_ids': submission_ids}
    )
    return response.json()

def get_scoring_record(submission_id):
    """获取评分记录"""
    response = requests.get(
        f'{API_BASE_URL}/api/scoring/records/{submission_id}'
    )
    return response.json()
```

## 数据库集成

### 查询评分结果

```python
from sqlalchemy.orm import Session
from app.models import MaterialSubmission

def get_submissions_with_scores(db: Session):
    """获取所有已评分的提交"""
    return db.query(MaterialSubmission).filter(
        MaterialSubmission.scoring_result != None
    ).all()

def get_submissions_by_grade(db: Session, grade: str):
    """按等级查询提交"""
    submissions = db.query(MaterialSubmission).filter(
        MaterialSubmission.scoring_result != None
    ).all()
    
    return [
        s for s in submissions
        if s.scoring_result.get('grade') == grade
    ]
```

### 统计评分结果

```python
def get_scoring_statistics(db: Session):
    """获取评分统计"""
    submissions = db.query(MaterialSubmission).filter(
        MaterialSubmission.scoring_result != None
    ).all()
    
    stats = {
        'total': len(submissions),
        'excellent': 0,
        'good': 0,
        'pass': 0,
        'fail': 0,
        'average_score': 0
    }
    
    total_score = 0
    for s in submissions:
        grade = s.scoring_result.get('grade')
        if grade == '优秀':
            stats['excellent'] += 1
        elif grade == '良好':
            stats['good'] += 1
        elif grade == '合格':
            stats['pass'] += 1
        else:
            stats['fail'] += 1
        
        total_score += s.scoring_result.get('final_score', 0)
    
    if stats['total'] > 0:
        stats['average_score'] = total_score / stats['total']
    
    return stats
```

## 监控和维护

### 监控 API 调用

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在 scoring_engine.py 中已实现日志记录
# 查看日志：
# tail -f app.log | grep "API"
```

### 性能监控

```python
import time

def monitor_scoring_performance(submission_ids):
    """监控评分性能"""
    start_time = time.time()
    
    # 执行批量评分
    result = batch_score(submission_ids)
    
    elapsed_time = time.time() - start_time
    
    print(f"评分 {len(submission_ids)} 份文件耗时: {elapsed_time:.2f} 秒")
    print(f"平均每份文件耗时: {elapsed_time / len(submission_ids):.2f} 秒")
    print(f"成功率: {result['success'] / result['total'] * 100:.1f}%")
```

## 故障排查

### 常见问题

1. **API 连接失败**
   - 检查网络连接
   - 验证 API 密钥
   - 查看防火墙设置

2. **文件解析失败**
   - 检查文件格式
   - 验证文件完整性
   - 查看错误日志

3. **评分结果不准确**
   - 检查文件内容
   - 查看 API 返回的理由
   - 调整提示词模板

## 下一步

1. 部署到生产环境
2. 配置监控和告警
3. 收集用户反馈
4. 持续优化评分标准

## 支持

如有问题，请查看：
- [快速开始指南](QUICKSTART.md)
- [完整配置指南](DEEPSEEK_SETUP.md)
- [系统 README](DEEPSEEK_README.md)
