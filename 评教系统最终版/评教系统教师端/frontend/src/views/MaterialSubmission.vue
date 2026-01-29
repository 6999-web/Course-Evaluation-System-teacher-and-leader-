<template>
  <div class="material-submission">
    <div class="page-header">
      <h1 class="page-title">材料提交</h1>
      <p class="page-description">上传并提交评教材料</p>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section">
      <div class="upload-card">
        <div class="card-header">
          <h2 class="card-title">上传文件</h2>
        </div>
        <div class="card-body">
          <div
            class="upload-area"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="$refs.fileInput.click()"
          >
            <div class="upload-icon">📤</div>
            <h3 class="upload-title">拖拽文件到此处或点击上传</h3>
            <p class="upload-hint">支持 PDF、DOCX、XLSX、PNG、JPG 格式，单个文件不超过 50MB</p>
            <input
              ref="fileInput"
              type="file"
              multiple
              accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg"
              @change="handleFileSelect"
              style="display: none"
            />
          </div>

          <!-- 已上传文件列表 -->
          <div v-if="uploadedFiles.length > 0" class="files-list">
            <h3 class="list-title">已上传文件 ({{ uploadedFiles.length }})</h3>
            <div
              v-for="(file, index) in uploadedFiles"
              :key="index"
              class="file-item"
            >
              <span class="file-icon">{{ getFileIcon(file.file_name) }}</span>
              <div class="file-info">
                <div class="file-name">{{ file.file_name }}</div>
                <div class="file-size">{{ formatFileSize(file.file_size) }}</div>
              </div>
              <button class="btn-remove" @click="removeFile(index)">✕</button>
            </div>
          </div>

          <!-- 备注 -->
          <div class="notes-section">
            <label class="notes-label">备注说明</label>
            <textarea
              v-model="notes"
              class="notes-textarea"
              rows="4"
              placeholder="请输入备注说明（可选）"
            ></textarea>
          </div>

          <!-- 提交按钮 -->
          <div class="submit-section">
            <button
              class="btn-submit"
              @click="submitMaterials"
              :disabled="uploadedFiles.length === 0 || submitting"
            >
              <span v-if="!submitting">📨 提交材料</span>
              <span v-else class="loading-text">
                <span class="loading-spinner"></span>
                提交中...
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交记录 -->
    <div class="submissions-section">
      <div class="submissions-card">
        <div class="card-header">
          <h2 class="card-title">提交记录</h2>
          <button class="btn-refresh" @click="loadSubmissions">🔄 刷新</button>
        </div>
        <div class="card-body">
          <div v-if="loadingSubmissions" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>

          <div v-else-if="submissions.length === 0" class="empty-state">
            <div class="empty-icon">📭</div>
            <p>暂无提交记录</p>
          </div>

          <div v-else class="submissions-list">
            <div
              v-for="submission in submissions"
              :key="submission.submission_id"
              class="submission-item"
            >
              <div class="submission-header">
                <span class="submission-id">提交ID: {{ submission.submission_id }}</span>
                <span :class="['status-badge', `status-${submission.review_status}`]">
                  {{ getStatusLabel(submission.review_status) }}
                </span>
              </div>
              <div class="submission-body">
                <div class="submission-info">
                  <span class="info-label">提交时间:</span>
                  <span class="info-value">{{ formatDate(submission.submission_time) }}</span>
                </div>
                <div class="submission-info">
                  <span class="info-label">文件数量:</span>
                  <span class="info-value">{{ submission.files.length }} 个</span>
                </div>
                <div v-if="submission.review_feedback" class="submission-feedback">
                  <span class="feedback-label">审核反馈:</span>
                  <p class="feedback-text">{{ submission.review_feedback }}</p>
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
import { ref, onMounted } from 'vue';

const API_BASE_URL = 'http://localhost:8000';

const fileInput = ref<HTMLInputElement>();
const uploadedFiles = ref<any[]>([]);
const notes = ref('');
const submitting = ref(false);
const loadingSubmissions = ref(false);
const submissions = ref<any[]>([]);

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
  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/png',
    'image/jpeg'
  ];

  for (const file of files) {
    if (!allowedTypes.includes(file.type)) {
      alert(`文件 ${file.name} 格式不支持`);
      continue;
    }
    if (file.size > 50 * 1024 * 1024) {
      alert(`文件 ${file.name} 超过50MB限制`);
      continue;
    }

    // 上传文件
    await uploadFile(file);
  }
};

// 上传文件
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/api/teacher/materials/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('上传失败');
    }

    const data = await response.json();
    uploadedFiles.value.push(data);
  } catch (error) {
    console.error('上传失败:', error);
    alert(`文件 ${file.name} 上传失败`);
  }
};

// 删除文件
const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1);
};

// 提交材料
const submitMaterials = async () => {
  if (uploadedFiles.value.length === 0) {
    alert('请先上传文件');
    return;
  }

  if (!confirm(`确定要提交 ${uploadedFiles.value.length} 个文件吗？`)) {
    return;
  }

  submitting.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/teacher/materials/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file_ids: uploadedFiles.value.map(f => f.file_id),
        notes: notes.value
      })
    });

    if (!response.ok) {
      throw new Error('提交失败');
    }

    alert('材料提交成功！');
    uploadedFiles.value = [];
    notes.value = '';
    loadSubmissions();
  } catch (error) {
    console.error('提交失败:', error);
    alert('提交失败');
  } finally {
    submitting.value = false;
  }
};

// 加载提交记录
const loadSubmissions = async () => {
  loadingSubmissions.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/teacher/materials/submissions`);
    const data = await response.json();
    submissions.value = data.submissions || [];
  } catch (error) {
    console.error('加载提交记录失败:', error);
  } finally {
    loadingSubmissions.value = false;
  }
};

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labels: any = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    needs_revision: '待修改'
  };
  return labels[status] || status;
};

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
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

onMounted(() => {
  loadSubmissions();
});
</script>

<style scoped>
.material-submission {
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

.upload-section,
.submissions-section {
  margin-bottom: 24px;
}

.upload-card,
.submissions-card {
  background: #FFFFFF;
  border-radius: 12px;
  border: 1px solid #EEEEEE;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #FAFAFA;
  border-bottom: 1px solid #EEEEEE;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.btn-refresh {
  padding: 8px 16px;
  font-size: 14px;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  cursor: pointer;
}

.btn-refresh:hover {
  background: #FAFAFA;
}

.card-body {
  padding: 24px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  border: 2px dashed #E0E0E0;
  border-radius: 12px;
  background: #FAFAFA;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #1976D2;
  background: #E3F2FD;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.upload-title {
  font-size: 16px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 14px;
  color: #757575;
  margin: 0;
}

.files-list {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #EEEEEE;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: #212121;
  margin: 0 0 16px 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #FAFAFA;
  border-radius: 8px;
  margin-bottom: 8px;
}

.file-icon {
  font-size: 24px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #212121;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 13px;
  color: #757575;
}

.btn-remove {
  background: none;
  border: none;
  font-size: 18px;
  color: #757575;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-remove:hover {
  background: #FFEBEE;
  color: #C62828;
}

.notes-section {
  margin-top: 24px;
}

.notes-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  margin-bottom: 8px;
}

.notes-textarea {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  outline: none;
  font-family: inherit;
  resize: vertical;
}

.notes-textarea:focus {
  border-color: #1976D2;
}

.submit-section {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.btn-submit {
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 500;
  background: #1976D2;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-submit:hover:not(:disabled) {
  background: #1565C0;
}

.btn-submit:disabled {
  background: #E0E0E0;
  color: #9E9E9E;
  cursor: not-allowed;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  color: #757575;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E0E0E0;
  border-top-color: #1976D2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.submissions-list {
  display: grid;
  gap: 16px;
}

.submission-item {
  border: 1px solid #EEEEEE;
  border-radius: 8px;
  overflow: hidden;
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #FAFAFA;
  border-bottom: 1px solid #EEEEEE;
}

.submission-id {
  font-size: 14px;
  font-weight: 500;
  color: #616161;
}

.status-badge {
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 12px;
}

.status-pending {
  background: #FFF3E0;
  color: #E65100;
}

.status-approved {
  background: #E8F5E9;
  color: #2E7D32;
}

.status-rejected {
  background: #FFEBEE;
  color: #C62828;
}

.status-needs_revision {
  background: #E3F2FD;
  color: #1565C0;
}

.submission-body {
  padding: 16px;
}

.submission-info {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-label {
  color: #757575;
}

.info-value {
  color: #212121;
  font-weight: 500;
}

.submission-feedback {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #EEEEEE;
}

.feedback-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  margin-bottom: 8px;
}

.feedback-text {
  font-size: 14px;
  color: #616161;
  margin: 0;
  line-height: 1.6;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
