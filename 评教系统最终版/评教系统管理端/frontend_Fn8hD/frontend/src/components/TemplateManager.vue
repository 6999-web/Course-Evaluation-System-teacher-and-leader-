<template>
  <div class="template-manager">
    <h2 class="page-title">提示词模板管理</h2>
    
    <el-card class="template-card">
      <!-- 操作按钮 -->
      <div class="action-bar">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><plus /></el-icon>
          新建模板
        </el-button>
        <el-button @click="loadTemplates" :loading="loading">
          <el-icon><refresh /></el-icon>
          刷新
        </el-button>
      </div>
      
      <!-- 模板列表 -->
      <el-table :data="templates" stripe :loading="loading" class="template-table">
        <el-table-column prop="file_type" label="文件类型" width="150" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">
              <el-icon><edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="danger" size="small" @click="deleteTemplate(row)">
              <el-icon><delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 编辑/创建对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEditMode ? '编辑模板' : '新建模板'" 
      width="900px"
      @close="resetForm"
    >
      <div class="template-form">
        <el-form :model="formData" label-width="150px" :rules="formRules" ref="formRef">
          <el-form-item label="文件类型" prop="file_type">
            <el-select v-model="formData.file_type" placeholder="选择文件类型" :disabled="isEditMode">
              <el-option label="教案" value="教案" />
              <el-option label="教学反思" value="教学反思" />
              <el-option label="教研/听课记录" value="教研/听课记录" />
              <el-option label="成绩/学情分析" value="成绩/学情分析" />
              <el-option label="课件" value="课件" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="模板内容" prop="template_content">
            <el-input 
              v-model="formData.template_content" 
              type="textarea"
              :rows="15"
              placeholder="输入模板内容（JSON格式）"
              class="template-textarea"
            />
          </el-form-item>
          
          <el-form-item label="启用状态">
            <el-switch v-model="formData.is_active" />
          </el-form-item>
          
          <!-- 模板预览 -->
          <el-form-item label="模板预览">
            <div class="template-preview">
              <el-alert
                v-if="templatePreviewError"
                :title="templatePreviewError"
                type="error"
                :closable="false"
                show-icon
              />
              <div v-else class="preview-content">
                <div v-if="parsedTemplate" class="preview-item">
                  <h4>等级标准</h4>
                  <div v-if="parsedTemplate.grade_standards" class="preview-section">
                    <div v-for="(grade, key) in parsedTemplate.grade_standards" :key="key" class="grade-item">
                      <span class="grade-name">{{ key }}:</span>
                      <span class="grade-range">{{ grade.min }}-{{ grade.max }}分</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="parsedTemplate" class="preview-item">
                  <h4>核心指标</h4>
                  <div v-if="parsedTemplate.core_indicators" class="preview-section">
                    <div v-for="(indicator, index) in parsedTemplate.core_indicators" :key="index" class="indicator-item">
                      <span class="indicator-name">{{ indicator.name }}</span>
                      <span class="indicator-weight">(权重: {{ indicator.weight }}%)</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="parsedTemplate" class="preview-item">
                  <h4>否决项</h4>
                  <div v-if="parsedTemplate.veto_items" class="preview-section">
                    <div v-if="parsedTemplate.veto_items.general" class="veto-group">
                      <span class="veto-label">通用否决项:</span>
                      <div v-for="(item, index) in parsedTemplate.veto_items.general" :key="index" class="veto-item">
                        {{ item }}
                      </div>
                    </div>
                    <div v-if="parsedTemplate.veto_items.specific" class="veto-group">
                      <span class="veto-label">专项否决项:</span>
                      <div v-for="(item, index) in parsedTemplate.veto_items.specific" :key="index" class="veto-item">
                        {{ item }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate" :loading="saveLoading">
            <el-icon><check /></el-icon>
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Refresh, Check } from '@element-plus/icons-vue'
import axios from 'axios'
import { waitForAuth } from '../utils/authState'

const templates = ref<any[]>([])
const loading = ref(false)
const saveLoading = ref(false)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref()

const formData = ref({
  file_type: '',
  template_content: '',
  is_active: true
})

const formRules = {
  file_type: [
    { required: true, message: '请选择文件类型', trigger: 'change' }
  ],
  template_content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' },
    { 
      validator: (rule: any, value: any, callback: any) => {
        if (!value) {
          callback()
          return
        }
        try {
          JSON.parse(value)
          callback()
        } catch (e) {
          callback(new Error('模板内容必须是有效的JSON格式'))
        }
      },
      trigger: 'blur'
    }
  ]
}

const templatePreviewError = computed(() => {
  try {
    if (formData.value.template_content) {
      JSON.parse(formData.value.template_content)
    }
    return ''
  } catch (e: any) {
    return `JSON格式错误: ${e.message}`
  }
})

const parsedTemplate = computed(() => {
  try {
    if (formData.value.template_content) {
      return JSON.parse(formData.value.template_content)
    }
    return null
  } catch (e) {
    return null
  }
})

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8001/api/scoring/templates', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    templates.value = response.data.templates || []
  } catch (error: any) {
    console.error('加载模板失败:', error)
    ElMessage.error(`加载模板失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEditMode.value = false
  formData.value = {
    file_type: '',
    template_content: '',
    is_active: true
  }
  dialogVisible.value = true
}

const openEditDialog = async (template: any) => {
  isEditMode.value = true
  try {
    const response = await axios.get(
      `http://localhost:8001/api/scoring/templates/${template.file_type}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
        }
      }
    )
    
    formData.value = {
      file_type: response.data.file_type,
      template_content: JSON.stringify(response.data.template_content, null, 2),
      is_active: response.data.is_active
    }
    dialogVisible.value = true
  } catch (error: any) {
    console.error('加载模板详情失败:', error)
    ElMessage.error(`加载模板详情失败: ${error.response?.data?.detail || error.message}`)
  }
}

const saveTemplate = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }
  
  saveLoading.value = true
  try {
    const templateContent = JSON.parse(formData.value.template_content)
    
    if (isEditMode.value) {
      // 更新模板
      await axios.put(
        `http://localhost:8001/api/scoring/templates/${formData.value.file_type}`,
        {
          file_type: formData.value.file_type,
          template_content: templateContent,
          is_active: formData.value.is_active
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        }
      )
      ElMessage.success('模板更新成功')
    } else {
      // 创建新模板
      await axios.post(
        'http://localhost:8001/api/scoring/templates',
        {
          file_type: formData.value.file_type,
          template_content: templateContent,
          is_active: formData.value.is_active
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        }
      )
      ElMessage.success('模板创建成功')
    }
    
    dialogVisible.value = false
    loadTemplates()
  } catch (error: any) {
    console.error('保存模板失败:', error)
    ElMessage.error(`保存模板失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    saveLoading.value = false
  }
}

const deleteTemplate = (template: any) => {
  ElMessageBox.confirm(
    `确定要删除模板 "${template.file_type}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.info('删除功能开发中...')
  }).catch(() => {
    // 用户取消
  })
}

const resetForm = () => {
  formData.value = {
    file_type: '',
    template_content: '',
    is_active: true
  }
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

onMounted(async () => {
  await waitForAuth()
  loadTemplates()
})
</script>

<style scoped>
.template-manager {
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

.template-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.action-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.template-table {
  margin-bottom: 1.5rem;
}

.template-form {
  padding: 1rem 0;
}

.template-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85rem;
}

.template-preview {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  max-height: 400px;
  overflow-y: auto;
}

.preview-content {
  padding: 0;
}

.preview-item {
  margin-bottom: 1.5rem;
}

.preview-item h4 {
  margin: 0 0 0.75rem 0;
  color: #212121;
  font-weight: 600;
  font-size: 0.95rem;
}

.preview-section {
  padding-left: 1rem;
}

.grade-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.grade-name {
  font-weight: 500;
  color: #424242;
  min-width: 60px;
}

.grade-range {
  color: #757575;
}

.indicator-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  padding: 0.5rem;
  background-color: #fff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.indicator-name {
  font-weight: 500;
  color: #212121;
  flex: 1;
}

.indicator-weight {
  color: #757575;
  font-size: 0.85rem;
}

.veto-group {
  margin-bottom: 1rem;
}

.veto-label {
  display: block;
  font-weight: 500;
  color: #424242;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.veto-item {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #f56c6c;
  color: #f56c6c;
  font-size: 0.85rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
