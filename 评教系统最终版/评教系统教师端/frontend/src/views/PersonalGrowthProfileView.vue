<template>
  <div class="personal-growth-profile-view">
    <div class="page-header">
      <h2 class="page-title">个人成长档案</h2>
      <div class="page-description">
        记录您的教学成长轨迹，展示教学成果与专业发展
      </div>
    </div>
    
    <PersonalGrowthProfile />
  </div>
</template>

<script setup lang="ts">
import PersonalGrowthProfile from '../components/PersonalGrowthProfile.vue'
</script>

<style scoped>
.personal-growth-profile-view {
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