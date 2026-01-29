<template>
  <div class="appeal-process-container">
    <div class="process-header">
      <h3>{{ currentStepTitle }}</h3>
      <div class="process-steps">
        <div
          v-for="(step, index) in processSteps"
          :key="index"
          class="step-item"
          :class="{
            'step-active': index === currentStep,
            'step-completed': index < currentStep
          }"
        >
          <div class="step-circle">
            <span v-if="index < currentStep"><el-icon name="Check" /></span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-text">{{ step.title }}</div>
        </div>
      </div>
    </div>
    
    <!-- 步骤内容区域 -->
    <div class="process-content">
      <!-- 步骤1：选择申诉类型 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-card class="step-card">
          <h4>请选择申诉类型</h4>
          <div class="appeal-types">
            <div
              v-for="type in appealTypes"
              :key="type.value"
              class="appeal-type-item"
              :class="{ 'appeal-type-active': selectedType === type.value }"
              @click="selectedType = type.value"
            >
              <div class="type-icon"><el-icon :name="type.iconName" /></div>
              <div class="type-info">
                <div class="type-title">{{ type.label }}</div>
                <div class="type-description">{{ type.description }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 步骤2：填写申诉信息 -->
      <div v-if="currentStep === 1" class="step-content">
        <el-card class="step-card">
          <el-form
            ref="appealFormRef"
            :model="appealForm"
            :rules="appealFormRules"
            label-width="100px"
            label-position="top"
          >
            <el-form-item label="申诉标题" prop="title">
              <el-input
                v-model="appealForm.title"
                placeholder="请输入申诉标题"
                size="default"
              />
            </el-form-item>
            
            <el-form-item label="关联项目" prop="relatedId">
              <el-select
                v-model="appealForm.relatedId"
                placeholder="请选择关联的评价或项目"
                size="default"
              >
                <el-option
                  v-for="item in relatedItems"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="申诉内容" prop="content">
              <el-input
                v-model="appealForm.content"
                type="textarea"
                placeholder="请详细描述您的申诉内容"
                rows="5"
                resize="vertical"
                show-word-limit
                maxlength="1000"
                size="default"
              />
            </el-form-item>
            
            <el-form-item label="申诉理由" prop="reason">
              <el-input
                v-model="appealForm.reason"
                type="textarea"
                placeholder="请说明您申诉的理由"
                rows="4"
                resize="vertical"
                show-word-limit
                maxlength="800"
                size="default"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </div>
      
      <!-- 步骤3：上传证据材料 -->
      <div v-if="currentStep === 2" class="step-content">
        <el-card class="step-card">
          <h4>上传证据材料</h4>
          <div class="evidence-upload">
            <el-upload
              v-model="appealForm.evidence"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              list-type="picture-card"
              accept=".jpg,.jpeg,.png,.pdf,.doc,.docx"
              multiple
              max="5"
            >
              <el-icon name="Plus" />
              <template #tip>
                <div class="el-upload__tip">
                  支持上传 JPG、PNG、PDF、DOC 格式的文件，最多上传 5 个文件，单个文件不超过 5MB
                </div>
              </template>
            </el-upload>
          </div>
        </el-card>
      </div>
      
      <!-- 步骤4：预览和提交 -->
      <div v-if="currentStep === 3" class="step-content">
        <el-card class="step-card">
          <h4>申诉信息预览</h4>
          <div class="appeal-preview">
            <div class="preview-item">
              <div class="preview-label">申诉类型：</div>
              <div class="preview-value">{{ getAppealTypeText(appealForm.type) }}</div>
            </div>
            <div class="preview-item">
              <div class="preview-label">申诉标题：</div>
              <div class="preview-value">{{ appealForm.title }}</div>
            </div>
            <div class="preview-item">
              <div class="preview-label">关联项目：</div>
              <div class="preview-value">{{ getRelatedItemName(appealForm.relatedId) }}</div>
            </div>
            <div class="preview-item">
              <div class="preview-label">申诉内容：</div>
              <div class="preview-value content">{{ appealForm.content }}</div>
            </div>
            <div class="preview-item">
              <div class="preview-label">申诉理由：</div>
              <div class="preview-value content">{{ appealForm.reason }}</div>
            </div>
            <div v-if="appealForm.evidence && appealForm.evidence.length > 0" class="preview-item">
              <div class="preview-label">证据材料：</div>
              <div class="preview-value">
                <el-link
                  v-for="(file, index) in fileList"
                  :key="index"
                  :href="file.url"
                  target="_blank"
                  type="primary"
                  class="evidence-link"
                >
                  {{ file.name }}
                </el-link>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 步骤5：提交成功 -->
      <div v-if="currentStep === 4" class="step-content">
        <el-card class="step-card success-card">
          <div class="success-icon">
            <el-icon name="SuccessFilled" />
          </div>
          <h4>申诉提交成功！</h4>
          <p class="success-message">您的申诉已成功提交，我们将尽快处理您的申诉请求。</p>
          <div class="appeal-info">
            <div class="info-item">
              <span class="info-label">申诉编号：</span>
              <span class="info-value">{{ appealId }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">提交时间：</span>
              <span class="info-value">{{ formatDate(new Date()) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">预计处理时间：</span>
              <span class="info-value">3-5 个工作日</span>
            </div>
          </div>
          <div class="success-actions">
            <el-button type="primary" @click="viewAppealProgress">查看申诉进度</el-button>
            <el-button @click="restartAppeal">提交新申诉</el-button>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 操作按钮区域 -->
    <div class="process-actions">
      <el-button
        v-if="currentStep > 0"
        @click="previousStep"
        :disabled="isSubmitting"
      >
        <el-icon name="ArrowLeft" /> 返回上一步
      </el-button>
      <div class="action-right">
        <el-button
          v-if="currentStep < processSteps.length - 2"
          @click="nextStep"
          :disabled="!canProceed || isSubmitting"
          type="primary"
        >
          下一步 <el-icon name="ArrowRight" />
        </el-button>
        <el-button
          v-if="currentStep === processSteps.length - 2"
          type="primary"
          @click="submitAppeal"
          :loading="isSubmitting"
          :disabled="!canProceed"
        >
          <el-icon name="Check" /> 提交申诉
        </el-button>
      </div>
    </div>
    
    <!-- 查看申诉进度对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="申诉进度查询"
      width="800px"
      class="appeal-progress-dialog"
    >
      <div class="progress-content">
        <div class="progress-info">
          <div class="progress-item">
            <span class="progress-label">申诉编号：</span>
            <span class="progress-value">{{ appealId }}</span>
          </div>
          <div class="progress-item">
            <span class="progress-label">申诉类型：</span>
            <span class="progress-value">{{ getAppealTypeText(appealForm.type) }}</span>
          </div>
          <div class="progress-item">
            <span class="progress-label">申诉标题：</span>
            <span class="progress-value">{{ appealForm.title }}</span>
          </div>
          <div class="progress-item">
            <span class="progress-label">当前状态：</span>
            <el-tag :type="appealStatusTagType">{{ appealStatusText }}</el-tag>
          </div>
          <div class="progress-item">
            <span class="progress-label">提交时间：</span>
            <span class="progress-value">{{ formatDate(new Date()) }}</span>
          </div>
        </div>
        
        <div class="progress-timeline">
          <div
            v-for="(event, index) in appealEvents"
            :key="index"
            class="timeline-item"
          >
            <div class="timeline-dot" :class="event.status"></div>
            <div class="timeline-content">
              <div class="timeline-title">{{ event.title }}</div>
              <div class="timeline-description">{{ event.description }}</div>
              <div class="timeline-time">{{ formatDate(event.time) }}</div>
            </div>
          </div>
        </div>
        
        <div class="progress-notes">
          <h4>申诉备注</h4>
          <div class="notes-content">{{ appealNotes }}</div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="progressDialogVisible = false">关闭</el-button>
          <el-button
            v-if="appealStatus === 'processing'"
            type="warning"
            @click="addAppealReply"
          >
            添加回复
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { AppealType } from '@/types/enums'
import type { AppealFormData } from '@/types/appeal'

// 组件属性（预留）
defineProps<{}>()

// 组件事件（预留）
defineEmits<{}>()

// 流程步骤
const processSteps = ref([
  { title: '选择类型', component: '' },
  { title: '填写信息', component: '' },
  { title: '上传证据', component: '' },
  { title: '预览提交', component: '' },
  { title: '完成', component: '' }
])

// 当前步骤
const currentStep = ref(0)

// 申诉类型选择
const selectedType = ref<AppealType | null>(null)

// 申诉表单数据
const appealFormRef = ref()
const appealForm = reactive<AppealFormData>({
  type: AppealType.EVALUATION,
  title: '',
  content: '',
  reason: '',
  evidence: [],
  relatedId: 0
})

// 申诉表单验证规则
const appealFormRules = reactive({
  title: [{ required: true, message: '请输入申诉标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入申诉内容', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入申诉理由', trigger: 'blur' }],
  relatedId: [{ required: true, message: '请选择关联项目', trigger: 'change' }]
})

// 文件列表
interface FileItem {
  name: string;
  url: string;
  uid: string;
  status?: string;
  response?: any;
}

const fileList = ref<FileItem[]>([])

// 提交状态
const isSubmitting = ref(false)

// 申诉ID
const appealId = ref('AP' + Date.now())

// 申诉状态
const appealStatus = ref('pending') // pending, processing, approved, rejected

// 申诉事件
const appealEvents = ref([
  {
    title: '申诉提交',
    description: '您的申诉已成功提交，等待审核',
    time: new Date(),
    status: 'completed'
  }
])

// 申诉备注
const appealNotes = ref('您的申诉正在处理中，请耐心等待。')

// 查看进度对话框
const progressDialogVisible = ref(false)

// 申诉类型选项
const appealTypes = ref([
  {
    value: AppealType.EVALUATION,
    label: '评价申诉',
    description: '对学生评价内容或结果有异议',
    iconName: 'Document'
  },
  {
    value: AppealType.SCORE,
    label: '分数申诉',
    description: '对评价分数计算有异议',
    iconName: 'Star'
  },
  {
    value: AppealType.PROCESS,
    label: '流程申诉',
    description: '对评价流程或规则有异议',
    iconName: 'Management'
  }
])

// 关联项目选项
const relatedItems = ref([
  { id: 1, name: '数据结构课程评价 - 2026年春季学期' },
  { id: 2, name: '高等数学课程评价 - 2026年春季学期' },
  { id: 3, name: '大学物理课程评价 - 2026年春季学期' },
  { id: 4, name: '计算机基础课程评价 - 2026年春季学期' }
])

// 当前步骤标题
const currentStepTitle = computed(() => {
  return processSteps.value[currentStep.value]?.title || '申诉流程'
})

// 是否可以进入下一步
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return selectedType.value !== null
  } else if (currentStep.value === 1) {
    // 验证表单
    if (!appealFormRef.value) return false
    let isValid = true
    ;(appealFormRef.value as any).validate((valid: boolean) => {
      isValid = valid
    })
    return isValid
  } else if (currentStep.value === 2) {
    // 证据材料可选
    return true
  } else if (currentStep.value === 3) {
    // 预览步骤，确保所有必填项都已填写
    return appealForm.title && appealForm.content && appealForm.reason && appealForm.relatedId
  }
  return false
})

// 监听申诉类型变化
watch(selectedType, (newType) => {
  if (newType) {
    appealForm.type = newType
  }
})

// 下一步
const nextStep = () => {
  if (currentStep.value < processSteps.value.length - 1) {
    currentStep.value++
  }
}

// 上一步
const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 提交申诉
const submitAppeal = async () => {
  isSubmitting.value = true
  
  try {
    // 模拟提交申诉
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 实际项目中应调用API
    // await createAppeal(appealForm)
    
    ElMessage.success('申诉提交成功！')
    
    // 进入完成步骤
    currentStep.value++
  } catch (error) {
    ElMessage.error('申诉提交失败，请重试')
    console.error('申诉提交失败:', error)
  } finally {
    isSubmitting.value = false
  }
}

// 处理文件上传
const handleFileChange = (_file: any, fileList: any) => {
  fileList.value = fileList
  // 实际项目中应处理文件上传逻辑
}

// 处理文件移除
const handleFileRemove = (_file: any, fileList: any) => {
  fileList.value = fileList
}

// 查看申诉进度
const viewAppealProgress = () => {
  progressDialogVisible.value = true
}

// 重新提交申诉
const restartAppeal = () => {
  currentStep.value = 0
  selectedType.value = null
  appealForm.title = ''
  appealForm.content = ''
  appealForm.reason = ''
  appealForm.evidence = []
  appealForm.relatedId = 0
  fileList.value = []
  appealId.value = 'AP' + Date.now()
  appealStatus.value = 'pending'
}

// 添加申诉回复
const addAppealReply = () => {
  ElMessageBox.prompt('请输入回复内容', '添加回复', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputType: 'textarea',
    inputPlaceholder: '请输入回复内容',
    inputValidator: (value: string): string | boolean => {
      if (!value.trim()) {
        return '回复内容不能为空'
      }
      return true
    }
  }).then(({ value }) => {
    // 模拟添加回复
    appealEvents.value.push({
      title: '添加回复',
      description: value,
      time: new Date(),
      status: 'processing'
    })
    
    appealNotes.value = value
    ElMessage.success('回复添加成功')
  }).catch(() => {
    // 用户取消
  })
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
      return '未知类型'
  }
}

// 获取关联项目名称
const getRelatedItemName = (id: number) => {
  const item = relatedItems.value.find(item => item.id === id)
  return item?.name || '未知项目'
}

// 申诉状态文本
const appealStatusText = computed(() => {
  switch (appealStatus.value) {
    case 'pending':
      return '待审核'
    case 'processing':
      return '处理中'
    case 'approved':
      return '已通过'
    case 'rejected':
      return '已拒绝'
    default:
      return '未知状态'
  }
})

// 申诉状态标签类型
const appealStatusTagType = computed(() => {
  switch (appealStatus.value) {
    case 'pending':
      return 'warning'
    case 'processing':
      return 'info'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'danger'
    default:
      return ''
  }
})

// 格式化日期
const formatDate = (date: Date | string | undefined) => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN', {
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
.appeal-process-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 12px;
}

.process-header {
  margin-bottom: 30px;
}

.process-header h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
  font-weight: bold;
}

.process-steps {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 0 auto;
  max-width: 800px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  padding: 0 10px;
}

.step-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 15px;
  right: -30px;
  width: 60px;
  height: 2px;
  background-color: #e0e0e0;
  z-index: 1;
}

.step-item.step-completed:not(:last-child)::after,
.step-item.step-active:not(:last-child)::after {
  background-color: #409eff;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  z-index: 2;
  transition: all 0.3s ease;
}

.step-item.step-active .step-circle {
  background-color: #409eff;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.5);
}

.step-item.step-completed .step-circle {
  background-color: #67c23a;
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.5);
}

.step-text {
  font-size: 14px;
  color: #909399;
  transition: color 0.3s ease;
}

.step-item.step-active .step-text,
.step-item.step-completed .step-text {
  color: #303133;
  font-weight: bold;
}

.process-content {
  margin-bottom: 30px;
}

.step-content {
  max-width: 800px;
  margin: 0 auto;
}

.step-card {
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(235, 245, 255, 0.9) 100%);
  border: 1px solid rgba(15, 76, 129, 0.2);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.step-card h4 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 16px;
  font-weight: bold;
  position: relative;
  padding-bottom: 10px;
}

.step-card h4::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #ffd04b, #0f4c81);
  border-radius: 2px;
}

/* 申诉类型选择 */
.appeal-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.appeal-type-item {
  padding: 20px;
  border: 2px solid rgba(220, 223, 230, 1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: white;
  display: flex;
  gap: 15px;
}

.appeal-type-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.appeal-type-item.appeal-type-active {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  background-color: rgba(235, 245, 255, 0.5);
}

.type-icon {
  font-size: 24px;
  color: #409eff;
}

.type-info {
  flex: 1;
}

.type-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.type-description {
  font-size: 14px;
  color: #909399;
  line-height: 1.4;
}

/* 证据上传 */
.evidence-upload {
  margin-top: 20px;
}

/* 预览区域 */
.appeal-preview {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.preview-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: rgba(245, 247, 250, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(220, 223, 230, 0.5);
}

.preview-label {
  width: 100px;
  font-weight: bold;
  color: #303133;
  flex-shrink: 0;
}

.preview-value {
  flex: 1;
  color: #606266;
}

.preview-value.content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.evidence-link {
  margin-right: 10px;
  margin-bottom: 10px;
}

/* 成功页面 */
.success-card {
  text-align: center;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin: 20px 0;
}

.success-message {
  margin: 20px 0;
  color: #606266;
  line-height: 1.6;
}

.appeal-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 30px 0;
  padding: 20px;
  background-color: rgba(240, 249, 235, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(226, 238, 218, 1);
}

.info-item {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.info-label {
  font-weight: bold;
  color: #67c23a;
}

.success-actions {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 操作按钮 */
.process-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
}

.action-right {
  display: flex;
  gap: 10px;
}

/* 申诉进度对话框 */
.progress-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 15px;
  background-color: rgba(245, 247, 250, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(220, 223, 230, 0.5);
}

.progress-item {
  display: flex;
  gap: 10px;
}

.progress-label {
  width: 100px;
  font-weight: bold;
  color: #303133;
}

.progress-value {
  flex: 1;
  color: #606266;
}

.progress-timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timeline-item {
  display: flex;
  gap: 20px;
  position: relative;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  top: 30px;
  left: 15px;
  width: 2px;
  height: calc(100% + 20px);
  background-color: #e0e0e0;
}

.timeline-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e0e0e0;
  margin-top: 5px;
  flex-shrink: 0;
}

.timeline-dot.completed {
  background-color: #67c23a;
}

.timeline-dot.processing {
  background-color: #e6a23c;
}

.timeline-dot.pending {
  background-color: #909399;
}

.timeline-content {
  flex: 1;
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(220, 223, 230, 0.5);
}

.timeline-title {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.timeline-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
}

.timeline-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.progress-notes {
  padding: 15px;
  background-color: rgba(240, 249, 235, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(226, 238, 218, 1);
}

.progress-notes h4 {
  margin: 0 0 15px 0;
  color: #67c23a;
  font-size: 16px;
  font-weight: bold;
}

.notes-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>