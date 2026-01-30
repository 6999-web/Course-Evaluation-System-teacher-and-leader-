<template>
  <div id="app">
    <el-container>
      <!-- 上导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="header-left">
            <div class="header-title">
              <h1>
                <span class="school-logo">
                  <img src="@/assets/images/gxjcxy(1).jpg" alt="广西警察学院" class="logo-image">
                </span>
                <span class="school-name">广西警察学院</span>
                <span class="system-title">评教系统 - 教师端</span>
              </h1>
            </div>
          </div>
          <div class="header-right">
            <div class="system-info">
              <span class="current-time">{{ currentTime }}</span>
            </div>
            <el-dropdown>
              <span class="user-info">
                <el-avatar size="small" :src="userAvatar">教师</el-avatar>
                {{ userName }}
                <el-icon name="ArrowDown" class="el-icon--right" />
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人中心</el-dropdown-item>
                  <el-dropdown-item>修改密码</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <!-- 侧导航栏 -->
        <el-aside width="200px" class="app-sidebar">
          <div class="sidebar-header">
            <div class="sidebar-logo">
              <div class="logo-pattern">
                <div class="pattern-dot"></div>
                <div class="pattern-line"></div>
              </div>
              <div class="sidebar-title">功能导航</div>
            </div>
          </div>
          <el-menu
            ref="menuRef"
            :default-active="activeMenu"
            class="sidebar-menu"
            background-color="#0f4c81"
            text-color="#fff"
            active-text-color="#ffd04b"
            router
          >
            <el-menu-item index="dashboard">
              <el-icon name="House" />
              <template #title>仪表盘</template>
            </el-menu-item>
            <el-menu-item index="evaluation">
              <el-icon name="Document" />
              <template #title>我的评价</template>
            </el-menu-item>
            <el-menu-item index="evaluation-form">
              <el-icon name="DocumentAdd" />
              <template #title>待办考评</template>
            </el-menu-item>
            <el-menu-item index="report">
              <el-icon name="PieChart" />
              <template #title>评价报告</template>
            </el-menu-item>
            <el-menu-item index="submission">
              <el-icon name="Upload" />
              <template #title>材料提交</template>
            </el-menu-item>
            <el-menu-item index="materials">
              <el-icon name="Document" />
              <template #title>材料管理</template>
            </el-menu-item>
          </el-menu>
          <!-- 侧边栏底部装饰 -->
          <div class="sidebar-footer">
            <div class="decorative-pattern">
              <div class="pattern-shape"></div>
            </div>
          </div>
        </el-aside>
        
        <!-- 主内容区 -->
        <el-main class="app-main">
          <div style="position: relative; z-index: 1;">
            <router-view />
          </div>
        </el-main>
      </el-container>
    </el-container>
    <!-- 辅助组件 -->
    <AiAssistant />
    <OfflineSyncManager />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import AiAssistant from '@/components/AiAssistant.vue'
import OfflineSyncManager from '@/components/OfflineSyncManager.vue'

const userName = ref('张老师')
const userAvatar = ref('')
const currentTime = ref('')
const route = useRoute()
const menuRef = ref<any>(null)

// 当前激活的菜单项
const activeMenu = computed(() => {
  return route.path.substring(1) || 'dashboard'
})

// 监听路由变化，手动更新菜单激活状态
watch(() => route.path, (newPath) => {
  const menuIndex = newPath.substring(1) || 'dashboard'
  if (menuRef.value && typeof menuRef.value.setActiveIndex === 'function') {
    // 对于Element Plus的el-menu，使用setActiveIndex方法
    menuRef.value.setActiveIndex(menuIndex)
  }
}, { immediate: true })

// 更新当前时间
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 处理退出登录逻辑
const handleLogout = () => {
  console.log('退出登录')
}

// 组件挂载时开始更新时间
onMounted(() => {
  updateCurrentTime()
  const timer = setInterval(updateCurrentTime, 1000)
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(timer)
  })
})
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  padding: 0;
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  background-image: url('https://images.unsplash.com/photo-1542744173-8e7e53415bb0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  background-color: rgba(15, 76, 129, 0.9);
  background-blend-mode: overlay;
}
</style>

<style scoped>
/* 上导航栏 */
.app-header {
  background: linear-gradient(135deg, #0f4c81 0%, #1a5b93 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  padding: 0 30px;
  height: 80px;
  position: relative;
  overflow: hidden;
}

/* 导航栏装饰图案 */
.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background-image: 
    radial-gradient(circle at 20% 30%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  z-index: 1;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  position: relative;
  z-index: 2;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  display: flex;
  flex-direction: column;
}

.header-title h1 {
  margin: 0;
  font-size: 20px;
  color: #fff;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.header-title .school-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.header-title .logo-image {
  width: 60px;
  height: 60px;
  object-fit: contain;
  vertical-align: middle;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.header-title .school-name {
  font-size: 24px;
  color: #fff;
  font-weight: bolder;
  font-family: 'Microsoft YaHei', 'SimHei', '黑体', sans-serif;
  letter-spacing: 2px;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.5);
  background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(200, 220, 255, 1) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  padding: 0 10px;
  border-radius: 4px;
}

.header-title .system-title {
  font-size: 18px;
  color: #ffd04b;
  font-weight: bold;
  background: rgba(255, 210, 75, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255, 210, 75, 0.3);
}

.school-slogan {
  font-size: 14px;
  color: #ffd04b;
  font-weight: bold;
  margin-top: 4px;
  font-family: 'SimHei', '黑体', sans-serif;
  letter-spacing: 2px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.school-slogan::before,
.school-slogan::after {
  content: '⚫';
  margin: 0 8px;
  font-size: 8px;
  color: #ffd04b;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.system-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  color: #fff;
}

.school-name {
  font-size: 14px;
  font-weight: bold;
  color: #ffd04b;
}

.current-time {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 2px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-info .el-avatar {
  margin-right: 10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

/* 侧导航栏 */
.app-sidebar {
  background: linear-gradient(180deg, #0f4c81 0%, #0a3a66 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

/* 侧边栏装饰 */
.app-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background-image: 
    linear-gradient(to right, transparent 0%, rgba(255, 255, 255, 0.03) 100%),
    repeating-linear-gradient(0deg, transparent, transparent 20px, rgba(255, 255, 255, 0.02) 20px, rgba(255, 255, 255, 0.02) 21px);
  z-index: 1;
  pointer-events: none;
}

.sidebar-header {
  padding: 20px 15px;
  position: relative;
  z-index: 2;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-pattern {
  width: 30px;
  height: 30px;
  background-color: rgba(255, 210, 75, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.pattern-dot {
  width: 8px;
  height: 8px;
  background-color: #ffd04b;
  border-radius: 50%;
  position: absolute;
}

.pattern-line {
  width: 20px;
  height: 2px;
  background-color: #ffd04b;
  position: absolute;
  transform: rotate(45deg);
}

.sidebar-title {
  font-size: 14px;
  font-weight: bold;
  color: #fff;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.sidebar-menu {
  height: calc(100% - 120px);
  border-right: none;
  background-color: transparent;
  position: relative;
  z-index: 2;
}

.sidebar-menu .el-menu-item {
  padding: 15px 25px;
  margin: 5px 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-menu-item:hover {
  background-color: rgba(255, 210, 75, 0.2) !important;
  color: #ffd04b !important;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: rgba(255, 220, 120, 0.25) !important;
  color: #ffdd66 !important;
  box-shadow: 0 2px 10px rgba(255, 220, 120, 0.4), 0 0 15px rgba(255, 220, 120, 0.2);
  text-shadow: 0 0 5px rgba(255, 220, 120, 0.5);
}

/* 移除Element Plus默认的菜单激活指示器 */
.sidebar-menu .el-menu-item.is-active::after {
  display: none !important;
}

/* 确保没有其他默认指示器 */
.sidebar-menu .el-menu-item::after {
  display: none !important;
}

.sidebar-menu .el-icon {
  font-size: 18px;
  margin-right: 10px;
}

.sidebar-footer {
  padding: 20px;
  position: relative;
  z-index: 2;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.decorative-pattern {
  display: flex;
  justify-content: center;
  align-items: center;
}

.pattern-shape {
  width: 60px;
  height: 60px;
  border: 2px solid rgba(255, 210, 75, 0.3);
  border-radius: 50%;
  position: relative;
}

.pattern-shape::before, .pattern-shape::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 210, 75, 0.3);
}

.pattern-shape::before {
  width: 30px;
  height: 2px;
}

.pattern-shape::after {
  width: 2px;
  height: 30px;
}

/* 主内容区 */
.app-main {
  padding: 30px;
  background-color: #ffffff;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 80px);
  position: relative;
  overflow: visible;
  z-index: 10;
  display: block;
}
</style>