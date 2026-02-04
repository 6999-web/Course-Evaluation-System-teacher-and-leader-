<template>
  <div class="review-manager">
    <h2 class="page-title">复核管理</h2>
    
    <el-tabs v-model="activeTab" class="review-tabs">
      <!-- 异议列表标签页 -->
      <el-tab-pane label="异议列表" name="appeals">
        <el-card class="review-card">
          <!-- 筛选条件 -->
          <div class="filters-section">
            <el-form :model="filters" label-width="100px" class="filters-form">
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="6">
                  <el-form-item label="异议状态">
                    <el-select v-model="filters.status" placeholder="所有状态" clearable>
                      <el-option label="待处理" value="pending" />
                      <el-option label="处理中" value="reviewing" />
                      <el-option label="已解决" value="resolved" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                  <el-button type="primary" @click="loadAppeals" :loading="loading">
                    <el-icon><search /></el-icon>
                    查询
                  </el-button>
                  <el-button @click="resetFilters">重置</el-button>
                </el-col>
              </el-row>
            </el-form>
          </div>
          
          <!-- 异议列表 -->
          <el-table :data="appeals" stripe :loading="loading" class="appeals-table">
            <el-table-column prop="id" label="异议ID" width="100" />
            <el-table-column prop="teacher_name" label="教师" width="120" />
            <el-table-column prop="appeal_reason" label="异议理由" min-width="250">
              <template #default="{ row }">
                <el-tooltip :content="row.appeal_reason" placement="top">
                  <span class="truncate-text">{{ row.appeal_reason }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="openReviewDialog(row)">
                  <el-icon><edit /></el-icon>
                  复核
                </el-button>
                <el-button link type="info" size="small" @click="viewDetail(row)">
                  <el-icon><view /></el-icon>
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <!-- 随机抽查标签页 -->
      <el-tab-pane label="随机抽查" name="sampling">
        <el-card class="review-card">
          <div class="sampling-section">
            <el-form :model="samplingOptions" label-width="120px">
              <el-form-item label="抽查比例">
                <el-input-number 
                  v-model="samplingOptions.sampleRate" 
                  :min="0.01" 
                  :max="1" 
                  :step="0.05"
                  :precision="2"
                />
                <span class="form-hint">（0.01-1.00）</span>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="executeSampling" :loading="samplingLoading">
                  <el-icon><refresh /></el-icon>
                  执行抽查
                </el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <!-- 抽查结果 -->
          <div v-if="sampledRecords.length > 0" class="sampling-results">
            <h4>抽查结果 ({{ sampledRecords.length }} 项)</h4>
            <el-table :data="sampledRecords" stripe>
              <el-table-column prop="id" label="记录ID" width="100" />
              <el-table-column prop="submission_id" label="提交ID" width="150" />
              <el-table-column prop="file_name" label="文件名" min-width="200" />
              <el-table-column prop="final_score" label="得分" width="100" />
              <el-table-column prop="grade" label="等级" width="100">
                <template #default="{ row }">
                  <el-tag :type="getGradeType(row.grade)">
                    {{ row.grade }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <el-button link type="primary" size="small" @click="openSamplingReviewDialog(row)">
                  <el-icon><edit /></el-icon>
                  复核
                </el-button>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 一致性统计标签页 -->
      <el-tab-pane label="一致性统计" name="consistency">
        <el-card class="review-card">
          <div class="consistency-section">
            <el-form :model="consistencyFilters" label-width="120px">
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="6">
                  <el-form-item label="开始日期">
                    <el-date-picker 
                      v-model="consistencyFilters.startDate" 
                      type="date"
                      placeholder="选择开始日期"
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                  <el-form-item label="结束日期">
                    <el-date-picker 
                      v-model="consistencyFilters.endDate" 
                      type="date"
                      placeholder="选择结束日期"
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                  <el-button type="primary" @click="loadConsistency" :loading="consistencyLoading">
                    <el-icon><search /></el-icon>
                    查询
                  </el-button>
                </el-col>
              </el-row>
            </el-form>
          </div>
          
          <!-- 一致性统计结果 -->
          <div v-if="consistencyData" class="consistency-results">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">总复核数</div>
                  <div class="stat-value">{{ consistencyData.total_reviews }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">一致数</div>
                  <div class="stat-value">{{ consistencyData.consistent_count }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">一致性比例</div>
                  <div class="stat-value" :style="{ color: getConsistencyColor(consistencyData.consistency_rate) }">
                    {{ (consistencyData.consistency_rate * 100).toFixed(2) }}%
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <!-- 差异原因分布 -->
            <div v-if="Object.keys(consistencyData.difference_reasons).length > 0" class="difference-reasons">
              <h4>差异原因分布</h4>
              <el-table :data="differenceReasonsList" stripe>
                <el-table-column prop="reason" label="差异原因" min-width="200" />
                <el-table-column prop="count" label="数量" width="100" />
                <el-table-column prop="percentage" label="占比" width="100">
                  <template #default="{ row }">
                    {{ row.percentage }}%
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 公示管理标签页 -->
      <el-tab-pane label="公示管理" name="publish">
        <el-card class="review-card">
          <div class="publish-section">
            <el-alert
              title="公示说明"
              type="info"
              description="只有当所有教师都确认评分结果后，才能进行公示。公示后，评分结果将对所有人可见。"
              :closable="false"
              show-icon
              class="publish-alert"
            />
            
            <el-form :model="publishOptions" label-width="120px" class="publish-form">
              <el-form-item label="选择任务">
                <el-select v-model="publishOptions.taskId" placeholder="选择要公示的任务">
                  <el-option label="任务1" value="task_1" />
                  <el-option label="任务2" value="task_2" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="publishResults" :loading="publishLoading">
                  <el-icon><check /></el-icon>
                  公示结果
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 复核对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="人工复核" width="700px" @close="resetReviewData">
      <div v-if="currentAppeal" class="review-dialog">
        <div class="appeal-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="异议ID">{{ currentAppeal.id }}</el-descriptions-item>
            <el-descriptions-item label="教师">{{ currentAppeal.teacher_name }}</el-descriptions-item>
            <el-descriptions-item label="异议理由" :span="2">
              {{ currentAppeal.appeal_reason }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="review-form">
          <h4>复核结果</h4>
          <el-form :model="reviewData" label-width="100px">
            <el-form-item label="新得分">
              <el-input-number 
                v-model.number="reviewData.newScore" 
                :min="0"
                :max="100"
                :precision="1"
                :step="0.5"
              />
            </el-form-item>
            <el-form-item label="新等级">
              <el-select v-model="reviewData.newGrade" placeholder="选择等级">
                <el-option label="优秀" value="优秀" />
                <el-option label="良好" value="良好" />
                <el-option label="合格" value="合格" />
                <el-option label="不合格" value="不合格" />
              </el-select>
            </el-form-item>
            <el-form-item label="复核理由">
              <el-input 
                v-model="reviewData.reviewReason" 
                type="textarea"
                :rows="4"
                placeholder="请输入复核理由"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitReview" :loading="reviewLoading">
            <el-icon><check /></el-icon>
            提交复核
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="异议详情" width="600px">
      <div v-if="currentAppeal" class="detail-dialog">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="异议ID">{{ currentAppeal.id }}</el-descriptions-item>
          <el-descriptions-item label="教师">{{ currentAppeal.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="异议理由">{{ currentAppeal.appeal_reason }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentAppeal.status)">
              {{ getStatusText(currentAppeal.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ formatDate(currentAppeal.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="复核时间">{{ formatDate(currentAppeal.reviewed_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Edit, View, Refresh, Check } from '@element-plus/icons-vue'
import axios from 'axios'
import { waitForAuth } from '../utils/authState'

const activeTab = ref('appeals')
const appeals = ref<any[]>([])
const sampledRecords = ref<any[]>([])
const loading = ref(false)
const samplingLoading = ref(false)
const consistencyLoading = ref(false)
const reviewLoading = ref(false)
const publishLoading = ref(false)

const filters = ref({
  status: ''
})

const samplingOptions = ref({
  sampleRate: 0.1
})

const consistencyFilters = ref({
  startDate: null,
  endDate: null
})

const publishOptions = ref({
  taskId: ''
})

const reviewDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentAppeal = ref<any>(null)

const reviewData = ref({
  newScore: 0,
  newGrade: '',
  reviewReason: ''
})

const consistencyData = ref<any>(null)

const differenceReasonsList = computed(() => {
  if (!consistencyData.value || !consistencyData.value.difference_reasons) {
    return []
  }
  
  const total = consistencyData.value.total_reviews
  return Object.entries(consistencyData.value.difference_reasons).map(([reason, count]: [string, any]) => ({
    reason,
    count,
    percentage: ((count / total) * 100).toFixed(2)
  }))
})

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    reviewing: '处理中',
    resolved: '已解决'
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    reviewing: 'info',
    resolved: 'success'
  }
  return typeMap[status] || 'info'
}

const getGradeType = (grade: string) => {
  const typeMap: Record<string, string> = {
    '优秀': 'success',
    '良好': 'primary',
    '合格': 'warning',
    '不合格': 'danger'
  }
  return typeMap[grade] || 'info'
}

const getConsistencyColor = (rate: number) => {
  if (rate >= 0.95) return '#67c23a'
  if (rate >= 0.90) return '#409eff'
  if (rate >= 0.80) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const loadAppeals = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8001/api/scoring/appeals', {
      params: filters.value,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    appeals.value = response.data.appeals || []
  } catch (error: any) {
    console.error('加载异议列表失败:', error)
    ElMessage.error(`加载异议列表失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = { status: '' }
  loadAppeals()
}

const openReviewDialog = (appeal: any) => {
  currentAppeal.value = appeal
  reviewData.value = {
    newScore: 0,
    newGrade: '',
    reviewReason: ''
  }
  reviewDialogVisible.value = true
}

const submitReview = async () => {
  if (!currentAppeal.value) return
  
  reviewLoading.value = true
  try {
    await axios.post(
      'http://localhost:8001/api/scoring/manual-review',
      {
        scoring_record_id: currentAppeal.value.scoring_record_id,
        new_score: {
          base_score: reviewData.value.newScore,
          final_score: reviewData.value.newScore,
          grade: reviewData.value.newGrade,
          review_reason: reviewData.value.reviewReason
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    ElMessage.success('复核提交成功')
    reviewDialogVisible.value = false
    loadAppeals()
  } catch (error: any) {
    console.error('提交复核失败:', error)
    ElMessage.error(`提交复核失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    reviewLoading.value = false
  }
}

const resetReviewData = () => {
  reviewData.value = {
    newScore: 0,
    newGrade: '',
    reviewReason: ''
  }
}

const viewDetail = (appeal: any) => {
  currentAppeal.value = appeal
  detailDialogVisible.value = true
}

const executeSampling = async () => {
  samplingLoading.value = true
  try {
    const response = await axios.post(
      'http://localhost:8001/api/scoring/random-sample',
      {
        task_id: 'all',
        sample_rate: samplingOptions.value.sampleRate
      },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    sampledRecords.value = response.data.sampled_records || []
    ElMessage.success(`抽查完成: 共抽取 ${sampledRecords.value.length} 项`)
  } catch (error: any) {
    console.error('执行抽查失败:', error)
    ElMessage.error(`执行抽查失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    samplingLoading.value = false
  }
}

const openSamplingReviewDialog = (record: any) => {
  currentAppeal.value = {
    id: record.id,
    teacher_name: '教师',
    appeal_reason: `对评分 ${record.final_score} 分进行复核`,
    scoring_record_id: record.id
  }
  reviewData.value = {
    newScore: record.final_score,
    newGrade: record.grade,
    reviewReason: ''
  }
  reviewDialogVisible.value = true
}

const loadConsistency = async () => {
  consistencyLoading.value = true
  try {
    const params: any = {}
    if (consistencyFilters.value.startDate) {
      params.start_date = consistencyFilters.value.startDate.toISOString().split('T')[0]
    }
    if (consistencyFilters.value.endDate) {
      params.end_date = consistencyFilters.value.endDate.toISOString().split('T')[0]
    }
    
    const response = await axios.get('http://localhost:8001/api/scoring/consistency', {
      params,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`
      }
    })
    
    consistencyData.value = response.data
  } catch (error: any) {
    console.error('加载一致性统计失败:', error)
    ElMessage.error(`加载一致性统计失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    consistencyLoading.value = false
  }
}

const publishResults = async () => {
  if (!publishOptions.value.taskId) {
    ElMessage.warning('请选择要公示的任务')
    return
  }
  
  publishLoading.value = true
  try {
    await axios.post(
      `http://localhost:8001/api/scoring/publish/${publishOptions.value.taskId}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || sessionStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }
    )
    
    ElMessage.success('评分结果公示成功')
  } catch (error: any) {
    console.error('公示失败:', error)
    ElMessage.error(`公示失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    publishLoading.value = false
  }
}

onMounted(async () => {
  await waitForAuth()
  loadAppeals()
})
</script>

<style scoped>
.review-manager {
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

.review-tabs {
  margin-bottom: 1.5rem;
}

.review-card {
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

.appeals-table {
  margin-bottom: 1.5rem;
}

.truncate-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sampling-section {
  padding: 1.5rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.form-hint {
  margin-left: 0.5rem;
  color: #757575;
  font-size: 0.85rem;
}

.sampling-results {
  margin-top: 1.5rem;
}

.sampling-results h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.consistency-section {
  padding: 1.5rem;
  background-color: #f6f8fb;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.consistency-results {
  margin-top: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  text-align: center;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
}

.difference-reasons {
  margin-top: 2rem;
}

.difference-reasons h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.publish-section {
  padding: 1.5rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.publish-alert {
  margin-bottom: 1.5rem;
}

.publish-form {
  margin-top: 1.5rem;
}

.review-dialog {
  padding: 1rem 0;
}

.appeal-info {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f6f8fb;
  border-radius: 4px;
}

.review-form {
  margin-top: 1.5rem;
}

.review-form h4 {
  margin-bottom: 1rem;
  color: #212121;
  font-weight: 600;
}

.detail-dialog {
  padding: 1rem 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
