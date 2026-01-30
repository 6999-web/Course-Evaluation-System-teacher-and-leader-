<template>
  <div class="evaluation-form-upload">
    <div class="upload-container">
      <h2 class="page-title">上传考评表</h2>
      
      <!-- 已上传的考评表列表 -->
      <el-card class="templates-list-card" v-if="uploadedTemplates.length > 0">
        <template #header>
          <div class="card-header">
            <span>已上传的考评表</span>
            <el-button link @click="loadUploadedTemplates">刷新</el-button>
          </div>
        </template>
        
        <el-table :data="uploadedTemplates" stripe>
          <el-table-column prop="template_id" label="ID" width="150" />
          <el-table-column prop="name" label="名称" min-width="150" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'published' ? 'success' : 'info'">
                {{ row.status === 'published' ? '已分配' : '待分配' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="target_count" label="分配教师数" width="120" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button 
                v-if="row.status !== 'published'" 
                link 
                type="primary" 
                @click="openDistributeDialog(row)"
              >
                分配
              </el-button>
              <el-button link type="primary" @click="viewTemplateDetail(row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <el-card class="upload-card">
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          
          <el-form :model="form" label-width="120px" class="form-content">
            <el-form-item label="考评表名称">
              <el-input 
                v-model="form.name" 
                placeholder="例如：2026年度教学评估"
                clearable
              />
            </el-form-item>
            
            <el-form-item label="考评表描述">
              <el-input 
                v-model="form.description" 
                type="textarea"
                placeholder="例如：教学质量评估考评表"
                :rows="3"
                clearable
              />
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 文件上传 -->
        <div class="form-section">
          <h3 class="section-title">选择文件</h3>
          
          <el-upload
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileSelect"
            accept=".pdf,.xlsx,.xls,.docx,.doc"
            class="upload-area"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此或 <em>点击选择</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 PDF、Excel、Word 格式，单个文件不超过 50MB
              </div>
            </template>
          </el-upload>
          
          <div v-if="selectedFile" class="file-info">
            <el-icon><document /></el-icon>
            <span>{{ selectedFile.name }}</span>
            <el-button link type="danger" @click="selectedFile = null">删除</el-button>
          </div>
        </div>
        
        <!-- 评分标准 -->
        <div class="form-section">
          <h3 class="section-title">评分标准</h3>
          
          <div class="criteria-list">
            <div v-for="(criterion, index) in form.scoringCriteria" :key="index" class="criterion-item">
              <el-input 
                v-model="criterion.name" 
                placeholder="评分项名称"
                class="criterion-name"
              />
              <el-input-number 
                v-model="criterion.max_score" 
                :min="1"
                :max="100"
                class="criterion-score"
              />
              <span class="criterion-unit">分</span>
              <el-button link type="danger" @click="removeCriterion(index)">删除</el-button>
            </div>
          </div>
          
          <el-button @click="addCriterion" type="primary" plain>
            <el-icon><plus /></el-icon>
            添加评分项
          </el-button>
          
          <div class="total-score">
            <span>总分：</span>
            <strong>{{ calculateTotalScore() }}</strong>
            <span>分</span>
          </div>
        </div>
        
        <!-- 提交要求 -->
        <div class="form-section">
          <h3 class="section-title">提交要求</h3>
          
          <el-form :model="form" label-width="120px" class="form-content">
            <el-form-item label="允许文件类型">
              <el-checkbox-group v-model="form.submissionRequirements.file_types">
                <el-checkbox :label="'pdf'">PDF</el-checkbox>
                <el-checkbox :label="'excel'">Excel</el-checkbox>
                <el-checkbox :label="'word'">Word</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="最多上传文件数">
              <el-input-number 
                v-model="form.submissionRequirements.max_files" 
                :min="1"
                :max="10"
              />
            </el-form-item>
            
            <el-form-item label="提交说明">
              <el-input 
                v-model="form.submissionRequirements.description" 
                type="textarea"
                placeholder="请输入提交说明"
                :rows="2"
              />
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 截止时间 -->
        <div class="form-section">
          <h3 class="section-title">截止时间</h3>
          
          <el-form :model="form" label-width="120px" class="form-content">
            <el-form-item label="截止天数">
              <el-input-number 
                v-model="form.deadline_days" 
                :min="1"
                :max="365"
              />
              <span class="deadline-hint">天后截止</span>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button type="primary" @click="submitForm" :loading="loading">
            <el-icon><upload-filled /></el-icon>
            上传考评表
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </div>
      </el-card>
    </div>
    
    <!-- 分配对话框 -->
    <el-dialog v-model="distributeDialogVisible" title="分配考评表" width="600px">
      <div v-if="currentTemplate" class="distribute-dialog">
        <div class="template-info">
          <p><strong>考评表：</strong> {{ currentTemplate.name }}</p>
          <p><strong>总分：</strong> {{ currentTemplate.total_score }}</p>
          <p><strong>截止时间：</strong> {{ currentTemplate.deadline }}</p>
        </div>
        
        <div class="distribution-type">
          <label>分配方式</label>
          <el-radio-group v-model="distributionType">
            <el-radio :label="'targeted'">指定教师</el-radio>
            <el-radio :label="'batch'">全部教师</el-radio>
          </el-radio-group>
        </div>
        
        <div v-if="distributionType === 'targeted'" class="teacher-selection">
          <label>选择教师</label>
          <el-select 
            v-model="selectedTeachers" 
            multiple 
            placeholder="选择要分配的教师"
            style="width: 100%"
          >
            <el-option 
              v-for="teacher in allTeachers" 
              :key="teacher.teacher_id" 
              :label="`${teacher.teacher_name} (${teacher.teacher_id})`" 
              :value="teacher.teacher_id"
            />
          </el-select>
          <div class="selected-count">
            已选择 {{ selectedTeachers.length }} 个教师
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="distributeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="distributeTemplate" :loading="loading">
          确认分配
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="考评表详情" width="700px">
      <div v-if="currentTemplate" class="detail-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentTemplate.template_id }}</el-descriptions-item>
          <el-descriptions-item label="名称">{{ currentTemplate.name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ currentTemplate.description }}</el-descriptions-item>
          <el-descriptions-item label="总分">{{ currentTemplate.total_score }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentTemplate.status === 'published' ? 'success' : 'info'">
              {{ currentTemplate.status === 'published' ? '已分配' : '待分配' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分配教师数">{{ currentTemplate.target_count }}</el-descriptions-item>
          <el-descriptions-item label="截止时间">{{ currentTemplate.deadline }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTemplate.created_at }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentTemplate.scoring_criteria" class="criteria-section">
          <h4>评分标准</h4>
          <el-table :data="currentTemplate.scoring_criteria" stripe>
            <el-table-column prop="name" label="评分项" />
            <el-table-column prop="max_score" label="最高分" width="100" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Plus, Document } from '@element-plus/icons-vue'
import axios from 'axios'

const form = ref({
  name: '',
  description: '',
  scoringCriteria: [{ name: '完成度', max_score: 10 }],
  submissionRequirements: {
    file_types: ['pdf', 'excel', 'word'],
    max_files: 3,
    description: '请上传考评相关文件'
  },
  deadline_days: 7
})

const selectedFile = ref<File | null>(null)
const loading = ref(false)
const uploadedTemplates = ref<any[]>([])
const distributeDialogVisible = ref(false)
const currentTemplate = ref<any>(null)
const distributionType = ref('targeted')
const selectedTeachers = ref<string[]>([])
const allTeachers = ref<any[]>([])
const detailDialogVisible = ref(false)

const handleFileSelect = (file: any) => {
  selectedFile.value = file.raw
}

const addCriterion = () => {
  form.value.scoringCriteria.push({ name: '', max_score: 10 })
}

const removeCriterion = (index: number) => {
  form.value.scoringCriteria.splice(index, 1)
}

const calculateTotalScore = () => {
  return form.value.scoringCriteria.reduce((sum, c) => sum + c.max_score, 0)
}

const submitForm = async () => {
  if (!form.value.name.trim()) {
    ElMessage.error('请输入考评表名称')
    return
  }

  if (!selectedFile.value) {
    ElMessage.error('请选择文件')
    return
  }

  if (form.value.scoringCriteria.length === 0) {
    ElMessage.error('请至少添加一个评分项')
    return
  }

  loading.value = true

  try {
    // 构建FormData，只包含文件
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    // 构建Query参数
    const params = new URLSearchParams()
    params.append('name', form.value.name)
    params.append('description', form.value.description)
    params.append('scoring_criteria', JSON.stringify(form.value.scoringCriteria))
    params.append('total_score', String(calculateTotalScore()))
    params.append('submission_requirements', JSON.stringify(form.value.submissionRequirements))
    params.append('deadline_days', String(form.value.deadline_days))

    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    const response = await axios.post(
      `http://localhost:8001/api/evaluation-templates/upload?${params.toString()}`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    ElMessage.success(`上传成功！考评表ID: ${response.data.template_id}`)
    resetForm()
    loadUploadedTemplates()
  } catch (error: any) {
    console.error('上传错误:', error)
    const errorMsg = error.response?.data?.detail || error.message || '上传失败'
    ElMessage.error(`上传失败: ${errorMsg}`)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    description: '',
    scoringCriteria: [{ name: '完成度', max_score: 10 }],
    submissionRequirements: {
      file_types: ['pdf', 'excel', 'word'],
      max_files: 3,
      description: '请上传考评相关文件'
    },
    deadline_days: 7
  }
  selectedFile.value = null
}

const loadUploadedTemplates = async () => {
  try {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    const response = await axios.get(
      'http://localhost:8001/api/evaluation-templates',
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    uploadedTemplates.value = response.data.templates || []
  } catch (error: any) {
    console.error('加载考评表失败:', error)
  }
}

const openDistributeDialog = async (template: any) => {
  currentTemplate.value = template
  distributionType.value = 'targeted'
  selectedTeachers.value = []
  
  // 加载所有教师
  try {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    const response = await axios.get(
      'http://localhost:8001/api/teachers',
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    allTeachers.value = response.data.teachers || []
  } catch (error: any) {
    console.error('加载教师列表失败:', error)
    ElMessage.error('加载教师列表失败')
  }
  
  distributeDialogVisible.value = true
}

const distributeTemplate = async () => {
  if (distributionType.value === 'targeted' && selectedTeachers.value.length === 0) {
    ElMessage.error('请选择至少一个教师')
    return
  }

  loading.value = true
  try {
    // 构建URL参数
    const params = new URLSearchParams()
    params.append('distribution_type', distributionType.value)
    
    // 只在指定分配时添加教师ID
    if (distributionType.value === 'targeted') {
      selectedTeachers.value.forEach(id => params.append('target_teachers', id))
    }

    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    const response = await axios.post(
      `http://localhost:8001/api/evaluation-templates/${currentTemplate.value.template_id}/distribute?${params.toString()}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    ElMessage.success('分配成功')
    distributeDialogVisible.value = false
    loadUploadedTemplates()
  } catch (error: any) {
    console.error('分配错误:', error)
    const errorMsg = error.response?.data?.detail || error.message || '分配失败'
    ElMessage.error(`分配失败: ${errorMsg}`)
  } finally {
    loading.value = false
  }
}

const viewTemplateDetail = (template: any) => {
  currentTemplate.value = template
  detailDialogVisible.value = true
}

onMounted(() => {
  loadUploadedTemplates()
})
</script>

<style scoped>
.evaluation-form-upload {
  width: 100%;
  padding: 0;
}

.upload-container {
  width: 100%;
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

.upload-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #f0f0f0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #212121;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 1rem;
  background-color: #ff3b30;
  border-radius: 2px;
}

.form-content {
  margin-bottom: 1rem;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #40a9ff;
  background-color: #fafafa;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-top: 1rem;
}

.file-info span {
  flex: 1;
  color: #212121;
  font-size: 0.9rem;
}

.criteria-list {
  margin-bottom: 1rem;
}

.criterion-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.criterion-name {
  flex: 1;
  min-width: 150px;
}

.criterion-score {
  width: 120px;
}

.criterion-unit {
  color: #757575;
  font-size: 0.9rem;
}

.total-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-top: 1rem;
  font-size: 0.95rem;
}

.total-score strong {
  color: #ff3b30;
  font-size: 1.1rem;
}

.deadline-hint {
  margin-left: 0.5rem;
  color: #757575;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #f0f0f0;
}

.form-actions button {
  min-width: 120px;
}

.templates-list-card {
  margin-bottom: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.distribute-dialog {
  padding: 1rem 0;
}

.template-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.template-info p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

.distribution-type {
  margin-bottom: 1.5rem;
}

.distribution-type label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.teacher-selection {
  margin-bottom: 1rem;
}

.teacher-selection label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.selected-count {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #757575;
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
</style>
