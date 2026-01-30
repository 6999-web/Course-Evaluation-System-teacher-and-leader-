<template>
  <div class="offline-sync-manager">
    <!-- 离线状态指示器 -->
    <div class="offline-indicator" :class="{ 'online': isOnline, 'offline': !isOnline }">
      <div class="indicator-dot"></div>
      <span class="indicator-text">{{ isOnline ? '在线' : '离线' }}</span>
      <el-dropdown @command="handleSyncAction" v-if="!isOnline">
        <el-button type="text" size="small">
          <el-icon name="ArrowUpDown"></el-icon>同步
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :command="'manual-sync'">手动同步</el-dropdown-item>
            <el-dropdown-item :command="'view-queue'">查看同步队列</el-dropdown-item>
            <el-dropdown-item :command="'sync-settings'">同步设置</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    
    <!-- 离线操作同步管理器主卡片 -->
    <el-dialog v-model="showSyncManager" title="离线操作同步管理器" width="70%" :close-on-click-modal="false">
      <div class="sync-manager-content">
        <!-- 同步概览 -->
        <div class="sync-overview">
          <el-card class="overview-card" shadow="hover" size="small">
            <template #header>
              <div class="section-header">
                <el-icon name="DataLine"></el-icon>
                <span class="section-title">同步概览</span>
              </div>
            </template>
            
            <div class="overview-content">
              <div class="overview-stats">
                <div class="overview-stat-item">
                  <div class="stat-icon online" v-if="isOnline">
                    <el-icon name="CircleCheck"></el-icon>
                  </div>
                  <div class="stat-icon offline" v-else>
                    <el-icon name="CircleClose"></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">当前状态</div>
                    <div class="stat-value">{{ isOnline ? '在线' : '离线' }}</div>
                  </div>
                </div>
                <div class="overview-stat-item">
                  <div class="stat-icon">
                    <el-icon name="List"></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">待同步操作</div>
                    <div class="stat-value">{{ pendingOperations.length }}</div>
                  </div>
                </div>
                <div class="overview-stat-item">
                  <div class="stat-icon">
                    <el-icon name="Clock"></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">上次同步</div>
                    <div class="stat-value">{{ lastSyncTime || '从未同步' }}</div>
                  </div>
                </div>
                <div class="overview-stat-item">
                  <div class="stat-icon">
                    <el-icon name="Check"></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-label">今日已同步</div>
                    <div class="stat-value">{{ todaySyncCount }}项</div>
                  </div>
                </div>
              </div>
              
              <!-- 同步控制按钮 -->
              <div class="sync-control-buttons">
                <el-button type="primary" size="large" @click="startSync" :loading="isSyncing">
                  <el-icon name="Refresh"></el-icon>开始同步
                </el-button>
                <el-button type="warning" size="large" @click="clearSyncQueue" v-if="pendingOperations.length > 0">
                  <el-icon name="Delete"></el-icon>清空队列
                </el-button>
                <el-button type="success" size="large" @click="exportSyncHistory">
                  <el-icon name="Download"></el-icon>导出历史
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 同步队列和历史记录 -->
        <div class="sync-queue-history">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="同步队列" name="queue">
              <div class="queue-content">
                <div v-if="pendingOperations.length === 0" class="empty-state">
                  <el-empty description="暂无待同步操作" />
                </div>
                
                <div v-else class="operations-list">
                  <el-table :data="pendingOperations" style="width: 100%" border size="small">
                    <el-table-column prop="id" label="ID" width="80" />
                    <el-table-column prop="type" label="操作类型" width="120">
                      <template #default="scope">
                        <el-tag :type="getOperationTypeColor(scope.row.type)">{{ getOperationTypeName(scope.row.type) }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="操作描述" min-width="300" />
                    <el-table-column prop="timestamp" label="操作时间" width="180" />
                    <el-table-column prop="status" label="状态" width="100">
                      <template #default="scope">
                        <el-tag :type="scope.row.status === 'pending' ? 'warning' : 'danger'">
                          {{ scope.row.status === 'pending' ? '待同步' : '失败' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button type="text" size="small" @click="syncSingleOperation(scope.row.id)">
                          <el-icon name="ArrowUp"></el-icon>同步
                        </el-button>
                        <el-button type="text" size="small" @click="removeOperation(scope.row.id)" danger>
                          <el-icon name="Delete"></el-icon>删除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="同步历史" name="history">
              <div class="history-content">
                <el-table :data="syncHistory" style="width: 100%" border size="small">
                  <el-table-column prop="id" label="ID" width="80" />
                  <el-table-column prop="syncTime" label="同步时间" width="180" />
                  <el-table-column prop="totalOperations" label="操作总数" width="100" />
                  <el-table-column prop="successCount" label="成功" width="80">
                    <template #default="scope">
                      <el-tag type="success">{{ scope.row.successCount }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="failureCount" label="失败" width="80">
                    <template #default="scope">
                      <el-tag type="danger">{{ scope.row.failureCount }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="scope">
                      <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                        {{ scope.row.status === 'success' ? '成功' : '失败' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="100">
                    <template #default="scope">
                      <el-button type="text" size="small" @click="viewSyncDetails(scope.row.id)">
                        <el-icon name="View"></el-icon>详情
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
                
                <!-- 分页 -->
                <div class="history-pagination">
                  <el-pagination
                    v-model:current-page="historyCurrentPage"
                    v-model:page-size="historyPageSize"
                    :page-sizes="[10, 20, 50]"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="syncHistory.length"
                  ></el-pagination>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="同步设置" name="settings">
              <div class="settings-content">
                <el-form label-width="150px" size="large">
                  <el-form-item label="自动同步">
                    <el-switch v-model="autoSyncEnabled" />
                    <span class="switch-desc">连接网络后自动同步离线操作</span>
                  </el-form-item>
                  
                  <el-form-item label="同步间隔">
                    <el-input-number v-model="syncInterval" :min="5" :max="120" :step="5" />
                    <span class="input-desc">分钟</span>
                  </el-form-item>
                  
                  <el-form-item label="自动重试">
                    <el-switch v-model="autoRetryEnabled" />
                    <span class="switch-desc">同步失败后自动重试</span>
                  </el-form-item>
                  
                  <el-form-item label="最大重试次数">
                    <el-input-number v-model="maxRetryCount" :min="1" :max="10" :step="1" />
                    <span class="input-desc">次</span>
                  </el-form-item>
                  
                  <el-form-item label="保留历史记录">
                    <el-input-number v-model="historyRetentionDays" :min="1" :max="365" :step="1" />
                    <span class="input-desc">天</span>
                  </el-form-item>
                  
                  <el-form-item label="可离线使用功能">
                    <el-checkbox-group v-model="availableOfflineFeatures">
                      <el-checkbox :label="'查看评价报告'" />
                      <el-checkbox :label="'编写改进计划'" />
                      <el-checkbox :label="'记录教学笔记'" />
                      <el-checkbox :label="'查看个人档案'" />
                      <el-checkbox :label="'阅读教学资源'" />
                    </el-checkbox-group>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button type="primary" @click="saveSettings">保存设置</el-button>
                    <el-button @click="resetSettings">重置</el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- 操作日志 -->
        <div class="sync-logs-section">
          <el-card class="logs-card" shadow="hover" size="small">
            <template #header>
              <div class="section-header">
                <el-icon name="Message"></el-icon>
                <span class="section-title">操作日志</span>
                <el-button type="text" size="small" @click="clearLogs">清空</el-button>
              </div>
            </template>
            
            <div class="logs-content">
              <div 
                v-for="(log, index) in syncLogs.slice(-10)" 
                :key="index"
                class="log-item"
                :class="getLogLevelClass(log.level)"
              >
                <div class="log-time">{{ log.timestamp }}</div>
                <div class="log-level">{{ log.level }}</div>
                <div class="log-message">{{ log.message }}</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>
    
    <!-- 同步详情对话框 -->
    <el-dialog v-model="showSyncDetailsDialog" title="同步详情" width="70%">
      <div class="sync-details">
        <div v-if="selectedSyncHistory">
          <div class="sync-details-header">
            <div class="detail-item">
              <span class="detail-label">同步时间：</span>
              <span class="detail-value">{{ selectedSyncHistory.syncTime }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">操作总数：</span>
              <span class="detail-value">{{ selectedSyncHistory.totalOperations }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">成功：</span>
              <span class="detail-value success">{{ selectedSyncHistory.successCount }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">失败：</span>
              <span class="detail-value error">{{ selectedSyncHistory.failureCount }}</span>
            </div>
          </div>
          
          <div class="sync-details-operations">
            <h4>操作详情：</h4>
            <el-table :data="selectedSyncHistory.operations" style="width: 100%" border size="small">
              <el-table-column prop="type" label="操作类型" width="120" />
              <el-table-column prop="description" label="操作描述" min-width="300" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                    {{ scope.row.status === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="error" label="错误信息" min-width="300" v-if="selectedSyncHistory.failureCount > 0" />
            </el-table>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// 组件显示状态
const showSyncManager = ref(false)
const activeTab = ref('queue')

// 离线状态
const isOnline = ref(navigator.onLine)
const lastSyncTime = ref<string>('')
const todaySyncCount = ref(0)

// 同步状态
const isSyncing = ref(false)
const syncProgress = ref(0)

// 分页
const historyCurrentPage = ref(1)
const historyPageSize = ref(10)

// 待同步操作
const pendingOperations = ref([
  {
    id: 1,
    type: 'improvement',
    description: '更新了《刑法学》课程的改进计划',
    timestamp: '2024-01-20 10:30:25',
    status: 'pending',
    data: { /* 操作数据 */ },
    retryCount: 0
  },
  {
    id: 2,
    type: 'note',
    description: '添加了教学笔记：刑法案例分析',
    timestamp: '2024-01-20 11:15:42',
    status: 'pending',
    data: { /* 操作数据 */ },
    retryCount: 0
  },
  {
    id: 3,
    type: 'appeal',
    description: '提交了评分申诉：学生张三的评价',
    timestamp: '2024-01-20 14:20:18',
    status: 'pending',
    data: { /* 操作数据 */ },
    retryCount: 0
  }
])

// 同步历史记录
const syncHistory = ref([
  {
    id: 1,
    syncTime: '2024-01-19 16:45:32',
    totalOperations: 5,
    successCount: 4,
    failureCount: 1,
    status: 'success',
    operations: [
      { type: 'improvement', description: '更新改进计划', status: 'success', error: '' },
      { type: 'note', description: '添加教学笔记', status: 'success', error: '' },
      { type: 'appeal', description: '提交申诉', status: 'success', error: '' },
      { type: 'resource', description: '下载教学资源', status: 'success', error: '' },
      { type: 'report', description: '生成评价报告', status: 'failure', error: '服务器错误' }
    ]
  },
  {
    id: 2,
    syncTime: '2024-01-18 09:20:15',
    totalOperations: 3,
    successCount: 3,
    failureCount: 0,
    status: 'success',
    operations: [
      { type: 'improvement', description: '更新改进计划', status: 'success', error: '' },
      { type: 'note', description: '添加教学笔记', status: 'success', error: '' },
      { type: 'appeal', description: '提交申诉', status: 'success', error: '' }
    ]
  }
])

// 同步日志
const syncLogs = ref([
  { level: 'info', message: '系统初始化完成', timestamp: new Date().toLocaleString() },
  { level: 'info', message: '检测到网络连接', timestamp: new Date().toLocaleString() },
  { level: 'warn', message: '上次同步失败，存在3个待同步操作', timestamp: new Date().toLocaleString() }
])

// 设置
const autoSyncEnabled = ref(true)
const syncInterval = ref(30)
const autoRetryEnabled = ref(true)
const maxRetryCount = ref(3)
const historyRetentionDays = ref(30)
const availableOfflineFeatures = ref(['查看评价报告', '编写改进计划', '记录教学笔记', '查看个人档案', '阅读教学资源'])

// 同步详情对话框
const showSyncDetailsDialog = ref(false)
const selectedSyncHistory = ref<any>(null)

// 计算属性
// const filteredPendingOperations = computed(() => {
//   return pendingOperations.value.filter(op => op.status === 'pending')
// })

// 监听网络状态变化
const handleOnlineStatusChange = () => {
  isOnline.value = navigator.onLine
  addLog(isOnline.value ? 'info' : 'warn', isOnline.value ? '网络已连接' : '网络已断开')
  
  if (isOnline.value && autoSyncEnabled.value) {
    setTimeout(() => {
      startSync()
    }, 3000)
  }
}

// 开始同步
const startSync = () => {
  if (isOnline.value && pendingOperations.value.length > 0) {
    isSyncing.value = true
    syncProgress.value = 0
    
    addLog('info', `开始同步，共 ${pendingOperations.value.length} 个操作`)
    
    // 模拟同步过程
    const totalOperations = pendingOperations.value.length
    let currentOperation = 0
    const successfulOperations: any[] = []
    const failedOperations: any[] = []
    
    const syncInterval = setInterval(() => {
      if (currentOperation < totalOperations) {
        const operation = pendingOperations.value[currentOperation]
        
        // 模拟操作同步结果
        const success = Math.random() > 0.1 // 90%成功率
        
        if (success) {
          successfulOperations.push({
            type: operation.type,
            description: operation.description,
            status: 'success',
            error: ''
          })
          addLog('info', `成功同步操作：${operation.description}`)
        } else {
          failedOperations.push({
            type: operation.type,
            description: operation.description,
            status: 'failure',
            error: '服务器连接错误'
          })
          addLog('error', `同步操作失败：${operation.description} - 服务器连接错误`)
          
          // 更新重试次数
          operation.retryCount++
          if (operation.retryCount >= maxRetryCount.value) {
            operation.status = 'failed'
          }
        }
        
        currentOperation++
        syncProgress.value = Math.floor((currentOperation / totalOperations) * 100)
      } else {
        clearInterval(syncInterval)
        
        // 记录同步历史
        const syncRecord = {
          id: syncHistory.value.length + 1,
          syncTime: new Date().toLocaleString(),
          totalOperations,
          successCount: successfulOperations.length,
          failureCount: failedOperations.length,
          status: failedOperations.length === 0 ? 'success' : 'failure',
          operations: [...successfulOperations, ...failedOperations]
        }
        
        syncHistory.value.unshift(syncRecord)
        lastSyncTime.value = syncRecord.syncTime
        todaySyncCount.value += successfulOperations.length
        
        // 移除成功的操作
        pendingOperations.value = pendingOperations.value.filter(op => op.status !== 'pending' || op.retryCount >= maxRetryCount.value)
        
        isSyncing.value = false
        addLog('info', `同步完成，成功 ${successfulOperations.length} 个，失败 ${failedOperations.length} 个`)
        
        ElMessage.success(`同步完成，成功 ${successfulOperations.length} 个，失败 ${failedOperations.length} 个`)
      }
    }, 500)
  } else if (!isOnline.value) {
    ElMessage.warning('当前处于离线状态，无法同步')
  } else {
    ElMessage.info('没有待同步的操作')
  }
}

// 同步单个操作
const syncSingleOperation = (operationId: number) => {
  const operation = pendingOperations.value.find(op => op.id === operationId)
  if (operation) {
    isSyncing.value = true
    
    addLog('info', `开始同步单个操作：${operation.description}`)
    
    // 模拟同步过程
    setTimeout(() => {
      const success = Math.random() > 0.1 // 90%成功率
      
      if (success) {
        // 从队列中移除
        pendingOperations.value = pendingOperations.value.filter(op => op.id !== operationId)
        addLog('info', `成功同步操作：${operation.description}`)
        ElMessage.success('操作同步成功')
      } else {
        addLog('error', `同步操作失败：${operation.description} - 服务器连接错误`)
        ElMessage.error('操作同步失败')
      }
      
      isSyncing.value = false
    }, 1000)
  }
}

// 移除操作
const removeOperation = (operationId: number) => {
  pendingOperations.value = pendingOperations.value.filter(op => op.id !== operationId)
  addLog('warn', `移除了待同步操作：ID ${operationId}`)
  ElMessage.success('操作已移除')
}

// 清空同步队列
const clearSyncQueue = () => {
  pendingOperations.value = []
  addLog('warn', '清空了所有待同步操作')
  ElMessage.warning('已清空所有待同步操作')
}

// 导出同步历史
const exportSyncHistory = () => {
  const data = JSON.stringify(syncHistory.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `sync-history-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  addLog('info', '导出了同步历史记录')
  ElMessage.success('同步历史已导出')
}

// 查看同步详情
const viewSyncDetails = (syncId: number) => {
  selectedSyncHistory.value = syncHistory.value.find(history => history.id === syncId)
  if (selectedSyncHistory.value) {
    showSyncDetailsDialog.value = true
  }
}

// 保存设置
const saveSettings = () => {
  // 保存设置到 localStorage
  const settings = {
    autoSyncEnabled: autoSyncEnabled.value,
    syncInterval: syncInterval.value,
    autoRetryEnabled: autoRetryEnabled.value,
    maxRetryCount: maxRetryCount.value,
    historyRetentionDays: historyRetentionDays.value,
    availableOfflineFeatures: availableOfflineFeatures.value
  }
  
  localStorage.setItem('offlineSyncSettings', JSON.stringify(settings))
  addLog('info', '保存了同步设置')
  ElMessage.success('设置已保存')
}

// 重置设置
const resetSettings = () => {
  autoSyncEnabled.value = true
  syncInterval.value = 30
  autoRetryEnabled.value = true
  maxRetryCount.value = 3
  historyRetentionDays.value = 30
  availableOfflineFeatures.value = ['查看评价报告', '编写改进计划', '记录教学笔记', '查看个人档案', '阅读教学资源']
  
  addLog('warn', '重置了同步设置')
  ElMessage.info('设置已重置')
}

// 加载设置
const loadSettings = () => {
  const savedSettings = localStorage.getItem('offlineSyncSettings')
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings)
      autoSyncEnabled.value = settings.autoSyncEnabled
      syncInterval.value = settings.syncInterval
      autoRetryEnabled.value = settings.autoRetryEnabled
      maxRetryCount.value = settings.maxRetryCount
      historyRetentionDays.value = settings.historyRetentionDays
      availableOfflineFeatures.value = settings.availableOfflineFeatures
      addLog('info', '加载了保存的设置')
    } catch (error) {
      addLog('error', '加载设置失败：' + error)
    }
  }
}

// 添加日志
const addLog = (level: string, message: string) => {
  syncLogs.value.push({
    level,
    message,
    timestamp: new Date().toLocaleString()
  })
}

// 清空日志
const clearLogs = () => {
  syncLogs.value = []
  addLog('info', '清空了操作日志')
  ElMessage.success('日志已清空')
}

// 处理同步操作
const handleSyncAction = (command: string) => {
  switch (command) {
    case 'manual-sync':
      startSync()
      break
    case 'view-queue':
      showSyncManager.value = true
      activeTab.value = 'queue'
      break
    case 'sync-settings':
      showSyncManager.value = true
      activeTab.value = 'settings'
      break
  }
}

// 获取操作类型名称
const getOperationTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'improvement': '改进计划',
    'note': '教学笔记',
    'appeal': '申诉',
    'resource': '资源操作',
    'report': '报告操作'
  }
  return typeMap[type] || type
}

// 获取操作类型颜色
const getOperationTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'improvement': 'success',
    'note': 'primary',
    'appeal': 'warning',
    'resource': 'info',
    'report': 'danger'
  }
  return colorMap[type] || 'default'
}

// 获取日志级别样式
const getLogLevelClass = (level: string) => {
  return `log-${level}`
}

// 获取日志级别样式
// const getLogLevelText = (level: string) => {
//   const levelMap: Record<string, string> = {
//     'info': '信息',
//     'warn': '警告',
//     'error': '错误'
//   }
//   return levelMap[level] || level
// }

// 生命周期钩子
onMounted(() => {
  // 监听网络状态变化
  window.addEventListener('online', handleOnlineStatusChange)
  window.addEventListener('offline', handleOnlineStatusChange)
  
  // 加载设置
  loadSettings()
  
  // 初始化日志
  addLog('info', '离线同步管理器已初始化')
  
  // 检查上次同步时间
  if (syncHistory.value.length > 0) {
    lastSyncTime.value = syncHistory.value[0].syncTime
  }
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnlineStatusChange)
  window.removeEventListener('offline', handleOnlineStatusChange)
})

// 将组件暴露给父组件
const toggleSyncManager = () => {
  showSyncManager.value = !showSyncManager.value
}

defineExpose({
  toggleSyncManager
})
</script>

<style scoped>
.offline-sync-manager {
  position: relative;
}

/* 离线状态指示器 */
.offline-indicator {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 8px 15px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.offline-indicator:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.offline-indicator.online {
  background-color: #f0f9eb;
  color: #67c23a;
}

.offline-indicator.offline {
  background-color: #fef0f0;
  color: #f56c6c;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.indicator-text {
  font-size: 14px;
  font-weight: bold;
}

/* 同步管理器内容 */
.sync-manager-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 概览卡片 */
.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.overview-stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.overview-stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-icon.online {
  background-color: #67c23a;
}

.stat-icon.offline {
  background-color: #f56c6c;
}

.stat-icon.default {
  background-color: #409eff;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.sync-control-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

/* 同步队列和历史记录 */
.sync-queue-history {
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 50px 0;
}

/* 设置部分 */
.settings-content {
  margin-top: 10px;
}

.switch-desc, .input-desc {
  margin-left: 10px;
  color: #909399;
  font-size: 14px;
}

/* 日志部分 */
.logs-content {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.log-item {
  display: flex;
  gap: 10px;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.log-time {
  color: #909399;
  width: 150px;
}

.log-level {
  font-weight: bold;
  width: 50px;
  text-align: center;
}

.log-message {
  flex: 1;
}

.log-info {
  background-color: #f0f9eb;
  color: #67c23a;
}

.log-warn {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.log-error {
  background-color: #fef0f0;
  color: #f56c6c;
}

/* 历史记录分页 */
.history-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 同步详情 */
.sync-details-header {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.detail-label {
  font-weight: bold;
  color: #606266;
}

.detail-value {
  color: #303133;
}

.detail-value.success {
  color: #67c23a;
  font-weight: bold;
}

.detail-value.error {
  color: #f56c6c;
  font-weight: bold;
}

.sync-details-operations {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .sync-control-buttons {
    flex-direction: column;
  }
  
  .sync-control-buttons .el-button {
    width: 100%;
  }
}
</style>