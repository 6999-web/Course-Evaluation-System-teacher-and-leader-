<template>
  <div class="resource-decoder">
    <!-- 解码器标题 -->
    <div class="decoder-header">
      <el-icon name="MagicStick" class="header-icon" />
      <h3>教学资源解码器</h3>
      <p class="decoder-description">智能分析教学资源，提取关键信息，为您提供个性化解读</p>
    </div>
    
    <!-- 解码器内容 -->
    <div class="decoder-content">
      <!-- 资源分析 -->
      <div v-if="currentResource" class="resource-analysis">
        <div class="analysis-section">
          <h4><el-icon name="DataAnalysis" /> 资源分析</h4>
          <div class="analysis-result">
            <div class="analysis-item">
              <span class="analysis-label">资源类型：</span>
              <span class="analysis-value">{{ currentResource.type }}</span>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">适用课程：</span>
              <span class="analysis-value">{{ currentResource.applicableCourses }}</span>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">难度等级：</span>
              <span class="analysis-value">{{ currentResource.difficulty }}</span>
            </div>
            <div class="analysis-item">
              <span class="analysis-label">预计学习时间：</span>
              <span class="analysis-value">{{ estimatedLearningTime }} 分钟</span>
            </div>
          </div>
        </div>
        
        <!-- 关键信息提取 -->
        <div class="analysis-section">
          <h4><el-icon name="InfoFilled" /> 关键信息提取</h4>
          <div class="key-info">
            <el-tag v-for="keyword in keyKeywords" :key="keyword" size="small" class="keyword-tag">
              {{ keyword }}
            </el-tag>
          </div>
        </div>
        
        <!-- 教学建议 -->
        <div class="analysis-section">
          <h4><el-icon name="Star" /> 个性化教学建议</h4>
          <div class="teaching-suggestions">
            <el-card v-for="(suggestion, index) in teachingSuggestions" :key="index" class="suggestion-card">
              <template #header>
                <div class="suggestion-header">
                  <el-icon :name="suggestion.icon" />
                  <span>{{ suggestion.title }}</span>
                </div>
              </template>
              <p>{{ suggestion.content }}</p>
            </el-card>
          </div>
        </div>
        
        <!-- 资源使用场景 -->
        <div class="analysis-section">
          <h4><el-icon name="Position" /> 推荐使用场景</h4>
          <div class="usage-scenarios">
            <div v-for="(scenario, index) in usageScenarios" :key="index" class="scenario-item">
              <el-checkbox v-model="scenario.selected" :disabled="true">
                {{ scenario.name }}
              </el-checkbox>
              <div class="scenario-description">{{ scenario.description }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 未选择资源时的提示 -->
      <div v-else class="no-resource">
        <el-icon name="DocumentRemove" class="no-resource-icon" />
        <p>请选择一个教学资源进行解码分析</p>
        <el-button type="primary" @click="$emit('openResourceLibrary')">
          <el-icon name="DocumentCopy" /> 浏览资源库
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// 组件属性
const props = defineProps<{
  resource?: any;
}>()

// 组件事件
// const emit = defineEmits<{
//   openResourceLibrary: [];
// }>()

// 状态变量
const currentResource = ref(props.resource)

// 监听资源变化
watch(() => props.resource, (newResource) => {
  currentResource.value = newResource
})

// 预计学习时间（基于资源类型和难度估算）
const estimatedLearningTime = computed(() => {
  if (!currentResource.value) return 0
  
  const baseTime = {
    '初级': 30,
    '中级': 60,
    '高级': 90
  }
  
  const typeMultiplier = {
    '基础课程': 1,
    '专业课程': 1.5,
    '实训课程': 2,
    '选修课程': 0.8
  }
  
  const difficultyTime = baseTime[currentResource.value.difficulty as keyof typeof baseTime] || 60
  const multiplier = typeMultiplier[currentResource.value.type as keyof typeof typeMultiplier] || 1
  
  return Math.round(difficultyTime * multiplier)
})

// 关键关键词提取
const keyKeywords = computed(() => {
  if (!currentResource.value) return []
  
  const keywords = new Set<string>()
  
  // 从标题提取
  const titleWords = currentResource.value.title.split(/[\s\-\(\)\[\]{}]/)
  titleWords.forEach((word: string) => {
    if (word.length > 2) keywords.add(word)
  })
  
  // 从描述提取
  const descWords = currentResource.value.description.split(/[\s，。；：！？]/)
  descWords.forEach((word: string) => {
    if (word.length > 2) keywords.add(word)
  })
  
  // 添加课程类型和难度
  keywords.add(currentResource.value.type)
  keywords.add(currentResource.value.difficulty)
  
  return Array.from(keywords).slice(0, 8) // 最多8个关键词
})

// 教学建议
const teachingSuggestions = computed(() => {
  if (!currentResource.value) return []
  
  const suggestions = [
    {
      title: '课前准备',
      content: '建议在课前1-2天预习本资源内容，熟悉相关知识点，为课堂教学做好准备。',
      icon: 'Calendar'
    },
    {
      title: '课堂应用',
      content: `可将本资源作为${currentResource.value.difficulty === '高级' ? '拓展材料' : '核心内容'}在课堂上使用，结合实际教学场景进行讲解。`,
      icon: 'Monitor'
    },
    {
      title: '课后巩固',
      content: '建议将本资源分享给学生，作为课后复习材料，加深学生对知识点的理解。',
      icon: 'Book'
    }
  ]
  
  // 根据资源类型添加特定建议
  if (currentResource.value.type === '实训课程') {
    suggestions.push({
      title: '实践操作',
      content: '建议在实验室或实训场地进行实际操作练习，强化学生的动手能力。',
      icon: 'Operation'
    })
  }
  
  return suggestions
})

// 推荐使用场景
const usageScenarios = computed(() => {
  if (!currentResource.value) return []
  
  return [
    {
      name: '新课导入',
      description: '作为新课的导入材料，激发学生的学习兴趣',
      selected: true
    },
    {
      name: '重点讲解',
      description: '作为课堂重点内容的详细讲解材料',
      selected: currentResource.value.difficulty === '中级'
    },
    {
      name: '案例分析',
      description: '作为实际案例进行分析讨论',
      selected: currentResource.value.type === '专业课程'
    },
    {
      name: '课后拓展',
      description: '作为学生课后自主学习的拓展材料',
      selected: currentResource.value.difficulty === '高级'
    }
  ]
})
</script>

<style scoped>
.resource-decoder {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-top: 20px;
}

.decoder-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.header-icon {
  font-size: 32px;
  color: #ffd04b;
  margin-bottom: 10px;
  display: block;
}

.decoder-header h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #0f4c81;
  font-weight: bold;
}

.decoder-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.decoder-content {
  min-height: 400px;
}

.resource-analysis {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.analysis-section {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
}

.analysis-section h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.analysis-section h4 .el-icon {
  color: #ffd04b;
}

.analysis-result {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.analysis-label {
  font-weight: bold;
  color: #303133;
  white-space: nowrap;
}

.analysis-value {
  color: #606266;
  flex: 1;
}

.key-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  background: rgba(255, 208, 75, 0.1);
  color: #0f4c81;
  border-color: #ffd04b;
}

.teaching-suggestions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.suggestion-card {
  border-left: 4px solid #ffd04b;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #0f4c81;
}

.suggestion-card p {
  margin: 10px 0 0 0;
  color: #606266;
  line-height: 1.5;
}

.usage-scenarios {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.scenario-item {
  background: white;
  border-radius: 6px;
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.scenario-description {
  margin-top: 6px;
  margin-left: 24px;
  font-size: 13px;
  color: #909399;
}

.no-resource {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 8px;
  min-height: 400px;
}

.no-resource-icon {
  font-size: 64px;
  color: #909399;
  margin-bottom: 20px;
}

.no-resource p {
  margin: 0 0 30px 0;
  color: #606266;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analysis-result {
    grid-template-columns: 1fr;
  }
  
  .teaching-suggestions {
    grid-template-columns: 1fr;
  }
  
  .decoder-header h3 {
    font-size: 18px;
  }
  
  .analysis-section h4 {
    font-size: 14px;
  }
}
</style>