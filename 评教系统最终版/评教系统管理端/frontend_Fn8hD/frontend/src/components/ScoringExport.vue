<template>
  <div class="scoring-export">
    <h2 class="page-title">评分结果导出</h2>
    
    <el-card class="export-card">
      <!-- 筛选条件 -->
      <div class="filters-section">
        <el-form :model="filters" label-width="120px" class="filters-form">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="文件类型">
                <el-select v-model="filters.fileType" placeholder="所有类型" clearable>
                  <el-option label="教案" value="教案" />
                  <el-option label="教学反思" value="教学反思" />
                  <el-option label="教研/听课记录" value="教研/听课记录" />
                  <el-option label="成绩/学情分析" value="成绩/学情分析" />
                  <el-option label="课件" value="课件" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="等级">
                <el-select v-model="filters.grade" placeholder="所有等级" clearable>
                  <el-option label="优秀" value="优秀" />
                  <el-option label="良好" value="良好" />
                  <el-option label="合格" value="合格" />
                  <el-option label="不合格" value="不合格" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="开始日期">
                <el-date-picker 
                  v-model="filters.startDate" 
                  type="date"
                  placeholder="选择开始日期"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="结束日期">
                <el-date-picker 
                  v-model="filters.endDate" 
                  type="date"
                  placeholder="选择结束日期"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="primary" @click="loadData" :loading="loading">
                <el-icon><search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetFilters">重置</el-button>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="success" @click="exportToExcel" :loading="exporting" :disabled="exportData.length === 0">
                <el-icon><download /></el-icon>
                导出Excel
              </el-button>
            </el-col>
          </el-row>
        </el-form>
      </div>
      
      <!-- 数据预览 -->
      <div class="preview-section">
        <h4>导出数据预览 ({{ exportData.length }} 条)</h4>
        <el-table :data="exportData" stripe :loading="loading" max-height="500">
          <el-table-column prop="submission_id" label="提交ID" width="150" />
          <el-table-column prop="file_name" label="文件名" min-width="200" />
          <el-table-column prop="file_type" label="文件类型" width="120" />
          <el-table-column prop="base_score" label="基础分" width="100" />
          <el-table-column prop="bonus_score" label="加分" width="100" />
          <el-table-column prop="final_score" label="最终得分" width="100" />
          <el-table-column prop="grade" label="等级" width="100">
            <template #default="{ row }">
              <el-tag :type="getGradeType(row.grade)">
                {{ row.grade }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="scoring_type" label="评分类型" width="100">
            <template #default="{ row }">
              <el-tag :type="row.scoring_type === 'auto' ? 'info' : 'warning'">
                {{ row.scoring_type === 'auto' ? '自动' : '手动' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="scored_at" label="评分时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.scored_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="is_confirmed" label="已确认" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_confirmed ? 'success' : 'info'">
                {{ row.is_confirmed ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 导出统计 -->
      <div v-if="exportData.length > 0" class="export-stats">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <div class="stat-item">
              <span class="stat-label">总数</span>
              <span class="stat-value">{{ exportData.length }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="stat-item">
              <span class="stat-label">平均分</span>
              <span class="stat-value">{{ averageScore.toFixed(2) }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="stat-item">
              <span class="stat-label">最高分</span>
              <span class="stat-value">{{ maxScore }}</span>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="stat-item">
              <span class="stat-label">最低分</span>
              <span class="stat-value">{{ minScore }}</span>
            </div>
          </el-col>
        </el-row>
        
        <!-- 等级分布 -->
        <div class="grade-distribution">
          <h4>等级分布</h4>
          <el-row :gutter="20">
            <el-col v-for="(count, grade) in gradeDistribution" :key="grade" :xs="24" :sm="12" :md="6">
              <div class="grade-stat">
                <span class="grade-name">{{ grade }}</span>
                <span class="grade-count">{{ count }} 人</span>
                <span class="grade-percentage">({{ ((count / exportData.length) * 100).toFixed(1) }}%)</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
import { waitForAuth } from '../utils/authState'

const filters = ref({
  fileType: '',
  grade: '',
  startDate: null,
  endDate: null
})

const exportData = ref<any[]>([])
const loading = ref(false)
const exporting = ref(false)

const getGradeType = (grade: string) => {
  const typeMap: Record<string, string> = {
    '优秀': 'success',
    '良好': 'primary',
    '合格': 'warning',
    '不合格': 'danger'
  }
  return typeMap[grade] || 'info'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const averageScore = computed(() => {
  if (exportData.value.length === 0) return 0
  const sum = exportData.value.reduce((acc, item) => acc + (item.final_score || 0), 0)
  return sum / exportData.value.length
})

const maxScore = computed(() => {
  if (exportData.value.length === 0) return 0
  return Math.max(...exportData.value.map(item => item.final_score || 0))
})

const minScore = computed(() => {
  if (exportData.value.length === 0) return 0
  return Math.min(...exportData.value.map(item => item.final_score || 0))
})

const gradeDistribution = computed(() => {
  const distribution: Record<string, number> = {
    '优秀': 0,
    '良好': 0,
    '合格': 0,
    '不合格': 0
  }
  
  exportData.value.forEach(item => {
    if (distribution[item.grade] !== undefined) {
      distribution[item.grade]++
    }
  })
  
  return distribution
})

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {}
    
    if (filters.value.fileType) {
      params.file_type = filters.value.fileType
    }
    if (filters.value.grade) {
      params.grade = filters.value.grade
    }
    if (filters.value.startDate) {
      params.start_date = filters.value.startDate.toISOString().split('T')[0]
    }
    if (filters.value.endDate) {
      params.end_date = filters.value.endDate.toISOString().split('T')[0]
    }
    
    const response = await axios.get('http://localhost:8001/api/scoring/export', {
      params,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    exportData.value = response.data.data || []
    ElMessage.success(`加载成功: ${exportData.value.length} 条数据`)
  } catch (error: any) {
    console.error('加载数据失败:', error)
    ElMessage.error(`加载数据失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    fileType: '',
    grade: '',
    startDate: null,
    endDate: null
  }
  exportData.value = []
}

const exportToExcel = async () => {
  if (exportData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  exporting.value = true
  try {
    // 创建工作簿数据
    const headers = [
      '提交ID',
      '文件名',
      '文件类型',
      '基础分',
      '加分',
      '最终得分',
      '等级',
      '评分类型',
      '评分时间',
      '已确认'
    ]
    
    const rows = exportData.value.map(item => [
      item.submission_id,
      item.file_name,
      item.file_type,
      item.base_score,
      item.bonus_score,
      item.final_score,
      item.grade,
      item.scoring_type === 'auto' ? '自动' : '手动',
      formatDate(item.scored_at),
      item.is_confirmed ? '是' : '否'
    ])
    
    // 创建CSV内容
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    // 创建Blob并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `评分结果_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(`导出失败: ${error.message}`)
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  await waitForAuth()
})
</script>

<style scoped>
.scoring-export {
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

.export-card {
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

.preview-section {
  margin-bottom: 1.5rem;
}

.preview-section h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.export-stats {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.9rem;
  color: #757575;
  margin-bottom: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1976d2;
}

.grade-distribution {
  margin-top: 1.5rem;
}

.grade-distribution h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.grade-stat {
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.grade-name {
  display: block;
  font-weight: 600;
  color: #212121;
  margin-bottom: 0.25rem;
}

.grade-count {
  display: block;
  font-size: 1.2rem;
  font-weight: bold;
  color: #1976d2;
  margin-bottom: 0.25rem;
}

.grade-percentage {
  display: block;
  font-size: 0.85rem;
  color: #757575;
}
</style>
