<template>
  <div class="app-pku">
    <!-- 认证页面 - 不显示侧边栏和头部 -->
    <router-view v-if="$route.path === '/auth'" />
    
    <!-- 系统主页面 - 显示完整布局 -->
    <div v-else class="app-container">
      <!-- 左侧侧边栏 -->
      <aside class="sidebar">
        <!-- Logo 和品牌 -->
        <div class="sidebar-brand" @click="navigateTo('home')">
          <i class="el-icon-shield brand-icon"></i>
          <h1 class="brand-text">警务教学评价系统</h1>
        </div>
        
        <!-- 导航菜单 -->
        <ul class="sidebar-menu">
          <li 
            v-for="item in navItems" 
            :key="item.id"
            class="sidebar-item"
            :class="{ active: activeNav === item.id }"
            @click="navigateTo(item.id)"
          >
            <i :class="item.icon" class="menu-icon"></i>
            <span class="menu-text">{{ item.label }}</span>
          </li>
        </ul>
        
        <!-- 用户菜单 -->
        <div class="sidebar-user">
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar size="small" :src="userAvatar"></el-avatar>
              <span class="user-name">{{ userName }}</span>
              <i class="el-icon-arrow-down"></i>
            </div>
            <template #dropdown>
              <div class="user-dropdown">
                <div class="user-details">
                  <p class="user-fullname">{{ userName }}</p>
                  <p class="user-email">{{ userEmail }}</p>
                </div>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item">
                  <i class="el-icon-user"></i>
                  <span>个人资料</span>
                </button>
                <button class="dropdown-item">
                  <i class="el-icon-setting"></i>
                  <span>系统设置</span>
                </button>
                <button class="dropdown-item" @click="logout">
                  <i class="el-icon-switch-button"></i>
                  <span>退出登录</span>
                </button>
              </div>
            </template>
          </el-dropdown>
        </div>
      </aside>
      
      <!-- 主内容区域 -->
      <div class="main-container">
        <!-- 顶部状态栏 -->
        <header class="top-bar">
          <div class="top-bar-content">
            <div class="page-title">
              {{ currentPageTitle }}
            </div>
            <div class="top-bar-actions">
              <el-button type="primary" size="small" @click="refreshPage">
                <i class="el-icon-refresh"></i>
                刷新
              </el-button>
            </div>
          </div>
        </header>
        
        <!-- 内容区域 -->
        <main class="content">
          <router-view :active-nav="activeNav" />
        </main>
        
        <!-- 底部信息 -->
        <footer class="footer">
          <div class="footer-content">
            <p class="footer-text">© 2024 警务教学评价系统 | 版本 1.0.0</p>
            <p class="footer-links">
              <a href="#" class="footer-link">使用指南</a>
              <span class="footer-divider">|</span>
              <a href="#" class="footer-link">系统公告</a>
              <span class="footer-divider">|</span>
              <a href="#" class="footer-link">联系我们</a>
            </p>
          </div>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, provide } from 'vue';
import { ElMessage } from 'element-plus';
import router from './router';

const activeNav = ref('monitoring');
const userName = ref('管理员');
const userEmail = ref('admin@example.com');
const userAvatar = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png');

// 向子组件提供activeNav状态
provide('activeNav', activeNav);

const navItems = [
  { id: 'monitoring', label: '监控中心', icon: 'el-icon-video-camera' },
  { id: 'analysis', label: '分析中心', icon: 'el-icon-data-analysis' },
  { id: 'application', label: '应用中心', icon: 'el-icon-s-flag' },
  { id: 'template', label: '评教模板库', icon: 'el-icon-document-copy' },
  { id: 'archive', label: '档案中心', icon: 'el-icon-document' },
  { id: 'collection', label: '材料回收', icon: 'el-icon-folder-opened' },
  { id: 'config', label: '系统配置', icon: 'el-icon-setting' }
];

// 计算当前页面标题
const currentPageTitle = computed(() => {
  const currentItem = navItems.find(item => item.id === activeNav.value);
  return currentItem ? currentItem.label : '监控中心';
});

const navigateTo = (navId: string) => {
  activeNav.value = navId;
};

const refreshPage = () => {
  ElMessage.success('页面已刷新');
};
const logout = () => {
  // 清除所有认证信息
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_info');
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('user_info');
  
  ElMessage.success('已退出登录');
  
  // 跳转到登录页
  router.push('/auth');
};</script>

<style>
/* 应用容器 - 警务风格：专业、整洁 */
.app-pku {
  min-height: 100vh;
  background-color: #FAFAFA;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", 
               "Microsoft YaHei", "Source Han Sans SC", sans-serif;
}

/* 主容器布局 */
.app-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

/* 左侧侧边栏 - 使用相对单位 */
.sidebar {
  width: 16vw;
  max-width: 280px;
  min-width: 200px;
  background-color: #003366;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

/* Logo 和品牌 */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-brand:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.brand-icon {
  font-size: 24px;
  color: #ff3b30;
  transition: transform 0.3s ease;
}

.sidebar-brand:hover .brand-icon {
  transform: rotate(5deg);
}

.brand-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #FFFFFF;
  letter-spacing: 0.5px;
  margin: 0;
}

/* 导航菜单 */
.sidebar-menu {
  flex: 1;
  list-style: none;
  margin: 0;
  padding: 20px 0;
}

.sidebar-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.sidebar-item:hover {
  color: #FFFFFF;
  background-color: rgba(255, 255, 255, 0.08);
  padding-left: 24px;
}

/* 选中状态 - 警红色标识 */
.sidebar-item.active {
  color: #FFFFFF;
  background-color: rgba(255, 59, 48, 0.2);
  border-left: 4px solid #ff3b30;
  padding-left: 16px;
}

.sidebar-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background-color: #ff3b30;
}

.menu-icon {
  font-size: 18px;
  line-height: 1;
  width: 20px;
  text-align: center;
}

.menu-text {
  font-size: 15px;
  line-height: 1;
  flex: 1;
}

/* 用户菜单 */
.sidebar-user {
  padding: 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: auto;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem;
  border-radius: 0.5rem;
  transition: background-color 0.3s ease;
  cursor: pointer;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.user-info .user-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #FFFFFF;
  margin: 0;
}

.user-info i {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.user-dropdown {
  position: absolute;
  bottom: calc(100% - 50px);
  left: 260px;
  min-width: 220px;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 8px;
  z-index: 1000;
  animation: fadeInLeft 0.2s ease;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.user-details {
  padding: 12px;
}

.user-fullname {
  font-size: 15px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 4px 0;
}

.user-email {
  font-size: 13px;
  color: #757575;
  margin: 0;
}

.dropdown-divider {
  height: 1px;
  background: #EEEEEE;
  margin: 8px 0;
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  font-size: 14px;
  color: #616161;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: #F5F5F5;
  color: #003366;
}

/* 主内容区域 - 使用相对单位 */
.main-container {
  flex: 1;
  margin-left: 16vw;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 顶部状态栏 */
.top-bar {
  background-color: #FFFFFF;
  border-bottom: 1px solid #EEEEEE;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 900;
}

.top-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2vw;
  height: 4rem;
  max-height: 64px;
  min-height: 56px;
}

.top-bar .page-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 内容区域 - 应用 monitoring-center 的 top-bar 样式 */
.content {
  flex: 1;
  padding: 2vw;
  background-color: #FAFAFA;
  overflow-y: auto;
  width: 100%;
  min-height: calc(100vh - 4rem);
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 页面内容容器 - 基于档案中心页面宽度的统一标准 */
.page-container {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 统一内容宽度容器 - 以档案中心为基准 */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

/* 顶部标题栏 */
.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  color: #003366;
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 底部信息 */
.footer {
  background-color: #FFFFFF;
  border-top: 1px solid #EEEEEE;
  margin-top: auto;
}

.footer-content {
  padding: 24px 32px;
  text-align: center;
}

.footer-text {
  font-size: 14px;
  color: #757575;
  margin: 0 0 8px 0;
  font-weight: 400;
}

.footer-links {
  font-size: 13px;
  color: #9E9E9E;
  margin: 0;
}

.footer-link {
  color: #757575;
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: #003366;
  text-decoration: underline;
}

.footer-divider {
  margin: 0 12px;
  color: #E0E0E0;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 响应式设计 - 使用相对单位 */
@media (max-width: 1200px) {
  .sidebar {
    width: 14vw;
  }
  
  .main-container {
    margin-left: 14vw;
  }
  
  .brand-text {
    font-size: 1rem;
  }
  
  .sidebar-item {
    font-size: 0.875rem;
    padding: 0.875rem 1.125rem;
  }
}

@media (max-width: 992px) {
  .content {
    padding: 1.5rem;
  }
  
  .top-bar-content {
    padding: 0 1.5rem;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 8vw;
    min-width: 60px;
  }
  
  .main-container {
    margin-left: 8vw;
  }
  
  .brand-text,
  .menu-text,
  .user-name {
    display: none;
  }
  
  .sidebar-brand {
    justify-content: center;
    padding: 1.25rem 0;
  }
  
  .sidebar-item {
    justify-content: center;
    padding: 1rem 0;
  }
  
  .sidebar-item.active {
    border-left: none;
    border-right: 0.25rem solid #ff3b30;
  }
  
  .sidebar-item.active::before {
    display: none;
  }
  
  .sidebar-user {
    padding: 1.25rem 0;
    display: flex;
    justify-content: center;
  }
  
  .user-info {
    padding: 0.625rem;
  }
  
  .content {
    padding: 1.25rem 1rem;
  }
  
  .top-bar-content {
    padding: 0 1rem;
    height: 3.5rem;
  }
  
  .top-bar .page-title {
    font-size: 1rem;
  }
  
  .footer-content {
    padding: 1.25rem 1rem;
  }
  
  .footer-text {
    font-size: 0.8125rem;
  }
  
  .footer-links {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 15vw;
    min-width: 50px;
  }
  
  .main-container {
    margin-left: 15vw;
  }
  
  .brand-icon {
    font-size: 1.25rem;
  }
  
  .sidebar-item {
    padding: 0.875rem 0;
  }
  
  .content {
    padding: 1rem 0.75rem;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #F5F5F5;
}

::-webkit-scrollbar-thumb {
  background: #BDBDBD;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9E9E9E;
}
</style>