<template>
  <div class="cache-manager">
    <!-- 缓存管理标题 -->
    <div class="cache-header">
      <el-icon name="DownloadFilled" class="header-icon" />
      <h3>我的缓存</h3>
      <p class="cache-description">管理您下载的所有教学资源，按来源分类展示</p>
    </div>
    
    <!-- 缓存统计 -->
    <div class="cache-stats">
      <el-card v-for="stat in cacheStats" :key="stat.type" class="stat-card">
        <div class="stat-content">
          <div class="stat-number">{{ stat.count }}</div>
          <div class="stat-label">{{ stat.type }}</div>
        </div>
      </el-card>
    </div>
    
    <!-- 分类导航 -->
    <div class="category-nav">
      <el-tabs v-model="activeCategory" @tab-click="handleCategoryChange">
        <el-tab-pane label="全部" name="all">
          <template #icon>
            <el-icon name="Menu" />
          </template>
        </el-tab-pane>
        <el-tab-pane v-for="category in cacheCategories" :key="category" :label="category" :name="category">
          <template #icon>
            <el-icon :name="categoryIcons[category] || 'Document'" />
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 缓存内容列表 -->
    <div class="cache-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon name="Loading" class="loading-icon" />
        <span>加载中...</span>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="filteredCache.length === 0" class="empty-state">
        <el-icon name="DocumentRemove" class="empty-icon" />
        <p>暂无缓存内容</p>
        <el-button type="primary" @click="$emit('openResourceLibrary')">
          <el-icon name="DocumentCopy" /> 浏览资源库
        </el-button>
      </div>
      
      <!-- 缓存列表 -->
      <div v-else class="cache-list">
        <div 
          v-for="item in filteredCache" 
          :key="item.id"
          class="cache-item"
        >
          <div class="cache-item-icon" :class="getItemIconClass(item.category)">
            <el-icon :name="getItemIcon(item.category)" />
          </div>
          <div class="cache-item-info">
            <div class="cache-item-title">{{ item.title }}</div>
            <div class="cache-item-meta">
              <span class="cache-item-category">{{ item.category }}</span>
              <span class="cache-item-date">{{ formatDate(item.downloadDate) }}</span>
              <span class="cache-item-size">{{ item.size || '未知' }}</span>
            </div>
            <div class="cache-item-description">{{ item.description }}</div>
          </div>
          <div class="cache-item-actions">
            <el-button type="primary" size="small" @click="viewCacheItem(item)">
              <el-icon name="View" /> 查看
            </el-button>
            <el-button type="warning" size="small" @click="openCacheItem(item)">
              <el-icon name="Folder" /> 打开
            </el-button>
            <el-button type="danger" size="small" @click="deleteCacheItem(item.id)">
              <el-icon name="Delete" /> 删除
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div v-if="filteredCache.length > 0" class="cache-pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredCache.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    
    <!-- 缓存管理操作 -->
    <div class="cache-actions">
      <el-button type="danger" @click="clearAllCache" :disabled="totalCacheCount === 0">
        <el-icon name="Delete" /> 清空所有缓存
      </el-button>
      <el-button type="warning" @click="clearCategoryCache" :disabled="filteredCache.length === 0">
        <el-icon name="Delete" /> 清空当前分类
      </el-button>
      <el-button type="info" @click="exportCacheData">
        <el-icon name="Share" /> 导出缓存记录
      </el-button>
    </div>
    
    <!-- 缓存详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentCacheItem?.title || '缓存详情'"
      width="70%"
      class="cache-detail-dialog"
    >
      <div v-if="currentCacheItem" class="cache-detail">
        <div class="detail-header">
          <div class="detail-meta">
            <el-tag>{{ currentCacheItem.category }}</el-tag>
            <span class="detail-date">下载时间：{{ formatDate(currentCacheItem.downloadDate) }}</span>
            <span class="detail-size">大小：{{ currentCacheItem.size || '未知' }}</span>
          </div>
        </div>
        <div class="detail-content">
          <div class="detail-section">
            <h4>资源描述</h4>
            <p>{{ currentCacheItem.description }}</p>
          </div>
          <div class="detail-section">
            <h4>资源详情</h4>
            <div class="detail-info">
              <div class="info-item">
                <span class="info-label">来源：</span>
                <span class="info-value">{{ currentCacheItem.source || '系统资源库' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">文件格式：</span>
                <span class="info-value">{{ currentCacheItem.format || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">适用课程：</span>
                <span class="info-value">{{ currentCacheItem.applicableCourses || '所有课程' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">难度等级：</span>
                <span class="info-value">{{ currentCacheItem.difficulty || '未知' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 组件事件
// const emit = defineEmits<{
//   openResourceLibrary: [];
// }>()

// 状态变量
const activeCategory = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const detailVisible = ref(false)
const currentCacheItem = ref<any>(null)
const cacheData = ref<any[]>([])

// 分类图标映射
const categoryIcons: Record<string, string> = {
  '教学资源': 'DocumentCopy',
  '批量操作': 'Operation',
  '个人档案': 'UserFilled',
  '评教趋势': 'DataLine',
  '经验交流': 'ChatRound'
}

// 初始化缓存数据
onMounted(() => {
  loadCacheData()
})

// 加载缓存数据
const loadCacheData = () => {
  loading.value = true
  setTimeout(() => {
    const cachedData = localStorage.getItem('teachingSystemCache')
    if (cachedData) {
      cacheData.value = JSON.parse(cachedData)
    } else {
      cacheData.value = []
    }
    loading.value = false
  }, 500)
}

// 保存缓存数据
const saveCacheData = () => {
  localStorage.setItem('teachingSystemCache', JSON.stringify(cacheData.value))
}

// 缓存分类
const cacheCategories = computed(() => {
  const categories = new Set<string>()
  cacheData.value.forEach(item => {
    categories.add(item.category)
  })
  return Array.from(categories)
})

// 缓存统计
const cacheStats = computed(() => {
  const stats: any[] = []
  const categoryCounts: { [key: string]: number } = {}
  
  cacheData.value.forEach(item => {
    if (categoryCounts[item.category]) {
      categoryCounts[item.category]++
    } else {
      categoryCounts[item.category] = 1
    }
  })
  
  Object.entries(categoryCounts).forEach(([category, count]) => {
    stats.push({ type: category, count })
  })
  
  return stats
})

// 总缓存数量
const totalCacheCount = computed(() => {
  return cacheData.value.length
})

// 筛选后的缓存
const filteredCache = computed(() => {
  if (activeCategory.value === 'all') {
    return cacheData.value
  }
  return cacheData.value.filter(item => item.category === activeCategory.value)
})

// 分页后的缓存
// const paginatedCache = computed(() => {
//   const start = (currentPage.value - 1) * pageSize.value
//   const end = start + pageSize.value
//   return filteredCache.value.slice(start, end)
// })

// 处理分类切换
const handleCategoryChange = () => {
  currentPage.value = 1
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 获取项目图标
const getItemIcon = (category: string) => {
  return categoryIcons[category] || 'Document'
}

// 获取项目图标样式
const getItemIconClass = (category: string) => {
  const colorMap: { [key: string]: string } = {
    '教学资源': 'primary',
    '批量操作': 'warning',
    '个人档案': 'success',
    '评教趋势': 'info',
    '经验交流': 'danger'
  }
  return colorMap[category] || 'info'
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 查看缓存项
const viewCacheItem = (item: any) => {
  currentCacheItem.value = item
  detailVisible.value = true
}

// 打开缓存项
const openCacheItem = (item: any) => {
  ElMessage.success(`正在打开：${item.title}`)
  // 这里可以添加实际的文件打开逻辑
}

// 删除缓存项
const deleteCacheItem = (id: string) => {
  ElMessageBox.confirm('确定要删除这个缓存项吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = cacheData.value.findIndex(item => item.id === id)
    if (index > -1) {
      cacheData.value.splice(index, 1)
      saveCacheData()
      ElMessage.success('删除成功')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 清空所有缓存
const clearAllCache = () => {
  ElMessageBox.confirm('确定要清空所有缓存吗？此操作不可恢复。', '清空确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'error'
  }).then(() => {
    cacheData.value = []
    saveCacheData()
    ElMessage.success('所有缓存已清空')
  }).catch(() => {
    // 取消清空
  })
}

// 清空当前分类缓存
const clearCategoryCache = () => {
  ElMessageBox.confirm(`确定要清空"${activeCategory.value}"分类的所有缓存吗？`, '清空确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    if (activeCategory.value === 'all') {
      cacheData.value = []
    } else {
      cacheData.value = cacheData.value.filter(item => item.category !== activeCategory.value)
    }
    saveCacheData()
    ElMessage.success('缓存已清空')
  }).catch(() => {
    // 取消清空
  })
}

// 导出缓存数据
const exportCacheData = () => {
  const exportData = JSON.stringify(cacheData.value, null, 2)
  const blob = new Blob([exportData], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `cache-export-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('缓存数据导出成功')
}

// 外部方法：添加缓存项
defineExpose({
  addCacheItem: (item: any) => {
    const newItem = {
      ...item,
      id: `cache-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      downloadDate: new Date().toISOString(),
      category: item.category || '教学资源'
    }
    cacheData.value.unshift(newItem)
    saveCacheData()
    return newItem
  },
  loadCacheData
})
</script>

<style scoped>
.cache-manager {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.cache-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.header-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 10px;
  display: block;
}

.cache-header h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #0f4c81;
  font-weight: bold;
}

.cache-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.cache-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.category-nav {
  margin-bottom: 20px;
}

.category-nav .el-tabs__header {
  margin-bottom: 0;
}

.cache-content {
  min-height: 400px;
  margin-bottom: 20px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-icon,
.empty-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 20px;
}

.loading-state span,
.empty-state p {
  color: #606266;
  margin-bottom: 20px;
}

.cache-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cache-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.cache-item:hover {
  background: #f0f9ff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.cache-item-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.cache-item-icon.primary {
  background: #409eff;
}

.cache-item-icon.success {
  background: #67c23a;
}

.cache-item-icon.warning {
  background: #e6a23c;
}

.cache-item-icon.danger {
  background: #f56c6c;
}

.cache-item-icon.info {
  background: #909399;
}

.cache-item-info {
  flex: 1;
  min-width: 0;
}

.cache-item-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cache-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.cache-item-category {
  font-size: 12px;
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.cache-item-date,
.cache-item-size {
  font-size: 12px;
  color: #909399;
}

.cache-item-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cache-item-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.cache-pagination {
  margin-top: 20px;
  text-align: right;
}

.cache-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #e4e7ed;
}

.cache-detail {
  padding: 20px;
}

.detail-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.detail-date,
.detail-size {
  font-size: 14px;
  color: #909399;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.detail-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-label {
  font-weight: bold;
  color: #303133;
  white-space: nowrap;
  min-width: 100px;
}

.info-value {
  color: #606266;
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cache-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cache-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .cache-item-actions {
    margin-top: 10px;
    justify-content: flex-end;
  }
  
  .cache-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .detail-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>