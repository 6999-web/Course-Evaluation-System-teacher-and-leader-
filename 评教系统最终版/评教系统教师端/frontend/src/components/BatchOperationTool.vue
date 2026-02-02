<template>
  <div class="batch-operation-tool">
    <!-- 批量操作工具栏 -->
    <el-card class="batch-tool-card" shadow="hover">
      <template #header>
        <div class="batch-tool-header">
          <el-icon name="DocumentCopy"></el-icon>
          <span class="batch-tool-title">批量操作工具</span>
        </div>
      </template>
      
      <div class="batch-tool-content">
        <!-- 选择区域 -->
        <div class="selection-section">
          <el-select v-model="selectedBatchType" placeholder="请选择操作类型" size="large" @change="handleBatchTypeChange">
            <el-option label="批量导出评价报告" value="export" />
            <el-option label="批量提交申诉" value="appeal" />
            <el-option label="批量标记已处理" value="mark" />
            <el-option label="批量下载教学资源" value="download" />
          </el-select>
          
          <el-select v-model="selectedItems" placeholder="请选择要操作的项目" multiple filterable remote reserve-keyword size="large" :remote-method="remoteSearchItems" :loading="loadingItems">
            <el-option v-for="item in filteredItems" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </div>
        
        <!-- 配置区域 -->
        <div class="config-section" v-if="selectedBatchType">
          <el-divider>{{ getConfigTitle() }}</el-divider>
          
          <!-- 导出配置 -->
          <div v-if="selectedBatchType === 'export'" class="config-content">
            <el-form label-position="top" size="default">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="导出格式">
                    <el-radio-group v-model="exportConfig.format">
                      <el-radio value="pdf">PDF</el-radio>
                      <el-radio value="excel">Excel</el-radio>
                      <el-radio value="word">Word</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="导出范围">
                    <el-radio-group v-model="exportConfig.range">
                      <el-radio value="all">全部内容</el-radio>
                      <el-radio value="summary">仅摘要</el-radio>
                      <el-radio value="details">详细数据</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="导出字段">
                    <el-checkbox-group v-model="exportConfig.fields">
                      <el-checkbox :label="'courseName'">课程名称</el-checkbox>
                      <el-checkbox :label="'studentName'">学生姓名</el-checkbox>
                      <el-checkbox :label="'scores'">评分详情</el-checkbox>
                      <el-checkbox :label="'comments'">评价内容</el-checkbox>
                      <el-checkbox :label="'suggestions'">改进建议</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
          
          <!-- 申诉配置 -->
          <div v-if="selectedBatchType === 'appeal'" class="config-content">
            <el-form label-position="top" size="default">
              <el-row :gutter="20">
                <el-col :span="24">
                  <el-form-item label="申诉类型">
                    <el-select v-model="appealConfig.type" placeholder="请选择申诉类型">
                      <el-option label="评价内容申诉" value="evaluation" />
                      <el-option label="分数计算申诉" value="score" />
                      <el-option label="评价流程申诉" value="process" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="申诉理由">
                    <el-input v-model="appealConfig.reason" type="textarea" :rows="3" placeholder="请输入申诉理由" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="附加证据">
                    <el-upload
                      v-model:file-list="appealConfig.evidenceFiles"
                      class="upload-demo"
                      action="#"
                      multiple
                      :auto-upload="false"
                    >
                      <el-button type="primary">
                        <el-icon name="Plus"></el-icon> 选择文件
                      </el-button>
                      <template #tip>
                        <div class="el-upload__tip">
                          支持上传图片、文档等证据材料，单文件不超过20MB
                        </div>
                      </template>
                    </el-upload>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
          
          <!-- 标记配置 -->
          <div v-if="selectedBatchType === 'mark'" class="config-content">
            <el-form label-position="top" size="default">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="标记状态">
                    <el-select v-model="markConfig.status" placeholder="请选择标记状态">
                      <el-option label="已查看" value="viewed" />
                      <el-option label="已处理" value="processed" />
                      <el-option label="待跟进" value="followup" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="处理备注">
                    <el-input v-model="markConfig.remark" type="textarea" :rows="2" placeholder="请输入处理备注" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
          
          <!-- 下载配置 -->
          <div v-if="selectedBatchType === 'download'" class="config-content">
            <el-form label-position="top" size="default">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="资源类型">
                    <el-checkbox-group v-model="downloadConfig.resourceTypes">
                      <el-checkbox :label="'PPT课件'">PPT课件</el-checkbox>
                      <el-checkbox :label="'视频教程'">视频教程</el-checkbox>
                      <el-checkbox :label="'教学案例'">教学案例</el-checkbox>
                      <el-checkbox :label="'参考资料'">参考资料</el-checkbox>
                    </el-checkbox-group>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="下载方式">
                    <el-radio-group v-model="downloadConfig.downloadType">
                      <el-radio value="打包下载">打包下载</el-radio>
                      <el-radio value="分别下载">分别下载</el-radio>
                      <el-radio value="导入到云盘">导入到云盘</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>
        
        <!-- 操作按钮区域 -->
        <div class="action-section">
          <el-button type="primary" size="large" :loading="isProcessing" :disabled="!canExecute" @click="executeBatchOperation">
            <el-icon name="Upload" v-if="selectedBatchType === 'export' || selectedBatchType === 'download'"></el-icon>
            <el-icon name="CircleCheck" v-if="selectedBatchType === 'appeal' || selectedBatchType === 'mark'"></el-icon>
            {{ getActionButtonText() }}
          </el-button>
          
          <el-button size="large" @click="resetForm">重置</el-button>
        </div>
        
        <!-- 进度区域 -->
        <div class="progress-section" v-if="isProcessing">
          <el-progress :percentage="progress" :status="progressStatus" :stroke-width="20" :show-text="true" />
          <div class="progress-log">{{ currentProgressText }}</div>
        </div>
        
        <!-- 结果区域 -->
        <div class="result-section" v-if="operationResult">
          <el-result :icon="operationResult.success ? 'success' : 'error'" :title="operationResult.title" :sub-title="operationResult.subTitle">
            <template #extra>
              <el-button type="primary" @click="viewOperationDetails">查看详情</el-button>
              <el-button @click="resetResult">返回</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="dialogVisible" title="操作详情" width="70%" :before-close="handleDialogClose">
      <div class="result-details">
        <el-table :data="operationDetails" style="width: 100%" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="项目名称" min-width="200" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">{{ scope.row.status === 'success' ? '成功' : '失败' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="信息" min-width="300" />
          <el-table-column prop="time" label="处理时间" width="180" />
        </el-table>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadOperationReport">下载操作报告</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 批量操作类型
const selectedBatchType = ref<string>('')
const selectedItems = ref<string[]>([])

// 数据加载状态
const loadingItems = ref(false)
const filteredItems = ref<any[]>([])
const allItems = ref<any[]>([])

// 处理状态
const isProcessing = ref(false)
const progress = ref(0)
const progressStatus = ref<'success' | 'exception' | 'warning'>('success')
const currentProgressText = ref('')

// 操作结果
const operationResult = ref<any>(null)
const operationDetails = ref<any[]>([])
const dialogVisible = ref(false)

// 导出配置
const exportConfig = ref({
  format: 'pdf',
  range: 'all',
  fields: ['courseName', 'studentName', 'scores', 'comments']
})

// 申诉配置
const appealConfig = ref({
  type: '',
  reason: '',
  evidenceFiles: []
})

// 标记配置
const markConfig = ref({
  status: 'processed',
  remark: ''
})

// 下载配置
const downloadConfig = ref({
  resourceTypes: ['PPT课件', '视频教程'],
  downloadType: '打包下载'
})

// 模拟数据
onMounted(() => {
  // 初始化模拟数据
  allItems.value = [
    { id: '1', name: '《刑法学》2023-2024学年第一学期评价报告' },
    { id: '2', name: '《刑事诉讼法》2023-2024学年第一学期评价报告' },
    { id: '3', name: '《治安管理学》2023-2024学年第一学期评价报告' },
    { id: '4', name: '《犯罪心理学》2023-2024学年第一学期评价报告' },
    { id: '5', name: '《刑法学》2023-2024学年第二学期评价报告' },
    { id: '6', name: '《刑事诉讼法》2023-2024学年第二学期评价报告' },
    { id: '7', name: '《治安管理学》2023-2024学年第二学期评价报告' },
    { id: '8', name: '《犯罪心理学》2023-2024学年第二学期评价报告' },
    { id: '9', name: '《警察法学》2023-2024学年第一学期评价报告' },
    { id: '10', name: '《法理学》2023-2024学年第一学期评价报告' }
  ]
})

// 远程搜索项目
const remoteSearchItems = (query: string) => {
  loadingItems.value = true
  setTimeout(() => {
    filteredItems.value = allItems.value.filter(item => item.name.toLowerCase().includes(query.toLowerCase()))
    loadingItems.value = false
  }, 200)
}

// 处理批量类型变化
const handleBatchTypeChange = () => {
  selectedItems.value = []
}

// 获取配置标题
const getConfigTitle = () => {
  const titles = {
    export: '导出配置',
    appeal: '申诉配置',
    mark: '标记配置',
    download: '下载配置'
  }
  return titles[selectedBatchType.value as keyof typeof titles] || ''
}

// 获取操作按钮文本
const getActionButtonText = () => {
  const texts = {
    export: '批量导出',
    appeal: '批量提交',
    mark: '批量标记',
    download: '批量下载'
  }
  return texts[selectedBatchType.value as keyof typeof texts] || '执行操作'
}

// 能否执行操作
const canExecute = computed(() => {
  return selectedBatchType.value && selectedItems.value.length > 0
})

// 执行批量操作
const executeBatchOperation = () => {
  if (!canExecute.value) return
  
  isProcessing.value = true
  progress.value = 0
  currentProgressText.value = '开始准备批量操作...'
  
  // 模拟批量操作过程
  const totalSteps = selectedItems.value.length
  let currentStep = 0
  
  const processInterval = setInterval(() => {
    currentStep++
    progress.value = Math.min(100, Math.floor((currentStep / totalSteps) * 100))
    
    // 随机生成操作结果
    const success = Math.random() > 0.2
    const item = allItems.value.find(i => i.id === selectedItems.value[currentStep - 1])
    
    operationDetails.value.push({
      id: selectedItems.value[currentStep - 1],
      name: item?.name || '',
      status: success ? 'success' : 'error',
      message: success ? '操作成功' : '操作失败，请重试',
      time: new Date().toLocaleString()
    })
    
    currentProgressText.value = `正在处理第 ${currentStep}/${totalSteps} 项...`
    
    if (currentStep >= totalSteps) {
      clearInterval(processInterval)
      setTimeout(() => {
        progressStatus.value = operationDetails.value.every(d => d.status === 'success') ? 'success' : 'warning'
        
        const successCount = operationDetails.value.filter(d => d.status === 'success').length
        const errorCount = operationDetails.value.filter(d => d.status === 'error').length
        
        operationResult.value = {
          success: errorCount === 0,
          title: errorCount === 0 ? '批量操作成功完成' : '批量操作部分完成',
          subTitle: `共处理 ${totalSteps} 项，成功 ${successCount} 项，失败 ${errorCount} 项`
        }
        
        isProcessing.value = false
        currentProgressText.value = ''
      }, 500)
    }
  }, 500)
}

// 重置表单
const resetForm = () => {
  selectedBatchType.value = ''
  selectedItems.value = []
  filteredItems.value = []
  
  exportConfig.value = {
    format: 'pdf',
    range: 'all',
    fields: ['courseName', 'studentName', 'scores', 'comments']
  }
  
  appealConfig.value = {
    type: '',
    reason: '',
    evidenceFiles: []
  }
  
  markConfig.value = {
    status: 'processed',
    remark: ''
  }
  
  downloadConfig.value = {
    resourceTypes: ['PPT课件', '视频教程'],
    downloadType: '打包下载'
  }
  
  resetResult()
}

// 重置结果
const resetResult = () => {
  operationResult.value = null
  operationDetails.value = []
  dialogVisible.value = false
}

// 查看操作详情
const viewOperationDetails = () => {
  dialogVisible.value = true
}

// 下载操作报告
const downloadOperationReport = () => {
  // 模拟下载报告
  ElMessage.success('操作报告已开始下载')
}

// 处理对话框关闭
const handleDialogClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.batch-operation-tool {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.batch-tool-card {
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
}

.batch-tool-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.batch-tool-title {
  margin-left: 8px;
}

.batch-tool-content {
  padding: 20px 0;
}

.selection-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.selection-section .el-select {
  flex: 1;
  min-width: 250px;
}

.config-section {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.config-content {
  margin-top: 10px;
}

.action-section {
  display: flex;
  gap: 10px;
  margin: 20px 0;
  justify-content: center;
}

.progress-section {
  margin: 20px 0;
  padding: 20px;
  background-color: #f0f9eb;
  border-radius: 8px;
}

.progress-log {
  margin-top: 15px;
  text-align: center;
  color: #67c23a;
  font-size: 14px;
}

.result-section {
  margin-top: 20px;
}

.result-details {
  max-height: 500px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .selection-section {
    flex-direction: column;
  }
  
  .selection-section .el-select {
    width: 100%;
  }
  
  .action-section {
    flex-direction: column;
  }
  
  .action-section .el-button {
    width: 100%;
  }
}
</style>