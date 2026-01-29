<template>
  <div class="evaluation-trend-prediction-view">
    <div class="page-header">
      <h2 class="page-title">评教趋势预测</h2>
      <div class="page-description">
        分析您的评教历史数据，预测未来发展趋势，提供改进建议
      </div>
    </div>
    
    <EvaluationTrendPrediction />
  </div>
</template>

<script setup lang="ts">
import EvaluationTrendPrediction from '../components/EvaluationTrendPrediction.vue'
</script>

<style scoped>
.evaluation-trend-prediction-view {
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