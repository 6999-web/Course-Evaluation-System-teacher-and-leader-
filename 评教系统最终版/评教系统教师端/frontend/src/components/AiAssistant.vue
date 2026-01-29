<template>
  <div 
    class="ai-assistant"
    :style="{
      left: position.x + 'px',
      top: position.y + 'px'
    }"
    ref="assistantRef"
  >
    <!-- 悬浮按钮 -->
    <div 
      class="assistant-button"
      :class="{ 'expanded': isExpanded }"
      @mousedown="(e) => startDrag('button', e)"
      @click="toggleExpand"
    >
      <el-icon :name="isExpanded ? 'Close' : 'ChatLineSquare'" class="button-icon" />
      <div v-if="!isExpanded" class="button-text">AI助手</div>
    </div>
    
    <!-- 聊天窗口 -->
    <div v-if="isExpanded" class="chat-window" ref="chatWindowRef" :style="{
      transform: `translate(${chatWindowPosition.x}px, ${chatWindowPosition.y}px)`
    }">
      <!-- 聊天窗口头部 -->
      <div class="chat-header" @mousedown="(e) => startDrag('window', e)">
        <div class="chat-title">
          <el-icon name="ChatLineSquare" /> AI助手
        </div>
        <div class="chat-header-right">
          <div class="chat-status" :class="{ 'online': isOnline }">
            <el-icon :name="isOnline ? 'Check' : 'Close'" />
            {{ isOnline ? '在线' : '离线' }}
          </div>
          <div class="close-button" @click.stop="toggleExpand">
            <span class="close-x">×</span>
          </div>
        </div>
      </div>
      
      <!-- 聊天内容区域 -->
      <div class="chat-content" ref="chatContentRef">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-avatar">
            <el-icon name="ChatLineSquare" />
          </div>
          <div class="welcome-text">
            <p>你好！我是评教系统的AI助手，有什么可以帮助你的吗？</p>
            <p>你可以咨询以下问题：</p>
            <ul>
              <li @click="sendQuickQuestion('如何使用教学资源推荐功能？')">如何使用教学资源推荐功能？</li>
              <li @click="sendQuickQuestion('批量操作工具怎么使用？')">批量操作工具怎么使用？</li>
              <li @click="sendQuickQuestion('个人成长档案有什么用？')">个人成长档案有什么用？</li>
              <li @click="sendQuickQuestion('评教趋势预测如何查看？')">评教趋势预测如何查看？</li>
            </ul>
          </div>
        </div>
        
        <!-- 聊天消息 -->
        <div v-for="(message, index) in messages" :key="index" class="chat-message" :class="message.role">
          <div class="message-avatar">
            <el-icon :name="message.role === 'user' ? 'User' : 'ChatLineSquare'" />
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ message.timestamp }}</div>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-message">
          <div class="message-avatar">
            <el-icon name="ChatLineSquare" />
          </div>
          <div class="message-content">
            <div class="loading-indicator">
              <el-icon name="Loading" class="loading-icon" />
              <span>思考中...</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 聊天输入区域 -->
      <div class="chat-input-area">
        <el-input
          v-model="inputMessage"
          placeholder="请输入你的问题..."
          class="chat-input"
          @keyup.enter="sendMessage"
        >
          <template #append>
            <el-button type="primary" @click="sendMessage" :disabled="!inputMessage.trim() || isLoading">
              <el-icon name="Send" />
            </el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 快捷问题 -->
      <div class="quick-questions">
        <el-tag 
          v-for="question in quickQuestions" 
          :key="question"
          size="small"
          class="quick-question-tag"
          @click="sendQuickQuestion(question)"
        >
          {{ question }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// 状态变量
const isExpanded = ref(false)
const isLoading = ref(false)
const isOnline = ref(true)
const inputMessage = ref('')
const messages = ref<any[]>([])
const position = ref({ x: 80, y: 300 })
const chatWindowPosition = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const draggedElement = ref<string | null>(null)
const startPos = ref({ x: 0, y: 0 })
const assistantRef = ref<HTMLElement>()
const chatContentRef = ref<HTMLElement>()
const chatWindowRef = ref<HTMLElement>()

// 快捷问题
const quickQuestions = [
  '如何查看我的评价报告？',
  '怎么提交改进计划？',
  '教学资源如何下载？',
  '如何使用批量操作工具？'
]

// 初始化位置
onMounted(() => {
  loadPosition()
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', stopDrag)
  window.addEventListener('resize', savePosition)
})

// 清理事件监听器
onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', stopDrag)
})

// 加载位置
const loadPosition = () => {
  const savedPosition = localStorage.getItem('aiAssistantPosition')
  if (savedPosition) {
    try {
      const pos = JSON.parse(savedPosition)
      position.value = pos.position || { x: 80, y: 300 }
      chatWindowPosition.value = pos.chatWindowPosition || { x: 0, y: 0 }
    } catch (e) {
      console.error('Failed to load AI assistant position:', e)
    }
  }
}

// 保存位置
const savePosition = () => {
  localStorage.setItem('aiAssistantPosition', JSON.stringify({
    position: position.value,
    chatWindowPosition: chatWindowPosition.value
  }))
}

// 开始拖动AI助手图标或聊天窗口
const startDrag = (element: string, e: MouseEvent) => {
  // 允许从AI助手按钮或聊天窗口头部拖动
  if (assistantRef.value?.contains(e.target as Node)) {
    isDragging.value = true
    draggedElement.value = element
    if (element === 'button') {
      startPos.value = {
        x: e.clientX - position.value.x,
        y: e.clientY - position.value.y
      }
      assistantRef.value?.classList.add('dragging')
    } else if (element === 'window') {
      startPos.value = {
        x: e.clientX - chatWindowPosition.value.x,
        y: e.clientY - chatWindowPosition.value.y
      }
      chatWindowRef.value?.classList.add('dragging')
    }
  }
}

// 鼠标移动
const onMouseMove = (e: MouseEvent) => {
  if (isDragging.value) {
    if (draggedElement.value === 'button') {
      const newX = e.clientX - startPos.value.x
      const newY = e.clientY - startPos.value.y
      
      // 限制在窗口内
      const windowWidth = window.innerWidth
      const windowHeight = window.innerHeight
      const assistantWidth = assistantRef.value?.offsetWidth || 60
      const assistantHeight = assistantRef.value?.offsetHeight || 60
      
      position.value = {
        x: Math.max(0, Math.min(windowWidth - assistantWidth, newX)),
        y: Math.max(0, Math.min(windowHeight - assistantHeight, newY))
      }
    } else if (draggedElement.value === 'window') {
      const newX = e.clientX - startPos.value.x
      const newY = e.clientY - startPos.value.y
      
      // 限制聊天窗口在合理范围内
      chatWindowPosition.value = {
        x: newX,
        y: newY
      }
    }
  }
}

// 停止拖动
const stopDrag = () => {
  if (isDragging.value) {
    isDragging.value = false
    assistantRef.value?.classList.remove('dragging')
    chatWindowRef.value?.classList.remove('dragging')
    draggedElement.value = null
    savePosition()
  }
}

// 切换展开/收起
const toggleExpand = () => {
  if (!isDragging.value) {
    isExpanded.value = !isExpanded.value
    if (isExpanded.value) {
      nextTick(() => {
        scrollToBottom()
      })
    }
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return
  
  // 添加用户消息
  addMessage('user', message)
  inputMessage.value = ''
  
  // 显示加载状态
  isLoading.value = true
  
  try {
    // 调用AI模型获取回复
    const reply = await getAIResponse(message)
    addMessage('assistant', reply)
  } catch (error) {
    console.error('AI response error:', error)
    addMessage('assistant', '抱歉，我暂时无法回答你的问题。请稍后再试。')
  } finally {
    isLoading.value = false
  }
}

// 发送快捷问题
const sendQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

// 添加消息
const addMessage = (role: string, content: string) => {
  const timestamp = new Date().toLocaleTimeString('zh-CN')
  messages.value.push({
    role,
    content,
    timestamp
  })
  
  nextTick(() => {
    scrollToBottom()
  })
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatContentRef.value) {
    chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
  }
}

// 获取AI回复
const getAIResponse = async (message: string): Promise<string> => {
  return new Promise((resolve) => {
    // 模拟API调用延迟
    setTimeout(() => {
      // 系统相关的回复逻辑
      const lowerMessage = message.toLowerCase()
      
      if (lowerMessage.includes('如何') && lowerMessage.includes('查看') && lowerMessage.includes('评价报告')) {
        resolve('你可以通过左侧导航菜单中的"评价报告"选项查看你的评教报告。在报告页面中，你可以看到详细的评分数据、图表分析和改进建议。')
      } else if (lowerMessage.includes('如何') && lowerMessage.includes('提交') && lowerMessage.includes('改进计划')) {
        resolve('在左侧导航菜单中选择"改进计划"，然后点击"创建改进计划"按钮。你可以根据评教结果和系统推荐，制定具体的改进措施和时间计划。')
      } else if (lowerMessage.includes('教学资源') && lowerMessage.includes('下载')) {
        resolve('进入"教学资源"模块，浏览推荐的教学资源。每个资源卡片下方都有"下载"按钮，点击即可下载资源到本地。你也可以在"我的缓存"中查看所有已下载的资源。')
      } else if (lowerMessage.includes('批量操作') && lowerMessage.includes('工具')) {
        resolve('在左侧导航菜单中选择"批量操作"，你可以进行批量导出、批量申诉、批量评分等操作。选择你需要的操作类型，按照提示上传文件或选择项目即可。')
      } else if (lowerMessage.includes('个人档案')) {
        resolve('"个人档案"模块记录了你的教学成长轨迹，包括基本信息、评教统计、教学成果和专业发展记录。你可以通过左侧导航菜单进入查看详细内容。')
      } else if (lowerMessage.includes('评教趋势')) {
        resolve('在"评教趋势"模块中，你可以查看历史评教数据的变化趋势，系统会基于历史数据预测未来的评教趋势，并提供针对性的改进建议。')
      } else if (lowerMessage.includes('经验交流')) {
        resolve('"经验交流"模块是一个教师之间分享教学经验的平台。你可以发布自己的教学心得，也可以浏览和评论其他教师的分享内容。')
      } else {
        // 通用回复
        resolve(`感谢你的问题！关于"${message}"，我可以为你提供以下帮助：\n\n1. 如果你有系统使用方面的问题，请具体说明你想了解的功能模块。\n2. 如果你有教学相关的问题，我可以基于系统数据为你提供建议。\n3. 如果你需要技术支持，请描述具体的问题现象。\n\n你也可以尝试点击下方的快捷问题，获取常见问题的解答。`)
      }
    }, 1500)
  })
}

// 外部方法
defineExpose({
  toggleExpand
})
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  right: 30px;
  bottom: 30px;
  z-index: 1000;
  user-select: none;
}

/* 悬浮按钮 */
.assistant-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.assistant-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.assistant-button.expanded {
  border-radius: 50% 50% 0 0;
}

.button-icon {
  font-size: 24px;
  transition: all 0.3s ease;
}

.button-text {
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
}

.assistant-button.dragging {
  cursor: grabbing;
  transform: rotate(5deg);
}

.chat-window.dragging {
  cursor: grabbing;
}

.chat-header {
  cursor: grab;
}

.chat-header:active {
  cursor: grabbing;
}

/* 聊天窗口 */
.chat-window {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 380px;
  max-height: 500px;
  background: white;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 聊天窗口头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
  border-radius: 12px 12px 0 0;
}

/* 关闭按钮样式增强 */
.close-button {
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-left: 10px;
}

.close-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.close-x {
  font-size: 24px;
  color: white;
  font-weight: bold;
  line-height: 1;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.chat-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.chat-status.online {
  color: #67c23a;
}

/* 聊天内容 */
.chat-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 300px;
  background: #f8f9fa;
}

/* 欢迎消息 */
.welcome-message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.welcome-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.welcome-text {
  flex: 1;
}

.welcome-text p {
  margin: 0 0 10px 0;
  color: #606266;
  line-height: 1.4;
}

.welcome-text ul {
  margin: 0;
  padding-left: 20px;
}

.welcome-text li {
  margin-bottom: 5px;
  color: #409eff;
  cursor: pointer;
  transition: color 0.3s ease;
}

.welcome-text li:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 聊天消息 */
.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-message.user .message-avatar {
  background: #67c23a;
}

.message-content {
  max-width: 70%;
  min-width: 120px;
}

.chat-message.user .message-content {
  text-align: right;
}

.message-text {
  padding: 10px 14px;
  border-radius: 18px;
  background: white;
  color: #303133;
  line-height: 1.4;
  word-wrap: break-word;
}

.chat-message.user .message-text {
  background: #409eff;
  color: white;
}

.message-time {
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
}

/* 加载消息 */
.loading-message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 18px;
  background: white;
  color: #606266;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 聊天输入 */
.chat-input-area {
  padding: 15px 20px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.chat-input {
  width: 100%;
}

/* 快捷问题 */
.quick-questions {
  padding: 0 20px 15px;
  background: white;
  border-top: 1px solid #e4e7ed;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-question-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-question-tag:hover {
  background: #ecf5ff;
  border-color: #d9ecff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-window {
    width: 320px;
    right: -10px;
  }
  
  .message-content {
    max-width: 80%;
  }
  
  .assistant-button {
    width: 50px;
    height: 50px;
  }
  
  .button-icon {
    font-size: 20px;
  }
  
  .button-text {
    display: none;
  }
}
</style>