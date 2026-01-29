<template>
  <div class="material-collection page-container">
    <div class="content-container">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">评教材料回收</h1>
          <p class="page-description">查看和管理教师提交的评教材料</p>
        </div>
      </div>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <div class="filter-group">
          <label class="filter-label">审核状态</label>
          <select v-model="filters.status" class="filter-select" @change="loadSubmissions">
            <option value="">全部</option>
            <option value="pending">待审核</option>
            <option value="approved">已审核</option>
            <option value="rejected">已拒绝</option>
            <option value="needs_revision">待修改</option>
          </select>
        </div>

        <div class="filter-group">
          <label class="filter-label">教师ID</label>
          <input
            v-model="filters.teacher_id"
            type="text"
            class="filter-input"
            placeholder="输入教师ID筛选"
            @input="loadSubmissions"
          />
        </div>

        <button class="btn-secondary" @click="resetFilters">
          🔄 重置筛选
        </button>
      </div>

      <!-- 提交列表 -->
      <div class="submissions-section">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner-large"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="submissions.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>暂无提交材料</h3>
          <p>还没有教师提交评教材料</p>
        </div>

        <div v-else class="submissions-grid">
          <div
            v-for="submission in submissions"
            :key="submission.submission_id"
            class="submission-card"
          >
            <div class="submission-header">
              <div class="teacher-info">
                <h3 class="teacher-name">{{ submission.teacher_name }}</h3>
                <span class="teacher-id">ID: {{ submission.teacher_id }}</span>
              </div>
              <span :class="['status-badge', `status-${submission.review_status}`]">
                {{ getStatusLabel(submission.review_status) }}
              </span>
            </div>

            <div class="submission-body">
              <div class="info-row">
                <span class="info-label">提交时间</span>
                <span class="info-value">{{ formatDate(submission.submission_time) }}</span>
              </div>

              <div class="files-list">
                <div class="files-header">
                  <span class="files-label">提交文件 ({{ submission.files.length }})</span>
                </div>
                <div
                  v-for="(file, index) in submission.files"
                  :key="index"
                  class="file-item"
                >
                  <span class="file-icon">{{ getFileIcon(file.file_name) }}</span>
                  <span class="file-name">{{ file.file_name }}</span>
                  <span class="file-size">{{ formatFileSize(file.file_size) }}</span>
                  <button
                    class="btn-icon"
                    @click="downloadFile(file.file_id)"
                    title="下载"
                  >
                    📥
                  </button>
                </div>
              </div>
            </div>

            <div class="submission-actions">
              <button
                class="btn-action btn-approve"
                @click="openReviewDialog(submission, 'approved')"
                :disabled="submission.review_status === 'approved'"
              >
                ✓ 通过
              </button>
              <button
                class="btn-action btn-revision"
                @click="openReviewDialog(submission, 'needs_revision')"
              >
                ↻ 待修改
              </button>
              <button
                class="btn-action btn-reject"
                @click="openReviewDialog(submission, 'rejected')"
              >
                ✕ 拒绝
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 审核对话框 -->
    <div v-if="showReviewDialog" class="dialog-overlay" @click="closeReviewDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h2 class="dialog-title">审核材料</h2>
          <button class="dialog-close" @click="closeReviewDialog">✕</button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label class="form-label">审核状态</label>
            <select v-model="reviewForm.status" class="form-select">
              <option value="approved">通过</option>
              <option value="needs_revision">待修改</option>
              <option value="rejected">拒绝</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">审核反馈</label>
            <textarea
              v-model="reviewForm.feedback"
              class="form-textarea"
              rows="4"
              placeholder="请输入审核意见..."
            ></textarea>
          </div>
        </div>

        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeReviewDialog">取消</button>
          <button class="btn-primary" @click="submitReview" :disabled="submitting">
            <span v-if="!submitting">确认提交</span>
            <span v-else class="loading-text">
              <span class="loading-spinner"></span>
              提交中...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { getMaterialSubmissions, updateReviewStatus, downloadMaterial } from '../utils/materialApi';

const loading = ref(false);
const submissions = ref<any[]>([]);
const showReviewDialog = ref(false);
const submitting = ref(false);

const filters = reactive({
  status: '',
  teacher_id: ''
});

const reviewForm = reactive({
  submission_id: '',
  status: 'approved',
  feedback: ''
});

// 加载提交列表
const loadSubmissions = async () => {
  loading.value = true;
  try {
    const params: any = {};
    if (filters.status) params.status = filters.status;
    if (filters.teacher_id) params.teacher_id = filters.teacher_id;

    const response = await getMaterialSubmissions(params);
    submissions.value = response.submissions || [];
  } catch (error: any) {
    alert('加载失败: ' + error.message);
  } finally {
    loading.value = false;
  }
};

// 重置筛选
const resetFilters = () => {
  filters.status = '';
  filters.teacher_id = '';
  loadSubmissions();
};

// 打开审核对话框
const openReviewDialog = (submission: any, status: string) => {
  reviewForm.submission_id = submission.submission_id;
  reviewForm.status = status;
  reviewForm.feedback = '';
  showReviewDialog.value = true;
};

// 关闭审核对话框
const closeReviewDialog = () => {
  showReviewDialog.value = false;
};

// 提交审核
const submitReview = async () => {
  if (!reviewForm.feedback && reviewForm.status !== 'approved') {
    alert('请输入审核反馈');
    return;
  }

  submitting.value = true;
  try {
    await updateReviewStatus(reviewForm.submission_id, {
      status: reviewForm.status as any,
      feedback: reviewForm.feedback
    });
    alert('审核成功');
    closeReviewDialog();
    loadSubmissions();
  } catch (error: any) {
    alert('审核失败: ' + error.message);
  } finally {
    submitting.value = false;
  }
};

// 下载文件
const downloadFile = (fileId: string) => {
  downloadMaterial(fileId);
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
  
  // 每3秒自动刷新一次提交列表
  const refreshInterval = setInterval(() => {
    loadSubmissions();
  }, 3000);
  
  // 组件卸载时清除定时器
  return () => clearInterval(refreshInterval);
});
</script>

<style scoped>
/* 继承全局样式 */
.material-collection {
  /* 使用 App.vue 的 page-container 样式 */
}

.page-header {
  padding: 20px 32px;
  border-bottom: 2px solid #EEEEEE;
  background: #FFFFFF;
}

.header-content {
  max-width: 800px;
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

/* 筛选区域 */
.filter-section {
  display: flex;
  gap: 16px;
  padding: 20px 32px;
  background: #FAFAFA;
  border-bottom: 1px solid #EEEEEE;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #616161;
  white-space: nowrap;
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  outline: none;
}

.filter-select:focus,
.filter-input:focus {
  border-color: #003366;
}

/* 提交列表 */
.submissions-section {
  padding: 24px 32px;
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

.loading-spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid #E0E0E0;
  border-top-color: #003366;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.submissions-grid {
  display: grid;
  gap: 20px;
}

.submission-card {
  background: #FFFFFF;
  border: 1px solid #EEEEEE;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.submission-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #FAFAFA;
  border-bottom: 1px solid #EEEEEE;
}

.teacher-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.teacher-name {
  font-size: 18px;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.teacher-id {
  font-size: 13px;
  color: #757575;
}

.status-badge {
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 16px;
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
  padding: 20px 24px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 14px;
}

.info-label {
  color: #757575;
}

.info-value {
  color: #212121;
  font-weight: 500;
}

.files-list {
  margin-top: 16px;
}

.files-header {
  margin-bottom: 12px;
}

.files-label {
  font-size: 14px;
  font-weight: 600;
  color: #424242;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #FAFAFA;
  border-radius: 6px;
  margin-bottom: 8px;
}

.file-icon {
  font-size: 20px;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #212121;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 13px;
  color: #757575;
}

.submission-actions {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  background: #FAFAFA;
  border-top: 1px solid #EEEEEE;
}

.btn-action {
  flex: 1;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-approve {
  background: #E8F5E9;
  color: #2E7D32;
}

.btn-approve:hover:not(:disabled) {
  background: #C8E6C9;
}

.btn-revision {
  background: #E3F2FD;
  color: #1565C0;
}

.btn-revision:hover {
  background: #BBDEFB;
}

.btn-reject {
  background: #FFEBEE;
  color: #C62828;
}

.btn-reject:hover {
  background: #FFCDD2;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: #FFFFFF;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #EEEEEE;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.dialog-close {
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
  transition: all 0.2s ease;
}

.dialog-close:hover {
  background: #F5F5F5;
}

.dialog-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #424242;
  margin-bottom: 8px;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  font-size: 14px;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  outline: none;
  font-family: inherit;
}

.form-select:focus,
.form-textarea:focus {
  border-color: #003366;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #EEEEEE;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary,
.btn-icon {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #003366;
  color: #FFFFFF;
}

.btn-primary:hover:not(:disabled) {
  background: #004080;
}

.btn-primary:disabled {
  background: #E0E0E0;
  color: #9E9E9E;
  cursor: not-allowed;
}

.btn-secondary {
  background: #FFFFFF;
  color: #616161;
  border: 1px solid #E0E0E0;
}

.btn-secondary:hover {
  background: #FAFAFA;
}

.btn-icon {
  padding: 6px;
  background: transparent;
}

.btn-icon:hover {
  background: #F5F5F5;
}

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
</style>
