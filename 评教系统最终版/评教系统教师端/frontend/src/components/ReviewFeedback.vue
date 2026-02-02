<template>
  <div class="review-feedback-container">
    <!-- 搜索和筛选区域 -->
    <div class="search-filter">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索审核标题或内容"
        prefix-icon="Search"
        clearable
        size="default"
        class="search-input"
        @input="handleSearch"
      />
      
      <el-select
        v-model="statusFilter"
        placeholder="选择审核状态"
        size="default"
        class="filter-select"
        @change="handleFilter"
      >
        <el-option label="全部" value="" />
        <el-option label="待审核" :value="ReviewStatus.PENDING" />
        <el-option label="已通过" :value="ReviewStatus.APPROVED" />
        <el-option label="已拒绝" :value="ReviewStatus.REJECTED" />
        <el-option label="已修改" :value="ReviewStatus.REVISED" />
      </el-select>
      
      <el-select
        v-model="typeFilter"
        placeholder="选择审核类型"
        size="default"
        class="filter-select"
        @change="handleFilter"
      >
        <el-option label="全部" value="" />
        <el-option label="改进计划" :value="ReviewType.IMPROVEMENT" />
        <el-option label="申诉" :value="ReviewType.APPEAL" />
      </el-select>
      
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        size="default"
        class="date-picker"
        @change="handleDateFilter"
      />
      
      <el-button type="primary" size="default" class="refresh-btn" @click="refreshList">
        <el-icon name="Refresh" />
        刷新
      </el-button>
    </div>
    
    <!-- 审核反馈列表 -->
    <el-card shadow="hover" class="review-list-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">审核反馈列表</span>
          <div class="header-stats">
            <el-badge :value="stats.pending" type="warning" class="stat-badge">
              <span>待审核</span>
            </el-badge>
            <el-badge :value="stats.approved" type="success" class="stat-badge">
              <span>已通过</span>
            </el-badge>
            <el-badge :value="stats.rejected" type="danger" class="stat-badge">
              <span>已拒绝</span>
            </el-badge>
          </div>
        </div>
      </template>
      
      <el-table
        :data="reviewList"
        style="width: 100%"
        stripe
        border
        :row-class-name="tableRowClassName"
        @row-dblclick="handleRowDoubleClick"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="scope">
            <div class="review-title">{{ scope.row.title }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === ReviewType.IMPROVEMENT ? 'primary' : 'warning'">
              {{ scope.row.type === ReviewType.IMPROVEMENT ? '改进计划' : '申诉' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getStatusTagType(scope.row.status)"
              effect="dark"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="申请人" width="120" />
        <el-table-column prop="createTime" label="申请时间" width="180">
          <template #default="scope">
            <span>{{ formatDate(scope.row.createTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reviewer" label="审核人" width="120" />
        <el-table-column prop="reviewTime" label="审核时间" width="180">
          <template #default="scope">
            <span>{{ formatDate(scope.row.reviewTime) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon name="Document" />
              详情
            </el-button>
            <el-button
              v-if="scope.row.status === ReviewStatus.PENDING"
              type="success"
              size="small"
              @click="handleReview(scope.row)"
            >
              <el-icon name="Check" />
              审核
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 审核反馈详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="`审核反馈详情 - ${detailData?.title}`"
      width="800px"
      class="review-detail-dialog"
    >
      <div v-if="detailData" class="review-detail">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="审核ID">{{ detailData.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ detailData.title }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="detailData.type === ReviewType.IMPROVEMENT ? 'primary' : 'warning'">
              {{ detailData.type === ReviewType.IMPROVEMENT ? '改进计划' : '申诉' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="getStatusTagType(detailData.status)"
              effect="dark"
            >
              {{ getStatusText(detailData.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申请人">{{ detailData.creator }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ formatDate(detailData.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="审核人">{{ detailData.reviewer }}</el-descriptions-item>
          <el-descriptions-item label="审核时间">{{ formatDate(detailData.reviewTime) }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-section">
          <h4>审核内容</h4>
          <div class="content-box">{{ detailData.content }}</div>
        </div>
        
        <div v-if="detailData.feedback" class="detail-section">
          <h4>审核意见</h4>
          <div class="feedback-box">{{ detailData.feedback }}</div>
        </div>
        
        <div v-if="detailData.attachments && detailData.attachments.length > 0" class="detail-section">
          <h4>附件</h4>
          <div class="attachments-list">
            <el-link
              v-for="(attachment, index) in detailData.attachments"
              :key="index"
              :href="attachment"
              target="_blank"
              type="primary"
              class="attachment-item"
            >
              <el-icon name="Document" />
              附件 {{ index + 1 }}
            </el-link>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button
            v-if="detailData?.status === ReviewStatus.PENDING"
            type="primary"
            @click="handleReview(detailData)"
          >
            进行审核
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 审核操作对话框 -->
    <el-dialog
      v-model="reviewVisible"
      title="审核操作"
      width="700px"
      class="review-operation-dialog"
    >
      <el-form
        ref="reviewFormRef"
        :model="reviewForm"
        :rules="reviewFormRules"
        label-width="100px"
        label-position="left"
        size="default"
      >
        <el-form-item label="审核标题" prop="title">
          <el-input v-model="reviewForm.title" readonly />
        </el-form-item>
        
        <el-form-item label="审核类型" prop="type">
          <el-select v-model="reviewForm.type" disabled>
            <el-option label="改进计划" :value="ReviewType.IMPROVEMENT" />
            <el-option label="申诉" :value="ReviewType.APPEAL" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="审核状态" prop="status">
          <el-radio-group v-model="reviewForm.status">
            <el-radio :value="ReviewStatus.APPROVED">通过</el-radio>
            <el-radio :value="ReviewStatus.REJECTED">拒绝</el-radio>
            <el-radio :value="ReviewStatus.REVISED">要求修改</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="审核意见" prop="feedback">
          <el-input
            v-model="reviewForm.feedback"
            type="textarea"
            placeholder="请输入审核意见"
            rows="6"
            resize="vertical"
            show-word-limit
            maxlength="500"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reviewVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitReview">提交审核</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ReviewStatus, ReviewType } from '@/types/enums'
import { 
  type ReviewItem, 
  type ReviewFormData 
} from '@/types/review'
import { 
  getReviewList, 
  getReviewDetail, 
  reviewAction 
} from '@/api/review'

// 组件属性（预留）
defineProps<{}>()

// 组件事件（预留）
defineEmits<{}>()

// 搜索和筛选
const searchKeyword = ref('')
const statusFilter = ref<ReviewStatus | ''>('')
const typeFilter = ref<ReviewType | ''>('')
const dateRange = ref<[Date, Date] | null>(null)

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 审核反馈列表
const reviewList = ref<ReviewItem[]>([])

// 审核统计数据
const stats = reactive({
  pending: 0,
  approved: 0,
  rejected: 0,
  revised: 0
})

// 详情对话框
const detailVisible = ref(false)
const detailData = ref<ReviewItem | null>(null)

// 审核对话框
const reviewVisible = ref(false)
const reviewFormRef = ref()
const reviewForm = reactive<ReviewFormData>({
  id: 0,
  title: '',
  content: '',
  type: ReviewType.IMPROVEMENT,
  status: ReviewStatus.APPROVED,
  feedback: '',
  relatedId: 0
})

// 审核表单规则
const reviewFormRules = reactive({
  status: [{ required: true, message: '请选择审核状态', trigger: 'change' }],
  feedback: [{ required: true, message: '请输入审核意见', trigger: 'blur' }]
})

// 初始化组件
onMounted(() => {
  loadReviewList()
  loadReviewStats()
})

// 加载审核反馈列表
const loadReviewList = async () => {
  try {
    const params = {
      page: pagination.currentPage,
      pageSize: pagination.pageSize,
      status: statusFilter.value || undefined,
      type: typeFilter.value || undefined,
      keyword: searchKeyword.value || undefined,
      startTime: dateRange.value ? dateRange.value[0].toISOString().split('T')[0] : undefined,
      endTime: dateRange.value ? dateRange.value[1].toISOString().split('T')[0] : undefined
    }
    
    const response = await getReviewList(params)
    reviewList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载审核反馈列表失败')
    console.error('加载审核反馈列表失败:', error)
  }
}

// 加载审核统计数据
const loadReviewStats = async () => {
  try {
    // 模拟数据，实际项目中应调用API
    stats.pending = 5
    stats.approved = 23
    stats.rejected = 7
    stats.revised = 4
  } catch (error) {
    ElMessage.error('加载审核统计数据失败')
    console.error('加载审核统计数据失败:', error)
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.currentPage = 1
  loadReviewList()
}

// 处理筛选
const handleFilter = () => {
  pagination.currentPage = 1
  loadReviewList()
}

// 处理日期筛选
const handleDateFilter = () => {
  pagination.currentPage = 1
  loadReviewList()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadReviewList()
}

// 处理当前页变化
const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadReviewList()
}

// 刷新列表
const refreshList = () => {
  loadReviewList()
  loadReviewStats()
}

// 查看详情
const handleViewDetail = async (row: ReviewItem) => {
  try {
    const response = await getReviewDetail(row.id)
    detailData.value = response.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载审核反馈详情失败')
    console.error('加载审核反馈详情失败:', error)
  }
}

// 处理双击行
const handleRowDoubleClick = (row: ReviewItem) => {
  handleViewDetail(row)
}

// 进行审核
const handleReview = (row: ReviewItem) => {
  reviewForm.id = row.id
  reviewForm.title = row.title
  reviewForm.content = row.content
  reviewForm.type = row.type
  reviewForm.status = ReviewStatus.APPROVED
  reviewForm.feedback = ''
  reviewForm.relatedId = row.relatedId
  reviewVisible.value = true
}

// 提交审核
const handleSubmitReview = async () => {
  if (!reviewFormRef.value) return
  
  try {
    await (reviewFormRef.value as any).validate()
    
    await reviewAction({
      id: reviewForm.id as number,
      status: reviewForm.status,
      feedback: reviewForm.feedback
    })
    
    ElMessage.success('审核提交成功')
    reviewVisible.value = false
    
    // 刷新列表和统计数据
    loadReviewList()
    loadReviewStats()
    
    // 如果当前正在查看该审核的详情，也需要更新详情数据
    if (detailData.value && detailData.value.id === reviewForm.id) {
      const response = await getReviewDetail(reviewForm.id)
      detailData.value = response.data
    }
  } catch (error) {
    ElMessage.error('审核提交失败')
    console.error('审核提交失败:', error)
  }
}

// 获取状态标签类型
const getStatusTagType = (status: ReviewStatus) => {
  switch (status) {
    case ReviewStatus.PENDING:
      return 'warning'
    case ReviewStatus.APPROVED:
      return 'success'
    case ReviewStatus.REJECTED:
      return 'danger'
    case ReviewStatus.REVISED:
      return 'info'
    default:
      return ''
  }
}

// 获取状态文本
const getStatusText = (status: ReviewStatus) => {
  switch (status) {
    case ReviewStatus.PENDING:
      return '待审核'
    case ReviewStatus.APPROVED:
      return '已通过'
    case ReviewStatus.REJECTED:
      return '已拒绝'
    case ReviewStatus.REVISED:
      return '已修改'
    default:
      return ''
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 表格行样式
const tableRowClassName = ({ row }: { row: ReviewItem }) => {
  return row.status === ReviewStatus.PENDING ? 'pending-row' : ''
}
</script>

<style scoped>
.review-feedback-container {
  padding: 0;
}

.search-filter {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 150px;
}

.date-picker {
  width: 300px;
}

.search-filter .el-input__wrapper {
  border-radius: 8px;
}

.search-filter .el-select .el-input__wrapper {
  border-radius: 8px;
}

.search-filter .el-date-editor .el-input__wrapper {
  border-radius: 8px;
}

.review-list-card {
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(235, 245, 255, 0.9) 100%);
  border: 1px solid rgba(15, 76, 129, 0.2);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #0f4c81;
  font-family: 'SimHei', '黑体', sans-serif;
}

.card-title {
  font-size: 18px;
}

.header-stats {
  display: flex;
  gap: 15px;
}

.stat-badge {
  font-size: 14px;
  font-weight: normal;
}

.review-list-card .el-table {
  border-radius: 8px;
  overflow: hidden;
}

.review-list-card .el-table th {
  background-color: rgba(15, 76, 129, 0.9);
  color: white;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.review-list-card .el-table td {
  border-bottom: 1px solid rgba(15, 76, 129, 0.1);
}

.review-list-card .el-table__row:hover {
  background-color: rgba(255, 220, 120, 0.1);
}

.review-title {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pending-row {
  background-color: rgba(255, 220, 120, 0.15);
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.pagination .el-pagination__total {
  color: #606266;
}

.review-detail {
  padding: 10px 0;
}

.detail-section {
  margin: 20px 0;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
  font-weight: bold;
  position: relative;
  padding-bottom: 5px;
}

.detail-section h4::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #ffd04b, #0f4c81);
  border-radius: 2px;
}

.content-box {
  background-color: rgba(245, 247, 250, 1);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(220, 223, 230, 1);
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.feedback-box {
  background-color: rgba(240, 249, 235, 1);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(226, 238, 218, 1);
  line-height: 1.6;
  color: #67c23a;
  white-space: pre-wrap;
}

.attachments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background-color: rgba(235, 245, 255, 1);
  border-radius: 6px;
  border: 1px solid rgba(212, 226, 246, 1);
}

.review-operation-dialog .el-form {
  margin: 0;
}

.review-operation-dialog .el-form-item {
  margin-bottom: 20px;
}

.review-operation-dialog .el-textarea__wrapper {
  border-radius: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.dialog-footer .el-button {
  border-radius: 6px;
}

.dialog-footer .el-button--primary {
  background: linear-gradient(135deg, #0f4c81 0%, #1a5b93 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(15, 76, 129, 0.3);
}

.dialog-footer .el-button--primary:hover {
  background: linear-gradient(135deg, #1a5b93 0%, #246ca6 100%);
  box-shadow: 0 4px 12px rgba(15, 76, 129, 0.4);
}
</style>