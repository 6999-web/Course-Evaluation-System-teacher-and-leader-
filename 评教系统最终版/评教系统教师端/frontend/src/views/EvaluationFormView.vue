<template>
  <div class="evaluation-form-view">
    <div class="page-header">
      <h2>待办考评</h2>
      <el-button type="primary" @click="refreshTasks">
        <el-icon><refresh /></el-icon>
        刷新
      </el-button>
    </div>
    
    <!-- 任务列表 -->
    <el-card class="task-card">
      <el-table 
        :data="tasks" 
        stripe 
        style="width: 100%"
        :loading="loading"
      >
        <el-table-column prop="task_id" label="任务ID" width="150" />
        <el-table-column prop="template_name" label="考评表名称" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ row.submitted_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'pending'" 
              link 
              type="primary" 
              @click="uploadFiles(row)"
            >
              上传文件
            </el-button>
            <el-button link type="primary" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button 
              v-if="row.status === 'scored'" 
              link 
              type="success" 
              @click="viewScore(row)"
            >
              查看评分
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 上传文件对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="600px">
      <div v-if="currentTask" class="upload-dialog">
        <div class="task-info">
          <p><strong>考评表：</strong> {{ currentTask.template_name }}</p>
          <p><strong>截止时间：</strong> {{ currentTask.deadline }}</p>
          <p><strong>提交要求：</strong> {{ currentTask.submission_requirements?.description }}</p>
        </div>
        
        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            v-model:file-list="fileList"
            action="#"
            :auto-upload="false"
            :on-change="handleFileSelect"
            :limit="currentTask.submission_requirements?.max_files || 3"
            accept=".pdf,.xlsx,.xls,.docx,.doc"
            multiple
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Excel、Word 格式，单个文件不超过 50MB，最多 {{ currentTask.submission_requirements?.max_files || 3 }} 个文件
              </div>
            </template>
          </el-upload>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFiles" :loading="uploadLoading">
          提交文件
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="任务详情" width="700px">
      <div v-if="currentTask" class="detail-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ currentTask.task_id }}</el-descriptions-item>
          <el-descriptions-item label="考评表">{{ currentTask.template_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.status)">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总分">{{ currentTask.total_score }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTask.created_at }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ currentTask.submitted_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ currentTask.deadline }}</el-descriptions-item>
          <el-descriptions-item label="当前得分">{{ currentTask.score || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentTask.scoring_criteria" class="criteria-section">
          <h4>评分标准</h4>
          <el-table :data="currentTask.scoring_criteria" stripe>
            <el-table-column prop="name" label="评分项" />
            <el-table-column prop="max_score" label="最高分" width="100" />
          </el-table>
        </div>
        
        <div v-if="currentTask.submitted_files && currentTask.submitted_files.length > 0" class="files-section">
          <h4>已提交文件</h4>
          <el-table :data="currentTask.submitted_files" stripe>
            <el-table-column prop="filename" label="文件名" />
            <el-table-column prop="file_size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="uploaded_at" label="上传时间" width="180" />
          </el-table>
        </div>
      </div>
    </el-dialog>
    
    <!-- 评分详情对话框 -->
    <el-dialog v-model="scoreDialogVisible" title="评分详情" width="600px">
      <div v-if="currentTask && currentTask.score !== null && currentTask.score !== undefined" class="score-dialog">
        <div class="score-header">
          <div class="score-display">
            <span class="score-label">总分</span>
            <span class="score-value">{{ currentTask.score }}</span>
            <span class="score-max">/ {{ currentTask.total_score }}</span>
          </div>
          <div class="score-percentage">
            {{ calculatePercentage(currentTask.score, currentTask.total_score) }}%
          </div>
        </div>
        
        <div v-if="currentTask.scoring_criteria && currentTask.scoring_criteria.length > 0" class="criteria-scores">
          <h4>各项评分</h4>
          <div v-for="criterion in currentTask.scoring_criteria" :key="criterion.name" class="criterion-score">
            <span class="criterion-name">{{ criterion.name }}</span>
            <span class="criterion-value">
              {{ getCriterionScore(criterion.name) }} / {{ criterion.max_score }}
            </span>
          </div>
        </div>
        
        <div v-if="currentTask.scoring_feedback" class="feedback-section">
          <h4>评分反馈</h4>
          <p>{{ currentTask.scoring_feedback }}</p>
        </div>
      </div>
      <div v-else class="score-dialog">
        <p style="color: #999; text-align: center;">暂无评分数据</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

const tasks = ref([])
const loading = ref(false)
const uploadLoading = ref(false)

const uploadDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const scoreDialogVisible = ref(false)

const currentTask = ref<any>(null)
const fileList = ref([])
const uploadRef = ref<any>(null)
const uploadedFileIds = ref<string[]>([])  // ← 新增：保存上传的文件ID

// 获取token
const getToken = () => {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
}

// 获取API基础URL
const getApiBaseUrl = () => {
  return 'http://localhost:8000'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待提交',
    submitted: '已提交',
    scored: '已评分'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    submitted: 'warning',
    scored: 'success'
  }
  return typeMap[status] || 'info'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${getApiBaseUrl()}/api/teacher/evaluation-tasks`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })
    // 处理响应数据
    const data = response.data
    if (data.pending_tasks || data.submitted_tasks) {
      // 合并所有任务
      tasks.value = [...(data.pending_tasks || []), ...(data.submitted_tasks || [])]
    } else if (Array.isArray(data)) {
      tasks.value = data
    } else if (data.tasks) {
      tasks.value = data.tasks
    } else {
      tasks.value = []
    }
  } catch (error: any) {
    console.error('加载任务失败:', error)
    ElMessage.error(`加载任务失败: ${error.response?.data?.detail || error.message}`)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const refreshTasks = () => {
  loadTasks()
}

const handleFileSelect = (file: any) => {
  // File selection is handled by el-upload
}

const uploadFiles = (task: any) => {
  currentTask.value = task
  fileList.value = []
  uploadedFileIds.value = []  // ← 重置已上传文件ID
  uploadDialogVisible.value = true
}

const submitFiles = async () => {
  if (fileList.value.length === 0) {
    ElMessage.error('请选择至少一个文件')
    return
  }

  uploadLoading.value = true
  try {
    // Upload files and collect file IDs
    uploadedFileIds.value = []
    for (const file of fileList.value) {
      const formData = new FormData()
      formData.append('file', file.raw || file)

      const uploadResponse = await axios.post(
        `${getApiBaseUrl()}/api/teacher/evaluation-tasks/${currentTask.value.task_id}/upload`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${getToken()}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      // 保存返回的文件ID
      if (uploadResponse.data.file_id) {
        uploadedFileIds.value.push(uploadResponse.data.file_id)
      }
    }

    // Submit files with file IDs
    if (uploadedFileIds.value.length === 0) {
      ElMessage.error('文件上传失败，无法获取文件ID')
      return
    }

    // 构建Query参数
    const params = new URLSearchParams()
    uploadedFileIds.value.forEach(id => params.append('file_ids', id))
    params.append('notes', '')

    await axios.post(
      `${getApiBaseUrl()}/api/teacher/evaluation-tasks/${currentTask.value.task_id}/submit?${params.toString()}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        }
      }
    )

    ElMessage.success('文件提交成功')
    uploadDialogVisible.value = false
    loadTasks()
  } catch (error: any) {
    console.error('提交错误:', error)
    ElMessage.error(`提交失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    uploadLoading.value = false
  }
}

const viewDetail = (task: any) => {
  currentTask.value = task
  detailDialogVisible.value = true
}

const viewScore = (task: any) => {
  currentTask.value = task
  scoreDialogVisible.value = true
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const calculatePercentage = (score: number | null | undefined, total: number | null | undefined) => {
  if (score === null || score === undefined || total === null || total === undefined || total === 0) {
    return 0
  }
  return Math.round((score / total) * 100)
}

const getCriterionScore = (criterionName: string) => {
  if (!currentTask.value || !currentTask.value.scores) {
    return 0
  }
  return currentTask.value.scores[criterionName] || 0
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.evaluation-form-view {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #003366;
}

.task-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.upload-dialog {
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

.upload-section {
  margin-bottom: 1rem;
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

.files-section {
  margin-top: 1.5rem;
}

.files-section h4 {
  margin-bottom: 1rem;
  color: #212121;
}

.score-dialog {
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
}

.criterion-value {
  color: #ff3b30;
  font-weight: bold;
}

.feedback-section {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
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
</style>
