<template>
  <div class="resource-recommendation">
    <!-- 资源推荐卡片 -->
    <div v-if="showRecommendation" class="recommendation-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon name="Star" class="title-icon" />
          教学资源推荐
        </div>
        <el-button type="text" @click="showRecommendation = false">
          <el-icon name="Close" />
        </el-button>
      </div>
      <div class="card-content">
        <div class="recommendation-info">
          <p class="recommendation-text">
            基于您的评教结果，发现您在 <span class="highlight">{{ lowScoreDimension }}</span> 维度得分较低，
            为您推荐以下针对性教学资源：
          </p>
        </div>
        <div class="resource-list">
          <div 
            v-for="resource in recommendedResources" 
            :key="resource.id"
            class="resource-item"
            @click="selectResource(resource)"
          >
            <div class="resource-icon" :class="resource.iconColor">
              <el-icon :name="resource.iconName" />
            </div>
            <div class="resource-info">
              <div class="resource-title">{{ resource.title }}</div>
              <div class="resource-meta">
                <span class="resource-type">{{ resource.type }}</span>
                <span class="resource-difficulty" :class="resource.difficulty.toLowerCase()">
                  {{ resource.difficulty }}
                </span>
                <span class="resource-views">
                  <el-icon name="View" /> {{ resource.views }}
                </span>
              </div>
              <div class="resource-description">{{ resource.description }}</div>
            </div>
            <div class="resource-actions">
              <el-button type="primary" size="small" @click.stop="downloadResource(resource)">
                <el-icon name="Download" /> 下载
              </el-button>
              <el-button type="success" size="small" @click.stop="importToImprovement(resource)">
                <el-icon name="CirclePlus" /> 导入
              </el-button>
              <el-button type="warning" size="small" @click.stop="decodeResource(resource)">
                <el-icon name="MagicStick" /> 解码
              </el-button>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <el-button type="text" @click="viewAllResources">
            <el-icon name="ArrowRight" /> 查看更多资源
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 教学资源解码器 -->
    <ResourceDecoder 
      :resource="decodingResource" 
      @open-resource-library="viewAllResources"
    />

    <!-- 资源库弹窗 -->
    <el-dialog
      v-model="resourceLibraryVisible"
      title="教学资源库"
      width="80%"
      class="resource-library-dialog"
    >
      <!-- 搜索和筛选 -->
      <div class="resource-search">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索资源名称或描述"
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon name="Search" />
          </template>
        </el-input>
        <div class="resource-filters">
          <el-select v-model="typeFilter" placeholder="课程类型" class="filter-select">
            <el-option label="全部" value="" />
            <el-option v-for="type in courseTypes" :key="type" :label="type" :value="type" />
          </el-select>
          <el-select v-model="difficultyFilter" placeholder="难度等级" class="filter-select">
            <el-option label="全部" value="" />
            <el-option v-for="difficulty in difficulties" :key="difficulty" :label="difficulty" :value="difficulty" />
          </el-select>
          <el-button type="primary" @click="resetFilters">
            <el-icon name="Refresh" /> 重置
          </el-button>
        </div>
      </div>

      <!-- 资源列表 -->
      <div class="resource-library-content">
        <el-table
          v-loading="loading"
          :data="filteredResources"
          style="width: 100%"
          :default-sort="{ prop: 'views', order: 'descending' }"
          stripe
        >
          <el-table-column prop="title" label="资源名称" min-width="200">
            <template #default="scope">
              <div class="table-resource-title">
                <div class="resource-icon-small" :class="scope.row.iconColor">
                  <el-icon :name="scope.row.iconName" />
                </div>
                {{ scope.row.title }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="课程类型" width="120" />
          <el-table-column prop="difficulty" label="难度等级" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.difficulty.toLowerCase()">
                {{ scope.row.difficulty }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
          <el-table-column prop="views" label="浏览量" width="100" sortable />
          <el-table-column prop="updateTime" label="更新时间" width="150" sortable />
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="downloadResource(scope.row)">
                <el-icon name="Download" /> 下载
              </el-button>
              <el-button type="success" size="small" @click="importToImprovement(scope.row)">
                <el-icon name="CirclePlus" /> 导入
              </el-button>
              <el-button type="text" size="small" @click="previewResource(scope.row)">
                <el-icon name="View" /> 预览
              </el-button>
              <el-button type="warning" size="small" @click="decodeResource(scope.row)">
                <el-icon name="MagicStick" /> 解码
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="resource-pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredResources.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-dialog>

    <!-- 资源预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      :title="currentResource?.title || '资源预览'"
      width="80%"
      class="resource-preview-dialog"
    >
      <div v-if="currentResource" class="resource-preview">
        <div class="preview-header">
          <div class="preview-meta">
            <el-tag>{{ currentResource.type }}</el-tag>
            <el-tag :type="currentResource.difficulty.toLowerCase()">
              {{ currentResource.difficulty }}
            </el-tag>
            <span class="preview-views">
              <el-icon name="View" /> {{ currentResource.views }}
            </span>
            <span class="preview-update">
              更新于：{{ currentResource.updateTime }}
            </span>
          </div>
        </div>
        <div class="preview-content">
          <div class="preview-description">
            <h4>资源简介</h4>
            <p>{{ currentResource.description }}</p>
          </div>
          <div class="preview-details">
            <h4>资源详情</h4>
            <div class="detail-item">
              <span class="detail-label">适用课程：</span>
              <span class="detail-value">{{ currentResource.applicableCourses }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">资源格式：</span>
              <span class="detail-value">{{ currentResource.format }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">资源大小：</span>
              <span class="detail-value">{{ currentResource.size }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">上传者：</span>
              <span class="detail-value">{{ currentResource.uploader }}</span>
            </div>
          </div>
          <div class="preview-samples">
            <h4>资源示例</h4>
            <div class="sample-content">
              <div class="sample-placeholder">
                <el-icon name="Document" class="placeholder-icon" />
                <p>资源预览功能开发中...</p>
                <p>请下载后查看完整内容</p>
              </div>
            </div>
          </div>
        </div>
        <div class="preview-footer">
          <el-button type="primary" size="large" @click="downloadResource(currentResource)">
            <el-icon name="Download" /> 下载资源
          </el-button>
          <el-button type="success" size="large" @click="importToImprovement(currentResource)">
            <el-icon name="CirclePlus" /> 导入到改进计划
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ResourceDecoder from '@/components/ResourceDecoder.vue'

// 组件属性
const props = defineProps<{
  lowScoreDimension?: string;
  show?: boolean;
}>()

// 组件事件
const emit = defineEmits<{
  importResource: [resource: any];
  close: [];
}>()

// 状态变量
const showRecommendation = ref(props.show !== undefined ? props.show : true)
const lowScoreDimension = ref(props.lowScoreDimension || '教学案例')
const resourceLibraryVisible = ref(false)
const previewVisible = ref(false)
const searchKeyword = ref('')
const typeFilter = ref('')
const difficultyFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const currentResource = ref<any>(null)
const decodingResource = ref<any>(null)

// 课程类型
const courseTypes = ref(['所有课程', '基础课程', '专业课程', '实训课程', '选修课程'])

// 难度等级
const difficulties = ref(['所有难度', '初级', '中级', '高级'])

// 推荐资源（模拟数据）
const recommendedResources = ref([
  {
    id: 1,
    title: '现代教学案例设计指南',
    type: '专业课程',
    difficulty: '中级',
    views: 1258,
    description: '包含100+个实用教学案例，覆盖多种教学场景，提升教学方法多样性。',
    iconName: 'Document',
    iconColor: 'primary',
    applicableCourses: '所有专业课程',
    format: 'PDF',
    size: '2.5MB',
    uploader: '教务处教学资源中心',
    updateTime: '2026-01-15'
  },
  {
    id: 2,
    title: '互动式教学技巧视频课程',
    type: '实训课程',
    difficulty: '初级',
    views: 2345,
    description: '通过视频演示各种互动教学技巧，帮助教师提升课堂参与度。',
    iconName: 'VideoCamera',
    iconColor: 'warning',
    applicableCourses: '所有实训课程',
    format: 'MP4',
    size: '45.2MB',
    uploader: '教育技术中心',
    updateTime: '2026-01-10'
  },
  {
    id: 3,
    title: '创新教学方法PPT模板',
    type: '基础课程',
    difficulty: '初级',
    views: 3456,
    description: '精美的PPT模板，包含多种教学方法的演示结构，直接可用。',
    iconName: 'Notebook',
    iconColor: 'success',
    applicableCourses: '所有基础课程',
    format: 'PPTX',
    size: '15.8MB',
    uploader: '教师发展中心',
    updateTime: '2026-01-05'
  },
  {
    id: 4,
    title: '案例教学法实施手册',
    type: '专业课程',
    difficulty: '高级',
    views: 987,
    description: '详细介绍案例教学法的实施步骤、注意事项和评估方法。',
    iconName: 'Document',
    iconColor: 'primary',
    applicableCourses: '所有专业课程',
    format: 'PDF',
    size: '3.2MB',
    uploader: '教学质量监控中心',
    updateTime: '2025-12-28'
  }
])

// 所有资源（模拟数据）
const allResources = ref([
  ...recommendedResources.value,
  {
    id: 5,
    title: '小组讨论教学组织技巧',
    type: '基础课程',
    difficulty: '中级',
    views: 1876,
    description: '如何有效组织小组讨论，提高学生参与度和学习效果。',
    iconName: 'UserFilled',
    iconColor: 'info',
    applicableCourses: '所有基础课程',
    format: 'PDF',
    size: '1.8MB',
    uploader: '教师发展中心',
    updateTime: '2025-12-20'
  },
  {
    id: 6,
    title: '翻转课堂教学模式设计',
    type: '专业课程',
    difficulty: '高级',
    views: 1567,
    description: '翻转课堂的设计理念、实施步骤和效果评估方法。',
    iconName: 'SwitchButton',
    iconColor: 'success',
    applicableCourses: '所有专业课程',
    format: 'PDF',
    size: '2.1MB',
    uploader: '教育技术中心',
    updateTime: '2025-12-15'
  },
  {
    id: 7,
    title: '多媒体课件制作教程',
    type: '基础课程',
    difficulty: '初级',
    views: 2890,
    description: '从零开始学习多媒体课件制作，包含PPT、动画、音频等制作技巧。',
    iconName: 'Monitor',
    iconColor: 'warning',
    applicableCourses: '所有基础课程',
    format: 'MP4',
    size: '67.5MB',
    uploader: '教育技术中心',
    updateTime: '2025-12-10'
  },
  {
    id: 8,
    title: '课堂提问艺术与策略',
    type: '所有课程',
    difficulty: '中级',
    views: 2134,
    description: '如何设计有效的课堂提问，激发学生思考和参与。',
    iconName: 'ChatDotRound',
    iconColor: 'primary',
    applicableCourses: '所有课程',
    format: 'PDF',
    size: '1.5MB',
    uploader: '教务处教学资源中心',
    updateTime: '2025-12-05'
  }
])

// 筛选后的资源
const filteredResources = computed(() => {
  return allResources.value.filter(resource => {
    const matchesKeyword = resource.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    const matchesType = typeFilter.value ? resource.type === typeFilter.value : true
    const matchesDifficulty = difficultyFilter.value ? resource.difficulty === difficultyFilter.value : true
    return matchesKeyword && matchesType && matchesDifficulty
  })
})

// 分页后的资源
// const paginatedResources = computed(() => {
//   const startIndex = (currentPage.value - 1) * pageSize.value
//   return filteredResources.value.slice(startIndex, startIndex + pageSize.value)
// })

// 选择资源
const selectResource = (resource: any) => {
  currentResource.value = resource
  previewVisible.value = true
}

// 下载资源
const downloadResource = (resource: any) => {
  // 模拟下载
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success(`开始下载：${resource.title}`)
    
    // 添加到缓存
    addToCache(resource)
  }, 1000)
}

// 添加到缓存
const addToCache = (resource: any) => {
  const cacheItem = {
    ...resource,
    category: '教学资源',
    downloadDate: new Date().toISOString()
  }
  
  // 保存到localStorage
  const cachedData = localStorage.getItem('teachingSystemCache')
  const cacheArray = cachedData ? JSON.parse(cachedData) : []
  
  // 检查是否已存在
  const existingIndex = cacheArray.findIndex((item: any) => item.id === resource.id)
  if (existingIndex > -1) {
    // 更新现有项
    cacheArray[existingIndex] = cacheItem
  } else {
    // 添加新项
    cacheArray.unshift(cacheItem)
  }
  
  localStorage.setItem('teachingSystemCache', JSON.stringify(cacheArray))
  ElMessage.info(`资源已添加到缓存`)
}

// 导入资源
const importToImprovement = (resource: any) => {
  emit('importResource', resource)
  ElMessage.success(`资源"${resource.title}"已成功导入到改进计划`)
  if (resourceLibraryVisible.value) {
    resourceLibraryVisible.value = false
  }
  if (previewVisible.value) {
    previewVisible.value = false
  }
}

// 预览资源
const previewResource = (resource: any) => {
  currentResource.value = resource
  previewVisible.value = true
}

// 解码资源
const decodeResource = (resource: any) => {
  decodingResource.value = resource
  // 滚动到解码器位置
  setTimeout(() => {
    const decoderElement = document.querySelector('.resource-decoder')
    if (decoderElement) {
      decoderElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 100)
}

// 查看所有资源
const viewAllResources = () => {
  resourceLibraryVisible.value = true
}

// 重置筛选条件
const resetFilters = () => {
  searchKeyword.value = ''
  typeFilter.value = ''
  difficultyFilter.value = ''
  currentPage.value = 1
}

// 分页处理
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
}

// 监听属性变化
onMounted(() => {
  if (props.lowScoreDimension) {
    lowScoreDimension.value = props.lowScoreDimension
  }
  if (props.show) {
    showRecommendation.value = props.show
  }
})
</script>

<style scoped>
.resource-recommendation {
  position: relative;
  z-index: 100;
}

/* 推荐卡片样式 */
.recommendation-card {
  background: linear-gradient(135deg, rgba(255, 240, 180, 0.95) 0%, rgba(255, 250, 220, 0.9) 100%);
  border: 2px solid rgba(255, 220, 120, 0.5);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: linear-gradient(135deg, #ffd04b, #ffc107);
  color: white;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.title-icon {
  margin-right: 8px;
  font-size: 20px;
}

.card-content {
  padding: 20px;
}

.recommendation-info {
  margin-bottom: 20px;
}

.recommendation-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.highlight {
  color: #f56c6c;
  font-weight: bold;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.resource-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.resource-item:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.resource-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
}

.resource-icon.primary {
  background: #409eff;
}

.resource-icon.success {
  background: #67c23a;
}

.resource-icon.warning {
  background: #e6a23c;
}

.resource-icon.info {
  background: #909399;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resource-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
  flex-wrap: wrap;
}

.resource-type {
  font-size: 12px;
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.resource-difficulty {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}

.resource-difficulty.primary {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.resource-difficulty.success {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.resource-difficulty.warning {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.resource-difficulty.info {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.resource-views {
  font-size: 12px;
  color: #909399;
}

.resource-description {
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

.resource-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.card-footer {
  text-align: right;
  padding-top: 15px;
  border-top: 1px dashed #e4e7ed;
}

/* 资源库弹窗 */
.resource-search {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.search-input {
  width: 300px;
}

.resource-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-select {
  width: 150px;
}

.resource-library-content {
  max-height: 600px;
  overflow-y: auto;
}

.resource-pagination {
  margin-top: 20px;
  text-align: right;
}

/* 资源预览弹窗 */
.preview-header {
  margin-bottom: 20px;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.preview-views, .preview-update {
  font-size: 14px;
  color: #909399;
}

.preview-content {
  margin-bottom: 30px;
}

.preview-content h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
  border-bottom: 2px solid #e4e7ed;
  padding-bottom: 5px;
}

.preview-content p {
  margin: 0 0 15px 0;
  line-height: 1.6;
  color: #606266;
}

.detail-item {
  margin-bottom: 10px;
}

.detail-label {
  font-weight: bold;
  color: #303133;
  margin-right: 10px;
}

.detail-value {
  color: #606266;
}

.sample-content {
  padding: 30px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;
}

.sample-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.placeholder-icon {
  font-size: 48px;
  color: #909399;
}

.preview-footer {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px dashed #e4e7ed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .resource-search {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .resource-filters {
    justify-content: center;
  }
  
  .resource-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .resource-actions {
    margin-top: 10px;
    justify-content: flex-end;
  }
}
</style>