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
            <div style="position: relative; z-index: 10; display: flex; gap: 8px;">
              <el-button 
                v-if="row.status === 'pending'" 
                link 
                type="primary" 
                @click="uploadFiles(row)"
                style="cursor: pointer; pointer-events: auto;"
              >
                上传文件
              </el-button>
              <el-button 
                link 
                type="primary" 
                @click="viewDetail(row)"
                style="cursor: pointer; pointer-events: auto;"
              >
                查看详情
              </el-button>
            </div>
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
            drag
          >
            <template #trigger>
              <el-button type="primary" style="position: relative; z-index: 10;">选择文件</el-button>
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
        
        <!-- 考评表文件部分 -->
        <div class="template-file-section">
          <h4>考评表文件</h4>
          <div class="file-item">
            <el-icon><document /></el-icon>
            <span class="file-name">{{ currentTask.template_name }}</span>
            <el-button link type="primary" @click="downloadTemplateFile(currentTask)">
              下载
            </el-button>
            <el-button link type="primary" @click="previewTemplateFile(currentTask)">
              预览
            </el-button>
          </div>
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

const viewDetail = async (task: any) => {
  currentTask.value = task
  detailDialogVisible.value = true
  
  // 同步查收状态到管理端
  try {
    await axios.post(
      `http://localhost:8001/api/evaluation-tasks/sync-viewed?task_id=${task.task_id}&viewed_at=${new Date().toISOString()}`,
      null,
      {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      }
    )
  } catch (error: any) {
    console.error('同步查收状态失败:', error)
    // 不影响用户操作，静默失败
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const downloadTemplateFile = (task: any) => {
  if (!task.template_file_url) {
    ElMessage.error('文件不存在')
    return
  }
  
  // 构建完整的下载URL
  const fileUrl = task.template_file_url.startsWith('http') 
    ? task.template_file_url 
    : `${getApiBaseUrl()}/${task.template_file_url}`
  
  // 创建临时链接并下载
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = task.template_name || '考评表'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success('文件下载开始')
}

const previewTemplateFile = (task: any) => {
  if (!task.template_file_url) {
    ElMessage.error('文件不存在')
    return
  }
  
  // 构建完整的预览URL
  const fileUrl = task.template_file_url.startsWith('http') 
    ? task.template_file_url 
    : `${getApiBaseUrl()}/${task.template_file_url}`
  
  // 在新标签页打开预览
  window.open(fileUrl, '_blank')
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.evaluation-form-view {
  width: 100%;
  position: relative;
  z-index: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  position: relative;
  z-index: auto;
}

.page-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #003366;
}

.task-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: auto;
}

/* 确保表格中的按钮可以点击 */
.el-table__body-wrapper {
  position: relative;
  z-index: auto;
}

.el-table__fixed-right {
  position: relative;
  z-index: 10;
}

.el-table__fixed-right::before {
  display: none;
}

/* 确保按钮可以点击 */
.el-button {
  position: relative;
  z-index: auto;
  pointer-events: auto;
  cursor: pointer;
}

.el-button:hover {
  pointer-events: auto;
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

.template-file-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.template-file-section h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #212121;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.file-name {
  flex: 1;
  color: #212121;
  font-size: 0.95rem;
}

.files-section {
  margin-top: 1.5rem;
}

.files-section h4 {
  margin-bottom: 1rem;
  color: #212121;
}
</style>
