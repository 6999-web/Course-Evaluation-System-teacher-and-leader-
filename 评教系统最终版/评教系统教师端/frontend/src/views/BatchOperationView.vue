<template>
  <div class="batch-operation-view">
    <div class="page-header">
      <h2 class="page-title">批量操作工具</h2>
      <div class="page-description">
        提供批量导出、批量申诉、批量评分等操作，提高您的工作效率
      </div>
    </div>
    
    <BatchOperationTool />
  </div>
</template>

<script setup lang="ts">
import BatchOperationTool from '../components/BatchOperationTool.vue'
</script>

<style scoped>
.batch-operation-view {
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #0f4c81;
}

.page-title {
  margin: 0;
  font-size: 24px;
  color: #0f4c81;
  font-weight: bold;
}

.page-description {
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}
</style>