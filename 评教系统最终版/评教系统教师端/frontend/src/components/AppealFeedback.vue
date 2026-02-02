<template>
  <div class="appeal-feedback-container">
    <!-- 搜索和筛选区域 -->
    <div class="search-filter">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索申诉标题或内容"
        prefix-icon="Search"
        clearable
        size="default"
        class="search-input"
        @input="handleSearch"
      />
      
      <el-select
        v-model="statusFilter"
        placeholder="选择申诉状态"
        size="default"
        class="filter-select"
        @change="handleFilter"
      >
        <el-option label="全部" value="" />
        <el-option label="待审核" :value="AppealStatus.PENDING" />
        <el-option label="已通过" :value="AppealStatus.APPROVED" />
        <el-option label="已拒绝" :value="AppealStatus.REJECTED" />
        <el-option label="处理中" :value="AppealStatus.PROCESSING" />
      </el-select>
      
      <el-select
        v-model="typeFilter"
        placeholder="选择申诉类型"
        size="default"
        class="filter-select"
        @change="handleFilter"
      >
        <el-option label="全部" value="" />
        <el-option label="评价申诉" :value="AppealType.EVALUATION" />
        <el-option label="分数申诉" :value="AppealType.SCORE" />
        <el-option label="流程申诉" :value="AppealType.PROCESS" />
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
    
    <!-- 申诉列表 -->
    <el-card class="table-card" shadow="hover">
      <el-table :data="appealList" style="width: 100%" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="申诉标题" min-width="200">
          <template #default="scope">
            <div class="appeal-title">{{ scope.row.title }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="申诉类型" width="120">
          <template #default="scope">
            <el-tag :type="getAppealTypeTagType(scope.row.type)">
              {{ getAppealTypeText(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag
              :type="getAppealStatusTagType(scope.row.status)"
              effect="dark"
            >
              {{ getAppealStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator" label="申诉人" width="120" />
        <el-table-column prop="createTime" label="申诉时间" width="180">
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleViewDetail(scope.row)">
              <el-icon name="Document" />
              详情
            </el-button>
            <el-button
              v-if="scope.row.status === AppealStatus.PENDING"
              type="success"
              size="small"
              @click="handleReviewAppeal(scope.row)"
            >
              <el-icon name="Check" />
              审核
            </el-button>
            <el-button
              v-if="scope.row.status === AppealStatus.PROCESSING"
              type="warning"
              size="small"
              @click="handleReplyAppeal(scope.row)"
            >
              <el-icon name="Edit" />
              回复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="pagination.currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
        />
      </div>
    </el-card>
    
    <!-- 申诉详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="`申诉详情 - ${detailData?.title}`"
      width="800px"
      class="appeal-detail-dialog"
    >
      <div v-if="detailData" class="appeal-detail">
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="申诉ID">{{ detailData.id }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ detailData.title }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="getAppealTypeTagType(detailData.type)">
              {{ getAppealTypeText(detailData.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="getAppealStatusTagType(detailData.status)"
              effect="dark"
            >
              {{ getAppealStatusText(detailData.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="申诉人">{{ detailData.creator }}</el-descriptions-item>
          <el-descriptions-item label="申诉时间">{{ formatDate(detailData.createTime) }}</el-descriptions-item>
          <el-descriptions-item label="审核人">{{ detailData.reviewer || '-' }}</el-descriptions-item>
          <el-descriptions-item label="审核时间">{{ formatDate(detailData.reviewTime) }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="detail-section">
          <h4>申诉内容</h4>
          <div class="content-box">{{ detailData.content }}</div>
        </div>
        
        <div class="detail-section">
          <h4>申诉理由</h4>
          <div class="reason-box">{{ detailData.reason }}</div>
        </div>
        
        <div v-if="detailData.evidence && detailData.evidence.length > 0" class="detail-section">
          <h4>证据材料</h4>
          <div class="evidence-list">
            <el-link
              v-for="(evidence, index) in detailData.evidence"
              :key="index"
              :href="evidence"
              target="_blank"
              type="primary"
              class="evidence-item"
            >
              <el-icon name="Picture" />
              证据 {{ index + 1 }}
            </el-link>
          </div>
        </div>
        
        <div v-if="detailData.feedback" class="detail-section">
          <h4>审核意见</h4>
          <div class="feedback-box">{{ detailData.feedback }}</div>
        </div>
        
        <div v-if="detailData.reply" class="detail-section">
          <h4>回复内容</h4>
          <div class="reply-box">{{ detailData.reply }}</div>
          <div class="reply-time">回复时间：{{ formatDate(detailData.replyTime) }}</div>
        </div>
        
        <div v-if="detailData.appealHistory && detailData.appealHistory.length > 0" class="detail-section">
          <h4>申诉历史</h4>
          <div class="appeal-history">
            <div
              v-for="(history, index) in detailData.appealHistory"
              :key="index"
              class="history-item"
              :class="`history-${history.type}`"
            >
              <div class="history-header">
                <span class="history-creator">{{ history.creator }}</span>
                <span class="history-time">{{ formatDate(history.createTime) }}</span>
                <el-tag :type="getHistoryTypeTagType(history.type)">
                  {{ getHistoryTypeText(history.type) }}
                </el-tag>
              </div>
              <div class="history-content">{{ history.content }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button
            v-if="detailData?.status === AppealStatus.PENDING"
            type="primary"
            @click="handleReviewAppeal(detailData)"
          >
            进行审核
          </el-button>
          <el-button
            v-if="detailData?.status === AppealStatus.PROCESSING"
            type="warning"
            @click="handleReplyAppeal(detailData)"
          >
            回复申诉
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 申诉审核对话框 -->
    <el-dialog
      v-model="reviewVisible"
      title="申诉审核"
      width="600px"
      class="appeal-review-dialog"
    >
      <el-form
        ref="reviewFormRef"
        :model="reviewForm"
        :rules="reviewFormRules"
        label-width="100px"
        label-position="left"
        size="default"
      >
        <el-form-item label="申诉标题" prop="title">
          <el-input v-model="reviewForm.title" readonly />
        </el-form-item>
        
        <el-form-item label="申诉类型" prop="type">
          <el-select v-model="reviewForm.type" disabled>
            <el-option label="评价申诉" :value="AppealType.EVALUATION" />
            <el-option label="分数申诉" :value="AppealType.SCORE" />
            <el-option label="流程申诉" :value="AppealType.PROCESS" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="审核状态" prop="status">
          <el-radio-group v-model="reviewForm.status">
            <el-radio :value="AppealStatus.APPROVED">通过</el-radio>
            <el-radio :value="AppealStatus.REJECTED">拒绝</el-radio>
            <el-radio :value="AppealStatus.PROCESSING">处理中</el-radio>
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
    
    <!-- 申诉回复对话框 -->
    <el-dialog
      v-model="replyVisible"
      title="回复申诉"
      width="600px"
      class="appeal-reply-dialog"
    >
      <el-form
        ref="replyFormRef"
        :model="replyForm"
        :rules="replyFormRules"
        label-width="100px"
        label-position="left"
        size="default"
      >
        <el-form-item label="申诉标题" prop="title">
          <el-input v-model="replyForm.title" readonly />
        </el-form-item>
        
        <el-form-item label="回复内容" prop="reply">
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            placeholder="请输入回复内容"
            rows="8"
            resize="vertical"
            show-word-limit
            maxlength="1000"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="replyVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitReply">提交回复</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { AppealStatus, AppealType } from '@/types/enums'
import { 
  type AppealItem, 
  type AppealDetail,
  type AppealReviewData, 
  type AppealReplyData 
} from '@/types/appeal'
import { 
  getAppealDetail, 
  reviewAppeal, 
  replyAppeal 
} from '@/api/appeal'

// 组件属性（预留）
defineProps<{}>()

// 组件事件（预留）
defineEmits<{}>()

// 搜索和筛选
const searchKeyword = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const dateRange = ref<[Date, Date] | null>(null)

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 申诉列表
const appealList = ref<AppealItem[]>([])

// 申诉详情
const detailVisible = ref(false)
const detailData = ref<AppealDetail | null>(null)

// 申诉审核
const reviewVisible = ref(false)
const reviewFormRef = ref()
const reviewForm = reactive<AppealReviewData & { title: string; type: AppealType }>({
  id: 0,
  title: '',
  type: AppealType.EVALUATION,
  status: AppealStatus.APPROVED,
  feedback: ''
})

// 申诉审核表单规则
const reviewFormRules = reactive({
  status: [{ required: true, message: '请选择审核状态', trigger: 'change' }],
  feedback: [{ required: true, message: '请输入审核意见', trigger: 'blur' }]
})

// 申诉回复
const replyVisible = ref(false)
const replyFormRef = ref()
const replyForm = reactive<AppealReplyData & { title: string }>({
  id: 0,
  title: '',
  reply: ''
})

// 申诉回复表单规则
const replyFormRules = reactive({
  reply: [{ required: true, message: '请输入回复内容', trigger: 'blur' }]
})

// 初始化组件
onMounted(() => {
  loadAppealList()
})

// 加载申诉列表
const loadAppealList = async () => {
  try {
    // 模拟数据，实际项目中应调用API
    appealList.value = [
      {
        id: 1,
        title: '关于数据结构课程评价的申诉',
        type: AppealType.EVALUATION,
        status: AppealStatus.APPROVED,
        content: '我对本次数据结构课程的评价结果有异议',
        reason: '评价内容与实际教学情况不符，存在不实信息',
        evidence: ['https://example.com/evidence1.jpg', 'https://example.com/evidence2.jpg'],
        creator: '张老师',
        createTime: '2026-01-15T10:30:00',
        reviewer: '李主任',
        reviewTime: '2026-01-16T14:20:00',
        feedback: '经核实，同意申诉请求，将重新进行评价',
        reply: '已重新组织评价，结果将在3个工作日内公布',
        replyTime: '2026-01-17T09:45:00',
        relatedId: 1001
      },
      {
        id: 2,
        title: '关于高等数学分数的申诉',
        type: AppealType.SCORE,
        status: AppealStatus.PENDING,
        content: '我对高等数学课程的评价分数有异议',
        reason: '评价分数明显低于实际教学质量',
        evidence: ['https://example.com/evidence3.jpg'],
        creator: '王老师',
        createTime: '2026-01-18T09:15:00',
        reviewer: '',
        reviewTime: '',
        feedback: '',
        reply: '',
        replyTime: '',
        relatedId: 2001
      },
      {
        id: 3,
        title: '关于评价流程的申诉',
        type: AppealType.PROCESS,
        status: AppealStatus.PROCESSING,
        content: '评价流程存在不合理之处',
        reason: '评价周期过短，无法充分反映教学情况',
        evidence: [],
        creator: '刘老师',
        createTime: '2026-01-19T16:40:00',
        reviewer: '赵院长',
        reviewTime: '2026-01-20T11:10:00',
        feedback: '已受理申诉，正在调查中',
        reply: '',
        replyTime: '',
        relatedId: 3001
      }
    ]
    pagination.total = appealList.value.length
  } catch (error) {
    ElMessage.error('加载申诉列表失败')
    console.error('加载申诉列表失败:', error)
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.currentPage = 1
  loadAppealList()
}

// 处理筛选
const handleFilter = () => {
  pagination.currentPage = 1
  loadAppealList()
}

// 处理日期筛选
const handleDateFilter = () => {
  pagination.currentPage = 1
  loadAppealList()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadAppealList()
}

// 处理当前页变化
const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadAppealList()
}

// 刷新列表
const refreshList = () => {
  loadAppealList()
}

// 查看详情
const handleViewDetail = async (row: AppealItem) => {
  try {
    const response = await getAppealDetail(row.id)
    detailData.value = response.data
    detailVisible.value = true
  } catch (error) {
    // 模拟数据
    detailData.value = row
    detailVisible.value = true
    ElMessage.info('使用模拟数据展示详情')
  }
}

// 审核申诉
const handleReviewAppeal = (row: AppealItem) => {
  reviewForm.id = row.id
  reviewForm.title = row.title
  reviewForm.type = row.type
  reviewForm.status = AppealStatus.APPROVED
  reviewForm.feedback = ''
  reviewVisible.value = true
}

// 回复申诉
const handleReplyAppeal = (row: AppealItem) => {
  replyForm.id = row.id
  replyForm.title = row.title
  replyForm.reply = ''
  replyVisible.value = true
}

// 提交审核
const handleSubmitReview = async () => {
  if (!reviewFormRef.value) return
  
  try {
    await (reviewFormRef.value as any).validate()
    
    await reviewAppeal({
      id: reviewForm.id,
      status: reviewForm.status,
      feedback: reviewForm.feedback
    })
    
    ElMessage.success('审核提交成功')
    reviewVisible.value = false
    loadAppealList()
    
    // 更新详情数据
    if (detailData.value && detailData.value.id === reviewForm.id) {
      detailData.value.status = reviewForm.status
      detailData.value.feedback = reviewForm.feedback
      detailData.value.reviewer = '当前用户' // 实际项目中应从登录信息获取
      detailData.value.reviewTime = new Date().toISOString()
    }
  } catch (error) {
    ElMessage.error('审核提交失败')
    console.error('审核提交失败:', error)
  }
}

// 提交回复
const handleSubmitReply = async () => {
  if (!replyFormRef.value) return
  
  try {
    await (replyFormRef.value as any).validate()
    
    await replyAppeal({
      id: replyForm.id,
      reply: replyForm.reply
    })
    
    ElMessage.success('回复提交成功')
    replyVisible.value = false
    loadAppealList()
    
    // 更新详情数据
    if (detailData.value && detailData.value.id === replyForm.id) {
      detailData.value.reply = replyForm.reply
      detailData.value.replyTime = new Date().toISOString()
    }
  } catch (error) {
    ElMessage.error('回复提交失败')
    console.error('回复提交失败:', error)
  }
}

// 获取申诉类型标签类型
const getAppealTypeTagType = (type: AppealType) => {
  switch (type) {
    case AppealType.EVALUATION:
      return 'primary'
    case AppealType.SCORE:
      return 'warning'
    case AppealType.PROCESS:
      return 'info'
    default:
      return ''
  }
}

// 获取申诉类型文本
const getAppealTypeText = (type: AppealType) => {
  switch (type) {
    case AppealType.EVALUATION:
      return '评价申诉'
    case AppealType.SCORE:
      return '分数申诉'
    case AppealType.PROCESS:
      return '流程申诉'
    default:
      return ''
  }
}

// 获取申诉状态标签类型
const getAppealStatusTagType = (status: AppealStatus) => {
  switch (status) {
    case AppealStatus.APPROVED:
      return 'success'
    case AppealStatus.PENDING:
      return 'warning'
    case AppealStatus.REJECTED:
      return 'danger'
    case AppealStatus.PROCESSING:
      return 'info'
    default:
      return ''
  }
}

// 获取申诉状态文本
const getAppealStatusText = (status: AppealStatus) => {
  switch (status) {
    case AppealStatus.APPROVED:
      return '已通过'
    case AppealStatus.PENDING:
      return '待审核'
    case AppealStatus.REJECTED:
      return '已拒绝'
    case AppealStatus.PROCESSING:
      return '处理中'
    default:
      return ''
  }
}

// 获取历史记录类型标签类型
const getHistoryTypeTagType = (type: string) => {
  switch (type) {
    case 'appeal':
      return 'primary'
    case 'reply':
      return 'success'
    case 'review':
      return 'warning'
    default:
      return ''
  }
}

// 获取历史记录类型文本
const getHistoryTypeText = (type: string) => {
  switch (type) {
    case 'appeal':
      return '申诉'
    case 'reply':
      return '回复'
    case 'review':
      return '审核'
    default:
      return ''
  }
}

// 格式化日期
const formatDate = (dateString: string | undefined) => {
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
</script>

<style scoped>
.appeal-feedback-container {
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

.table-card {
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(235, 245, 255, 0.9) 100%);
  border: 1px solid rgba(15, 76, 129, 0.2);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.table-card .el-table {
  border-radius: 8px;
  overflow: hidden;
}

.table-card .el-table th {
  background-color: rgba(15, 76, 129, 0.9);
  color: white;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.table-card .el-table td {
  border-bottom: 1px solid rgba(15, 76, 129, 0.1);
}

.table-card .el-table__row:hover {
  background-color: rgba(255, 220, 120, 0.1);
}

.appeal-title {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.pagination-container .el-pagination__total {
  color: #606266;
}

.appeal-detail {
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

.content-box, .reason-box {
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

.reply-box {
  background-color: rgba(235, 245, 255, 1);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(212, 226, 246, 1);
  line-height: 1.6;
  color: #409eff;
  white-space: pre-wrap;
}

.reply-time {
  margin-top: 10px;
  text-align: right;
  font-size: 12px;
  color: #909399;
}

.evidence-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.evidence-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background-color: rgba(235, 245, 255, 1);
  border-radius: 6px;
  border: 1px solid rgba(212, 226, 246, 1);
}

.appeal-history {
  border: 1px solid rgba(220, 223, 230, 1);
  border-radius: 8px;
  padding: 10px;
  background-color: rgba(245, 247, 250, 0.5);
}

.history-item {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 6px;
  background-color: white;
  border-left: 3px solid #c0c4cc;
}

.history-item:last-child {
  margin-bottom: 0;
}

.history-appeal {
  border-left-color: #409eff;
}

.history-reply {
  border-left-color: #67c23a;
}

.history-review {
  border-left-color: #e6a23c;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  font-size: 14px;
  color: #303133;
}

.history-creator {
  font-weight: bold;
}

.history-time {
  color: #909399;
  font-size: 12px;
}

.history-content {
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>