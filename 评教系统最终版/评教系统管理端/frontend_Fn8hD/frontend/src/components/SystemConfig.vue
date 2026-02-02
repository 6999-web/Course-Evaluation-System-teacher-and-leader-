<template>
  <div class="system-config-pku page-container">
    <div class="content-container">
      <!-- 页面头部 - 北大风格：简约、留白 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">系统配置</h1>
          <p class="page-description">配置评教方案和分发材料</p>
        </div>
      </div>

    <!-- 标签页导航 - 网格布局 -->
    <div class="tabs-container">
      <div class="tabs-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-button', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <!-- 标签页内容 -->
      <div class="tabs-content">
        <!-- 评教方案配置 -->
        <div v-show="activeTab === 'config'" class="tab-pane fade-in">
          <div class="content-card">
            <div class="card-header">
              <h2 class="card-title">评教方案配置</h2>
              <button class="btn-primary" @click="saveConfig" :disabled="saving">
                <span v-if="!saving">💾 保存配置</span>
                <span v-else class="loading-text">
                  <span class="loading-spinner"></span>
                  保存中...
                </span>
              </button>
            </div>

            <div class="card-body">
              <form class="form-grid">
                <!-- 学年学期 -->
                <div class="form-group">
                  <label class="form-label">学年学期</label>
                  <input
                    v-model="form.academic_year"
                    type="text"
                    class="form-input"
                    placeholder="例如：2024-2025-1"
                  />
                </div>

                <!-- 评价模板 -->
                <div class="form-group">
                  <label class="form-label">评价模板</label>
                  <select v-model="form.template_id" class="form-select">
                    <option value="default">📝 默认模板</option>
                    <option value="practice">🔧 实训课程模板</option>
                    <option value="ideology">💭 思政课程模板</option>
                  </select>
                </div>

                <!-- 时间窗口 -->
                <div class="form-group form-group-full">
                  <label class="form-label">评教时间</label>
                  <div class="date-range">
                    <input
                      v-model="form.time_windows.start_time"
                      type="datetime-local"
                      class="form-input"
                    />
                    <span class="date-separator">至</span>
                    <input
                      v-model="form.time_windows.end_time"
                      type="datetime-local"
                      class="form-input"
                    />
                  </div>
                </div>

                <!-- 启用状态 -->
                <div class="form-group">
                  <label class="form-label">启用状态</label>
                  <label class="switch">
                    <input v-model="form.status" type="checkbox" />
                    <span class="switch-slider"></span>
                    <span class="switch-label">{{ form.status ? '已启用' : '已禁用' }}</span>
                  </label>
                </div>
              </form>

              <!-- 评价维度权重 -->
              <div class="dimensions-section">
                <h3 class="section-title">评价维度权重</h3>
                <div class="dimensions-list">
                  <div
                    v-for="(dimension, index) in form.dimensions"
                    :key="index"
                    class="dimension-item"
                  >
                    <input
                      v-model="dimension.name"
                      type="text"
                      class="dimension-name"
                      placeholder="维度名称"
                    />
                    <div class="dimension-weight">
                      <input
                        v-model.number="dimension.weight"
                        type="range"
                        min="0"
                        max="100"
                        class="weight-slider"
                      />
                      <input
                        v-model.number="dimension.weight"
                        type="number"
                        min="0"
                        max="100"
                        class="weight-input"
                      />
                      <span class="weight-unit">%</span>
                    </div>
                    <button
                      v-if="form.dimensions.length > 1"
                      class="btn-icon btn-danger"
                      @click="removeDimension(index)"
                      title="删除"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                <button class="btn-secondary btn-add" @click="addDimension">
                  ➕ 添加维度
                </button>
              </div>
            </div>
          </div>
        </div>


        <!-- 分发材料 -->
        <div v-show="activeTab === 'distribute'" class="tab-pane fade-in">
          <div class="content-card">
            <div class="card-header">
              <h2 class="card-title">材料分发管理</h2>
              <button
                class="btn-primary"
                @click="distributeFiles"
                :disabled="uploadedFiles.length === 0 || distributing"
              >
                <span v-if="!distributing">📨 统一分发 ({{ uploadedFiles.length }})</span>
                <span v-else class="loading-text">
                  <span class="loading-spinner"></span>
                  分发中...
                </span>
              </button>
            </div>

            <div class="card-body">
              <!-- 文件上传区域 -->
              <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
                <div class="upload-icon">📤</div>
                <h3 class="upload-title">拖拽文件到此处或点击上传</h3>
                <p class="upload-hint">支持 PDF、DOCX、XLSX、PNG、JPG 格式，单个文件不超过 10MB</p>
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg"
                  @change="handleFileSelect"
                  style="display: none"
                />
                <button class="btn-secondary" @click="$refs.fileInput.click()">
                  选择文件
                </button>
              </div>

              <!-- 文件列表 -->
              <div v-if="uploadedFiles.length > 0" class="files-section">
                <h3 class="section-title">已上传文件 ({{ uploadedFiles.length }})</h3>
                <div class="files-grid">
                  <div
                    v-for="(file, index) in uploadedFiles"
                    :key="index"
                    class="file-card"
                  >
                    <div class="file-icon">{{ getFileIcon(file.name) }}</div>
                    <div class="file-info">
                      <div class="file-name" :title="file.name">{{ file.name }}</div>
                      <div class="file-meta">
                        <span class="file-size">{{ formatFileSize(file.size) }}</span>
                        <span class="file-status success">✓ 已上传</span>
                      </div>
                    </div>
                    <button class="btn-icon btn-danger" @click="removeFile(index)" title="删除">
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, reactive } from 'vue';

// 标签页配置
const tabs = [
  { key: 'config', label: '评教方案', icon: '📋' },
  { key: 'distribute', label: '分发材料', icon: '📤' }
];

const activeTab = ref('config');
const saving = ref(false);
const distributing = ref(false);

// 评教方案表单
const form = reactive({
  academic_year: '',
  template_id: 'default',
  dimensions: [
    { name: '教学态度', weight: 25 },
    { name: '教学内容', weight: 25 },
    { name: '教学方法', weight: 25 },
    { name: '教学效果', weight: 25 }
  ],
  time_windows: {
    start_time: '',
    end_time: ''
  },
  status: false
});

// 文件上传
const fileInput = ref<HTMLInputElement>();
const uploadedFiles = ref<any[]>([]);

// 添加维度
const addDimension = () => {
  form.dimensions.push({ name: '', weight: 0 });
};

// 删除维度
const removeDimension = (index: number) => {
  if (form.dimensions.length <= 1) {
    alert('至少保留一个评价维度');
    return;
  }
  form.dimensions.splice(index, 1);
};

// 保存配置
const saveConfig = async () => {
  const totalWeight = form.dimensions.reduce((sum, dim) => sum + dim.weight, 0);
  if (totalWeight !== 100) {
    alert('评价维度权重总和必须为100%');
    return;
  }
  
  if (!form.academic_year) {
    alert('请输入学年学期');
    return;
  }
  
  saving.value = true;
  
  try {
    const response = await fetch('http://120.26.29.145:8000/config/evaluation-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        academic_year: form.academic_year,
        evaluation_plan: {
          template_id: form.template_id,
          dimensions: form.dimensions
        },
        time_windows: form.time_windows,
        status: form.status ? 'enable' : 'disable'
      })
    });
    
    if (response.ok) {
      alert('配置保存成功！');
    } else {
      alert('配置保存失败');
    }
  } catch (error) {
    alert('网络错误');
  } finally {
    saving.value = false;
  }
};

// 文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    handleFiles(Array.from(target.files));
  }
};

// 文件拖放
const handleDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files) {
    handleFiles(Array.from(event.dataTransfer.files));
  }
};

// 处理文件
const handleFiles = async (files: File[]) => {
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'image/png', 'image/jpeg'];
  
  for (const file of files) {
    if (!allowedTypes.includes(file.type)) {
      alert(`文件 ${file.name} 格式不支持`);
      continue;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert(`文件 ${file.name} 超过10MB限制`);
      continue;
    }
    
    // 上传文件到服务器
    try {
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8001/upload/materials', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('文件上传成功:', result);
        
        // 保存文件信息，使用服务器返回的file_id
        uploadedFiles.value.push({
          name: file.name,  // 显示用的原始文件名
          size: file.size,
          status: 'success',
          url: result.url || result.file_url,
          file_id: result.file_id,  // 服务器上的实际文件名
          filename: result.filename  // 原始文件名
        });
        
        console.log('已添加文件:', uploadedFiles.value[uploadedFiles.value.length - 1]);
      } else {
        const error = await response.json();
        alert(`文件 ${file.name} 上传失败: ${error.detail || '未知错误'}`);
      }
    } catch (error) {
      console.error('上传失败:', error);
      alert(`文件 ${file.name} 上传失败`);
    }
  }
};

// 删除文件
const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1);
};

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

// 获取文件图标
const getFileIcon = (filename: string) => {
  if (filename.endsWith('.pdf')) return '📕';
  if (filename.endsWith('.docx')) return '📘';
  if (filename.endsWith('.xlsx')) return '📗';
  if (filename.match(/\.(png|jpg|jpeg)$/)) return '🖼️';
  return '📄';
};

// 分发文件
const distributeFiles = async () => {
  if (!confirm(`确定要将 ${uploadedFiles.value.length} 个文件分发给所有教师吗？`)) {
    return;
  }
  
  distributing.value = true;
  
  try {
    // 获取 token
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    if (!token) {
      alert('请先登录');
      distributing.value = false;
      return;
    }
    
    // 准备分发数据 - 使用服务器返回的file_id
    const material_ids = uploadedFiles.value.map(file => file.file_id);
    const material_types = uploadedFiles.value.map(() => 'file');
    
    console.log('准备分发材料:', { 
      material_ids, 
      material_types,
      files: uploadedFiles.value 
    });
    
    // 调用分发 API
    const response = await fetch('http://localhost:8001/api/materials/distribute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        material_ids: material_ids,
        material_types: material_types,
        distribution_type: 'batch',  // 批量分发给所有教师
        target_teachers: []
      })
    });
    
    console.log('分发响应状态:', response.status);
    
    if (response.ok) {
      const result = await response.json();
      console.log('分发成功:', result);
      alert(`✅ 成功分发 ${uploadedFiles.value.length} 个文件给 ${result.distributed_count} 位教师！`);
      uploadedFiles.value = [];
    } else {
      const error = await response.json();
      console.error('分发失败:', error);
      alert(`❌ 分发失败: ${error.detail || '未知错误'}`);
    }
  } catch (error: any) {
    console.error('分发失败:', error);
    alert(`❌ 分发失败: ${error.message}`);
  } finally {
    distributing.value = false;
  }
};
</script>


<style scoped>
/* 系统配置页面 - 样式已统一到 App.vue 的 page-container 类 */
.system-config-pku {
  /* 继承 App.vue 中的 page-container 样式 */
}

/* 页面头部 - 紧凑布局 */
.page-header {
  padding: 20px 32px;
  border-bottom: 2px solid #EEEEEE;
  background: #FFFFFF;
  flex-shrink: 0;
}

.header-content {
  max-width: 800px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.page-description {
  font-size: 14px;
  color: #757575;
  margin: 0;
  line-height: 1.5;
}

/* 标签页导航 - 占满剩余空间 */
.tabs-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
  margin: 0;
}

.tabs-nav {
  display: flex;
  border-bottom: 1px solid #EEEEEE;
  background: #FAFAFA;
  padding: 8px;
  gap: 4px;
}

.tab-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  font-size: 15px;
  font-weight: 500;
  color: #616161;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-button:hover {
  color: #212121;
  background: #FFFFFF;
}

/* 选中状态 - 北大红色底色反衬 */
.tab-button.active {
  color: #FFFFFF;
  background: #003366;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 51, 102, 0.2);
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  font-size: 15px;
}

/* 标签页内容 - 占满剩余空间 */
.tabs-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  overflow-x: hidden;
}

.tab-pane {
  animation: fadeIn 0.3s ease;
  height: 100%;
}

/* 内容卡片 */
.content-card {
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #EEEEEE;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #EEEEEE;
  background: #FAFAFA;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.card-body {
  padding: 32px;
}

/* 表单网格布局 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  margin-bottom: 4px;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 16px;
  font-size: 15px;
  color: #212121;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  transition: all 0.2s ease;
  outline: none;
}

.form-input:hover,
.form-select:hover {
  border-color: #BDBDBD;
}

.form-input:focus,
.form-select:focus {
  border-color: #003366;
  box-shadow: 0 0 0 3px rgba(0, 51, 102, 0.1);
}

/* 日期范围 */
.date-range {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-separator {
  font-size: 14px;
  color: #757575;
  font-weight: 500;
}

/* 开关按钮 */
.switch {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.switch input[type="checkbox"] {
  position: relative;
  width: 48px;
  height: 24px;
  appearance: none;
  background: #E0E0E0;
  border-radius: 12px;
  outline: none;
  cursor: pointer;
  transition: background 0.3s ease;
}

.switch input[type="checkbox"]:checked {
  background: #003366;
}

.switch input[type="checkbox"]::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #FFFFFF;
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.switch input[type="checkbox"]:checked::before {
  transform: translateX(24px);
}

.switch-label {
  font-size: 14px;
  color: #616161;
  font-weight: 500;
}

/* 维度配置 */
.dimensions-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid #EEEEEE;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 20px 0;
}

.dimensions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #FAFAFA;
  border: 1px solid #EEEEEE;
  border-radius: 8px;
  transition: all 0.2s ease;
  flex-wrap: wrap;
}

.dimension-item:hover {
  background: #F5F5F5;
  border-color: #E0E0E0;
}

.dimension-name {
  flex: 1;
  min-width: 150px;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s ease;
}

.dimension-name:focus {
  border-color: #003366;
}

.dimension-weight {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.weight-slider {
  flex: 1;
  height: 6px;
  appearance: none;
  background: #E0E0E0;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.weight-slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  background: #003366;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

.weight-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.weight-input {
  width: 70px;
  padding: 6px 10px;
  font-size: 14px;
  text-align: center;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  outline: none;
}

.weight-unit {
  font-size: 14px;
  color: #757575;
  font-weight: 500;
}

/* 按钮样式 - 北大风格 */
.btn-primary,
.btn-secondary,
.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  outline: none;
}

.btn-primary {
  background: #003366;
  color: #FFFFFF;
  box-shadow: 0 2px 4px rgba(0, 51, 102, 0.2);
}

.btn-primary:hover:not(:disabled) {
  background: #004080;
  box-shadow: 0 4px 8px rgba(0, 51, 102, 0.3);
  transform: translateY(-1px);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  background: #E0E0E0;
  color: #9E9E9E;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-secondary {
  background: #FFFFFF;
  color: #616161;
  border: 1px solid #E0E0E0;
}

.btn-secondary:hover {
  background: #FAFAFA;
  border-color: #BDBDBD;
  color: #212121;
}

.btn-add {
  width: 100%;
  padding: 12px;
  border-style: dashed;
}

.btn-icon {
  padding: 8px;
  background: transparent;
  border: 1px solid transparent;
}

.btn-danger {
  color: #003366;
}

.btn-danger:hover {
  background: #FFEBEE;
  border-color: #FFCDD2;
}

/* 加载状态 */
.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 文件上传区域 */
.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 32px;
  border: 2px dashed #E0E0E0;
  border-radius: 12px;
  background: #FAFAFA;
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #003366;
  background: #F0F5FA;
}

.upload-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.upload-title {
  font-size: 18px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 14px;
  color: #757575;
  margin: 0 0 24px 0;
}

/* 文件列表 */
.files-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid #EEEEEE;
}

.files-grid {
  display: grid;
  gap: 12px;
}

.file-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #FAFAFA;
  border: 1px solid #EEEEEE;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.file-card:hover {
  background: #F5F5F5;
  border-color: #E0E0E0;
}

.file-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #212121;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #757575;
}

.file-status.success {
  color: #2E7D32;
}

/* 复选框组 */
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #003366;
}

.checkbox-label span {
  font-size: 14px;
  color: #424242;
}

/* 表格样式 */
.table-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid #EEEEEE;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #EEEEEE;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #FFFFFF;
}

.data-table thead {
  background: #FAFAFA;
}

.data-table th {
  padding: 14px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #616161;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #EEEEEE;
  white-space: nowrap;
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #212121;
  border-bottom: 1px solid #F5F5F5;
}

.data-table tbody tr {
  transition: background 0.2s ease;
}

.data-table tbody tr:hover {
  background: #FAFAFA;
}

.table-input {
  width: 100%;
  padding: 6px 10px;
  font-size: 13px;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  outline: none;
  transition: border-color 0.2s ease;
}

.table-input:focus {
  border-color: #003366;
}

.total-score {
  font-weight: 600;
  color: #003366;
  font-size: 16px;
}

/* 动画 */
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

.fade-in {
  animation: fadeIn 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .page-header {
    padding: 16px 24px;
  }
  
  .tabs-content {
    padding: 20px 24px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .tabs-nav {
    flex-direction: column;
  }
  
  .tabs-content {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .card-body {
    padding: 20px;
  }
  
  .dimension-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .dimension-name {
    width: 100%;
  }
  
  .date-range {
    flex-direction: column;
  }
  
  .table-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .table-actions {
    flex-direction: column;
  }
}
</style>
