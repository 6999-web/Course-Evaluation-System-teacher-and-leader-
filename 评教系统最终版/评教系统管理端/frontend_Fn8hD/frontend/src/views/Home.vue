<template>
  <div class="home-container page-container">
    <div class="main-content-fluid">
      <!-- 监控中心 -->
      <MonitoringCenter v-if="activeNavValue === 'monitoring'" />
      
      <!-- 分析中心 -->
      <AnalysisCenter v-else-if="activeNavValue === 'analysis'" />
      
      <!-- 应用中心 -->
      <ApplicationCenter v-else-if="activeNavValue === 'application'" />
      
      <!-- 评教模板库 -->
      <TemplateLibrary v-else-if="activeNavValue === 'template'" />
      
      <!-- 档案中心 -->
      <ArchiveCenter v-else-if="activeNavValue === 'archive'" />
      
      <!-- 材料回收 -->
      <MaterialCollection v-else-if="activeNavValue === 'collection'" />
      
      <!-- 系统配置 -->
      <SystemConfig v-else-if="activeNavValue === 'config'" />
      
      <!-- 默认显示监控中心 -->
      <MonitoringCenter v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject, computed } from 'vue';
import MonitoringCenter from '../components/MonitoringCenter.vue';
import AnalysisCenter from '../components/AnalysisCenter.vue';
import ApplicationCenter from '../components/ApplicationCenter.vue';
import ArchiveCenter from '../components/ArchiveCenter.vue';
import SystemConfig from '../components/SystemConfig.vue';
import TemplateLibrary from '../components/TemplateLibrary.vue';
import MaterialCollection from '../components/MaterialCollection.vue';

// 接收来自App组件的activeNav状态
const activeNav = inject('activeNav');

// 计算activeNav的值，处理ref对象和字符串的情况
const activeNavValue = computed(() => {
  if (activeNav && typeof activeNav === 'object' && 'value' in activeNav) {
    return activeNav.value;
  }
  return activeNav || 'monitoring';
});
</script>

<style scoped>
/* 推荐的容器样式 */ 
.main-content-fluid { 
    width: 100%;             /* 强制占满父容器宽度 */ 
    max-width: none !important; /* 移除最大宽度限制 */ 
    min-width: 1024px;       /* 设置最小宽度防止布局崩坏 */ 
    margin: 0;               /* 移除自动外边距 */ 
    padding: 24px;           /* 统一内边距，保持呼吸感 */ 
    box-sizing: border-box;  /* 确保 padding 不会撑大容器 */ 
} 

/* 样式已统一到 App.vue 的 page-container 类 */
</style>