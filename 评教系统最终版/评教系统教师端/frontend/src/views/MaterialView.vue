<template>
  <div class="material-view">
    <div class="page-header">
      <h1 class="page-title">分发材料</h1>
      <p class="page-description">查看管理端分发的评教材料</p>
    </div>

    <div class="materials-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="materials.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>暂无分发材料</h3>
        <p>还没有收到管理端分发的材料</p>
      </div>

      <div v-else class="materials-grid">
        <div
          v-for="material in materials"
          :key="material.material_id"
          class="material-card"
        >
          <div class="material-icon">
            {{ getMaterialIcon(material.material_type) }}
          </div>
          <div class="material-info">
            <h3 class="material-name">{{ material.material_name }}</h3>
            <div class="material-meta">
              <span class="material-type">{{ getMaterialTypeLabel(material.material_type) }}</span>
              <span class="material-date">{{ formatDate(material.distributed_time) }}</span>
            </div>
          </div>
          <div class="material-actions">
            <button class="btn-action btn-download" @click="downloadMaterial(material)">
              📥 下载
            </button>
            <button
              v-if="canPreview(material)"
              class="btn-action btn-preview"
              @click="openPreview(material)"
            >
              👁️ 预览
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 预览对话框 -->
    <div v-if="showPreview" class="preview-overlay" @click="closePreview">
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h2 class="preview-title">{{ previewMaterial.material_name }}</h2>
          <button class="preview-close" @click="closePreview">✕</button>
        </div>
        <div class="preview-body">
          <iframe
            v-if="previewUrl"
            :src="previewUrl"
            class="preview-frame"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const API_BASE_URL = 'http://localhost:8000';

const loading = ref(false);
const materials = ref<any[]>([]);
const showPreview = ref(false);
const previewMaterial = ref<any>(null);
const previewUrl = ref('');

// 加载材料列表
const loadMaterials = async () => {
  loading.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/teacher/materials`);
    const data = await response.json();
    materials.value = data.materials || [];
  } catch (error) {
    console.error('加载材料失败:', error);
    alert('加载材料失败');
  } finally {
    loading.value = false;
  }
};

// 下载材料
const downloadMaterial = async (material: any) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/teacher/materials/${material.material_id}/download`
    );
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = material.material_name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('下载失败:', error);
    alert('下载失败');
  }
};

// 预览材料
const openPreview = (material: any) => {
  previewMaterial.value = material;
  previewUrl.value = `${API_BASE_URL}/api/teacher/materials/${material.material_id}/download`;
  showPreview.value = true;
};

// 关闭预览
const closePreview = () => {
  showPreview.value = false;
  previewUrl.value = '';
};

// 判断是否可以预览
const canPreview = (material: any) => {
  const previewableTypes = ['pdf', 'png', 'jpg', 'jpeg'];
  const ext = material.material_name.split('.').pop()?.toLowerCase();
  return previewableTypes.includes(ext || '');
};

// 获取材料图标
const getMaterialIcon = (type: string) => {
  return type === 'evaluation_form' ? '📊' : '📄';
};

// 获取材料类型标签
const getMaterialTypeLabel = (type: string) => {
  return type === 'evaluation_form' ? '考评表' : '文件';
};

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
};

onMounted(() => {
  loadMaterials();
  
  // 每3秒自动刷新一次材料列表
  const refreshInterval = setInterval(() => {
    loadMaterials();
  }, 3000);
  
  // 组件卸载时清除定时器
  return () => clearInterval(refreshInterval);
});
</script>

<style scoped>
.material-view {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #757575;
  margin: 0;
}

.materials-container {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 32px;
  color: #757575;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #E0E0E0;
  border-top-color: #1976D2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.materials-grid {
  display: grid;
  gap: 16px;
}

.material-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #FAFAFA;
  border: 1px solid #EEEEEE;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.material-card:hover {
  background: #F5F5F5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.material-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.material-info {
  flex: 1;
  min-width: 0;
}

.material-name {
  font-size: 16px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #757575;
}

.material-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-download {
  background: #1976D2;
  color: #FFFFFF;
}

.btn-download:hover {
  background: #1565C0;
}

.btn-preview {
  background: #FFFFFF;
  color: #616161;
  border: 1px solid #E0E0E0;
}

.btn-preview:hover {
  background: #FAFAFA;
}

/* 预览对话框 */
.preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.preview-content {
  background: #FFFFFF;
  border-radius: 12px;
  width: 90%;
  height: 90%;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #EEEEEE;
}

.preview-title {
  font-size: 18px;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.preview-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #757575;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.preview-close:hover {
  background: #F5F5F5;
}

.preview-body {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
