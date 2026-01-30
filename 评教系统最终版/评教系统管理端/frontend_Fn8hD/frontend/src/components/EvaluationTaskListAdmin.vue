<template>
  <div class="evaluation-task-list">
    <h2 class="page-title">考评任务管理</h2>
    
    <el-card class="task-card">
      <!-- 筛选条件 -->
      <div class="filters-section">
        <el-form :model="filters" label-width="100px" class="filters-form">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="任务状态">
                <el-select v-model="filters.status" placeholder="所有状态" clearable>
                  <el-option label="未查收" value="pending" />
                  <el-option label="已查收" value="viewed" />
                  <el-option label="已提交" value="submitted" />
                  <el-option label="已评分" value="scored" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="教师ID">
                <el-input v-model="filters.teacher_id" placeholder="输入教师ID" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="考评表">
                <el-input v-model="filters.template_id" placeholder="输入考评表ID" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="primary" @click="loadTasks" :loading="loading">
                <el-icon><search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <!-- 任务列表 -->
      <el-table 
        :data="tasks" 
        stripe 
        style="width: 100%"
        :loading="loading"
        class="task-table"
      >
        <el-table-column prop="task_id" label="任务ID" width="150" />
        <el-table-column prop="template_name" label="考评表名称" min-width="150" />
        <el-table-column prop="teacher_id" label="教师ID" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.display_status || row.status)">
              {{ getStatusText(row.display_status || row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ row.submitted_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button 
                v-if="row.status === 'submitted'" 
                link 
                type="primary" 
                size="small"
                @click="openScoreDialog(row)"
              >
                <el-icon><edit /></el-icon>
                评分
              </el-button>
              <el-button 
                v-if="row.status === 'scored'" 
                link 
                type="success" 
                size="small"
                @click="viewScore(row)"
              >
                <el-icon><view /></el-icon>
                查看评分
              </el-button>
              <el-button 
                link 
                type="info" 
                size="small"
                @click="viewDetail(row)"
              >
                <el-icon><document /></el-icon>
                详情
              </el-button>
              <el-button 
                v-if="row.submitted_files && row.submitted_files.length > 0"
                link 
                type="warning" 
                size="small"
                @click="viewFiles(row)"
              >
                <el-icon><folder /></el-icon>
                文件
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        class="pagination"
      />
    </el-card>
    
    <!-- 评分对话框 -->
    <el-dialog v-model="scoreDialogVisible" title="考评任务评分" width="800px" @close="resetScoreData">
      <div v-if="currentTask" class="score-dialog">
        <div class="task-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="考评表">{{ currentTask.template_name }}</el-descriptions-item>
            <el-descriptions-item label="教师">{{ currentTask.teacher_id }}</el-descriptions-item>
            <el-descriptions-item label="提交时间">{{ currentTask.submitted_at }}</el-descriptions-item>
            <el-descriptions-item label="截止时间">{{ currentTask.deadline }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="scoring-section">
          <h4>
            <el-icon><edit /></el-icon>
            评分标准
          </h4>
          <div v-if="currentTask.scoring_criteria && currentTask.scoring_criteria.length > 0" class="score-items">
            <div v-for="(criterion, index) in currentTask.scoring_criteria" :key="index" class="score-item">
              <div class="criterion-info">
                <label class="criterion-label">{{ criterion.name }}</label>
                <span class="criterion-desc" v-if="criterion.description">{{ criterion.description }}</span>
              </div>
              <div class="score-input-group">
                <el-input-number 
                  v-model.number="scoreData.scores[criterion.name]" 
                  :min="0"
                  :max="criterion.max_score"
                  :precision="1"
                  :step="0.5"
                  class="score-input"
                  @change="onScoreChange"
                />
                <span class="score-max">/ {{ criterion.max_score }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-criteria">
            <el-alert
              title="暂无评分标准"
              type="warning"
              :closable="false"
              show-icon
            />
          </div>
          
          <div class="total-score-display">
            <div class="score-summary">
              <span class="score-label">总分：</span>
              <strong class="score-value">{{ calculateTotalScore() }}</strong>
              <span class="score-max">/ {{ currentTask.total_score || 100 }}</span>
            </div>
            <div class="score-percentage">
              <el-tag :type="getScoreType(calculatePercentage())" size="large">
                {{ calculatePercentage() }}%
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="feedback-section">
          <h4>
            <el-icon><chat-line-round /></el-icon>
            评分反馈
          </h4>
          <el-input 
            v-model="scoreData.feedback" 
            type="textarea"
            placeholder="请输入评分反馈和建议（可选）"
            :rows="4"
            maxlength="500"
            show-word-limit
          />
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="scoreDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitScore" :loading="scoreLoading">
            <el-icon><check /></el-icon>
            提交评分
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="任务详情" width="700px">
      <div v-if="currentTask" class="detail-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentTask.task_id }}</el-descriptions-item>
          <el-descriptions-item label="考评表">{{ currentTask.template_name }}</el-descriptions-item>
          <el-descriptions-item label="教师ID">{{ currentTask.teacher_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.display_status || currentTask.status)">
              {{ getStatusText(currentTask.display_status || currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总分">{{ currentTask.total_score }}</el-descriptions-item>
          <el-descriptions-item label="当前得分">
            {{ currentTask.score || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTask.created_at }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ currentTask.submitted_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ currentTask.deadline }}</el-descriptions-item>
          <el-descriptions-item label="评分时间">{{ currentTask.scored_at || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentTask.scoring_criteria" class="criteria-section">
          <h4>评分标准</h4>
          <el-table :data="currentTask.scoring_criteria" stripe>
            <el-table-column prop="name" label="评分项" />
            <el-table-column prop="max_score" label="最高分" width="100" />
          </el-table>
        </div>
        
        <div v-if="currentTask.feedback" class="feedback-display">
          <h4>评分反馈</h4>
          <p>{{ currentTask.feedback }}</p>
        </div>
      </div>
    </el-dialog>
    
    <!-- 文件列表对话框 -->
    <el-dialog v-model="filesDialogVisible" title="提交文件" width="600px">
      <div v-if="currentTask" class="files-dialog">
        <el-table :data="currentTask.submitted_files || []" stripe>
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="file_size" label="大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column prop="uploaded_at" label="上传时间" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="downloadFile(row)">
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
    
    <!-- 评分详情对话框 -->
    <el-dialog v-model="scoreDetailDialogVisible" title="评分详情" width="800px">
      <div v-if="currentTask" class="score-detail-dialog">
        <div class="score-header">
          <div class="score-display">
            <div class="score-main">
              <span class="score-label">总分</span>
              <span class="score-value">{{ currentTask.score !== undefined && currentTask.score !== null ? currentTask.score : 0 }}</span>
              <span class="score-max">/ {{ currentTask.total_score || 100 }}</span>
            </div>
            <div class="score-percentage">
              <el-tag :type="getScoreType(currentTask.total_score && currentTask.score !== undefined && currentTask.score !== null ? Math.round(((currentTask.score || 0) / currentTask.total_score) * 100) : 0)" size="large">
                {{ currentTask.total_score && currentTask.score !== undefined && currentTask.score !== null ? Math.round(((currentTask.score || 0) / currentTask.total_score) * 100) : 0 }}%
              </el-tag>
            </div>
          </div>
        </div>
        
        <div v-if="currentTask.scoring_criteria && currentTask.scoring_criteria.length > 0" class="criteria-scores">
          <h4>
            <el-icon><document /></el-icon>
            各项评分详情
          </h4>
          <div class="criteria-grid">
            <div v-for="criterion in currentTask.scoring_criteria" :key="criterion.name" class="criterion-card">
              <div class="criterion-header">
                <span class="criterion-name">{{ criterion.name }}</span>
                <span class="criterion-score">
                  {{ (currentTask.scores && currentTask.scores[criterion.name] !== undefined) ? currentTask.scores[criterion.name] : 0 }} / {{ criterion.max_score }}
                </span>
              </div>
              <div class="criterion-progress">
                <el-progress 
                  :percentage="criterion.max_score ? Math.round((((currentTask.scores && currentTask.scores[criterion.name]) || 0) / criterion.max_score) * 100) : 0"
                  :color="getProgressColor(criterion.max_score ? Math.round((((currentTask.scores && currentTask.scores[criterion.name]) || 0) / criterion.max_score) * 100) : 0)"
                  :stroke-width="8"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="currentTask.scoring_feedback" class="feedback-section">
          <h4>
            <el-icon><chat-line-round /></el-icon>
            评分反馈
          </h4>
          <div class="feedback-content">
            <p>{{ currentTask.scoring_feedback }}</p>
          </div>
        </div>
        
        <div class="score-meta">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="评分时间">
              {{ currentTask.scored_at || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="评分状态">
              <el-tag type="success">已完成</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Edit, View, Document, Folder, ChatLineRound, Check } from '@element-plus/icons-vue'
import axios from 'axios'

const filters = ref({
  status: '',
  teacher_id: '',
  template_id: ''
})

const tasks = ref([])
const loading = ref(false)
const scoreLoading = ref(false)

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0
})

const scoreDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const filesDialogVisible = ref(false)
const scoreDetailDialogVisible = ref(false)  // ← 新增

const currentTask = ref<any>(null)
const scoreData = ref({
  scores: {} as Record<string, number>,
  feedback: ''
})

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '未查收',
    viewed: '已查收',
    submitted: '已提交',
    scored: '已评分'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    viewed: 'warning',
    submitted: 'warning',
    scored: 'success'
  }
  return typeMap[status] || 'info'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8001/api/evaluation-tasks', {
      params: {
        ...filters.value,
        page: pagination.value.page,
        page_size: pagination.value.pageSize
      },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    console.log('任务列表响应:', response.data)
    tasks.value = response.data.tasks || []
    pagination.value.total = response.data.total || 0
    
    // 调试：检查任务数据
    if (tasks.value.length > 0) {
      console.log('第一个任务数据:', tasks.value[0])
      const submittedTask = tasks.value.find(t => t.status === 'submitted')
      if (submittedTask) {
        console.log('已提交任务示例:', submittedTask)
        console.log('评分标准:', submittedTask.scoring_criteria)
      }
    }
    
  } catch (error: any) {
    console.error('加载任务失败:', error)
    ElMessage.error(`加载任务失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    teacher_id: '',
    template_id: ''
  }
  pagination.value.page = 1
  loadTasks()
}

const openScoreDialog = (task: any) => {
  console.log('打开评分对话框，任务数据:', task)
  currentTask.value = task
  
  // 初始化评分数据 - 使用对象格式而不是数组
  if (task.scoring_criteria && task.scoring_criteria.length > 0) {
    const scoresObj: Record<string, number> = {}
    task.scoring_criteria.forEach((criterion: any) => {
      // 如果已有评分，使用已有的；否则初始化为0
      scoresObj[criterion.name] = (task.scores && task.scores[criterion.name]) || 0
    })
    scoreData.value = {
      scores: scoresObj,
      feedback: task.scoring_feedback || ''
    }
  } else {
    scoreData.value = {
      scores: {},
      feedback: ''
    }
  }
  
  console.log('初始化评分数据:', scoreData.value)
  scoreDialogVisible.value = true
}

const calculateTotalScore = () => {
  if (!currentTask.value?.scoring_criteria) return 0
  // scoreData.scores is now an object: { "完成度": 8, "准确性": 9, ... }
  const total = Object.values(scoreData.value.scores).reduce((sum: number, score: any) => sum + (score || 0), 0)
  console.log('计算总分:', scoreData.value.scores, '=', total)
  return total
}

const calculatePercentage = () => {
  const total = calculateTotalScore()
  const maxScore = currentTask.value?.total_score || 100
  if (maxScore === 0) return 0
  const percentage = Math.round((total / maxScore) * 100)
  console.log('计算百分比:', total, '/', maxScore, '=', percentage, '%')
  return percentage
}

const getScoreType = (percentage: number) => {
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'primary'
  if (percentage >= 70) return 'warning'
  if (percentage >= 60) return 'info'
  return 'danger'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 80) return '#409eff'
  if (percentage >= 70) return '#e6a23c'
  if (percentage >= 60) return '#909399'
  return '#f56c6c'
}

const onScoreChange = () => {
  console.log('评分变化:', scoreData.value.scores)
  // 触发重新渲染
}

const resetScoreData = () => {
  scoreData.value = {
    scores: {},
    feedback: ''
  }
}

const submitScore = async () => {
  if (!currentTask.value) return

  console.log('提交评分，当前任务:', currentTask.value.task_id)
  console.log('评分数据:', scoreData.value)

  scoreLoading.value = true
  try {
    // scoreData.scores 已经是对象格式: { "完成度": 8, "准确性": 9, ... }
    const scoresObj = scoreData.value.scores
    
    console.log('转换后的评分对象:', scoresObj)
    
    const scoresJson = JSON.stringify(scoresObj)
    console.log('JSON字符串:', scoresJson)

    // 构建Query参数
    const params = new URLSearchParams()
    params.append('scores', scoresJson)
    params.append('feedback', scoreData.value.feedback)

    console.log('请求URL:', `http://localhost:8001/api/evaluation-tasks/${currentTask.value.task_id}/score?${params.toString()}`)

    const response = await axios.post(
      `http://localhost:8001/api/evaluation-tasks/${currentTask.value.task_id}/score?${params.toString()}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('评分响应:', response.data)
    ElMessage.success('评分成功')
    scoreDialogVisible.value = false
    loadTasks()
  } catch (error: any) {
    console.error('评分错误:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error(`评分失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    scoreLoading.value = false
  }
}

const viewDetail = (task: any) => {
  currentTask.value = task
  detailDialogVisible.value = true
}

const viewFiles = (task: any) => {
  currentTask.value = task
  filesDialogVisible.value = true
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const downloadFile = (file: any) => {
  ElMessage.info('下载功能开发中...')
}

// 监听评分数据变化，实时更新总分
watch(
  () => scoreData.value.scores,
  (newScores) => {
    console.log('评分数据变化:', newScores)
    // 触发重新渲染
  },
  { deep: true }
)

const viewScore = (task: any) => {
  console.log('=== 查看评分 ===')
  console.log('任务数据:', task)
  console.log('scores:', task.scores)
  console.log('score:', task.score)
  console.log('total_score:', task.total_score)
  console.log('scoring_criteria:', task.scoring_criteria)
  console.log('scoring_feedback:', task.scoring_feedback)
  console.log('scored_at:', task.scored_at)
  
  currentTask.value = task
  scoreDetailDialogVisible.value = true
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.evaluation-task-list {
  width: 100%;
  padding: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #003366;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.task-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filters-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.filters-form {
  margin: 0;
}

.task-table {
  margin-bottom: 1.5rem;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.score-dialog {
  padding: 1rem 0;
}

.task-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.task-info p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.scoring-section {
  margin-bottom: 1.5rem;
}

.scoring-section h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.score-item label {
  min-width: 100px;
  font-weight: 500;
}

.score-input {
  width: 120px;
}

.score-max {
  color: #757575;
  font-size: 0.9rem;
}

.total-score-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-top: 1rem;
  font-size: 0.95rem;
}

.total-score-display strong {
  color: #ff3b30;
  font-size: 1.1rem;
}

.feedback-section {
  margin-bottom: 1rem;
}

.feedback-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.detail-dialog {
  padding: 1rem 0;
}

.criteria-section {
  margin-top: 1.5rem;
}

.criteria-section h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.feedback-display {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.feedback-display h4 {
  margin-top: 0;
  color: #212121;
}

.feedback-display p {
  margin: 0;
  color: #424242;
  line-height: 1.6;
}

.files-dialog {
  padding: 1rem 0;
}

.score-detail-dialog {
  padding: 1rem 0;
}

.score-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f6f8fb 0%, #e8f0f8 100%);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.score-label {
  font-size: 0.9rem;
  color: #757575;
}

.score-value {
  font-size: 2rem;
  font-weight: bold;
  color: #ff3b30;
}

.score-max {
  font-size: 0.9rem;
  color: #757575;
}

.score-percentage {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4CAF50;
}

.criteria-scores {
  margin-bottom: 1.5rem;
}

.criteria-scores h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.criterion-score {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
}

.criterion-name {
  font-weight: 500;
  color: #212121;
  min-width: 100px;
}

.criterion-value {
  color: #ff3b30;
  font-weight: bold;
  min-width: 80px;
  text-align: center;
}

.criterion-percentage {
  color: #4CAF50;
  font-weight: bold;
  min-width: 60px;
  text-align: right;
}

.feedback-section {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.feedback-section h4 {
  margin-top: 0;
  color: #212121;
}

.feedback-section p {
  margin: 0;
  color: #424242;
  line-height: 1.6;
}

.score-info {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.score-info p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
  color: #424242;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
  padding: 4px 8px;
  font-size: 0.85rem;
}

.action-buttons .el-button .el-icon {
  margin-right: 2px;
}

/* 评分对话框样式 */
.score-dialog {
  padding: 0;
}

.task-info {
  margin-bottom: 1.5rem;
}

.scoring-section h4,
.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #212121;
  font-size: 1rem;
  font-weight: 600;
}

.score-items {
  margin-bottom: 1.5rem;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  margin-bottom: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.criterion-info {
  flex: 1;
  margin-right: 1rem;
}

.criterion-label {
  display: block;
  font-weight: 500;
  color: #212121;
  margin-bottom: 0.25rem;
}

.criterion-desc {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.4;
}

.score-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-input {
  width: 120px;
}

.score-max {
  color: #757575;
  font-size: 0.9rem;
  font-weight: 500;
}

.no-criteria {
  margin-bottom: 1.5rem;
}

.total-score-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f6f8fb 0%, #e8f0f8 100%);
  border-radius: 8px;
  margin-top: 1rem;
  border: 2px solid #e3f2fd;
}

.score-summary {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.score-label {
  font-size: 1rem;
  color: #424242;
  font-weight: 500;
}

.score-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #1976d2;
}

.score-percentage .el-tag {
  font-size: 1.1rem;
  font-weight: bold;
  padding: 8px 16px;
}

.feedback-section {
  margin-top: 1.5rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* 评分详情对话框样式 */
.score-detail-dialog {
  padding: 0;
}

.score-header {
  margin-bottom: 2rem;
}

.score-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.score-main {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.score-detail-dialog .score-label {
  font-size: 1rem;
  opacity: 0.9;
}

.score-detail-dialog .score-value {
  font-size: 2.5rem;
  font-weight: bold;
}

.score-detail-dialog .score-max {
  font-size: 1.2rem;
  opacity: 0.8;
}

.criteria-scores {
  margin-bottom: 2rem;
}

.criteria-scores h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  color: #212121;
  font-size: 1.1rem;
  font-weight: 600;
}

.criteria-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.criterion-card {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.criterion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.criterion-name {
  font-weight: 600;
  color: #212121;
  font-size: 0.95rem;
}

.criterion-score {
  font-weight: bold;
  color: #1976d2;
  font-size: 1rem;
}

.criterion-progress {
  margin-top: 0.5rem;
}

.feedback-section {
  margin-bottom: 2rem;
}

.feedback-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #212121;
  font-size: 1.1rem;
  font-weight: 600;
}

.feedback-content {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.feedback-content p {
  margin: 0;
  color: #424242;
  line-height: 1.6;
  font-size: 0.95rem;
}

.score-meta {
  margin-top: 1.5rem;
}
</style>
