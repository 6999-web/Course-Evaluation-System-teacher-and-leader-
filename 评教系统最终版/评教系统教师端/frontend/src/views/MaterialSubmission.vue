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
            @click="($refs.fileInput as HTMLInputElement)?.click()"
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
                
                <!-- 评分结果展示 -->
                <div v-if="submission.showScoring" class="scoring-section">
                  <div class="scoring-header">
                    <span class="scoring-title">📊 评分结果</span>
                    <button class="btn-collapse" @click="submission.showScoring = false">收起</button>
                  </div>
                  
                  <div v-if="submission.loadingScoring" class="loading-state">
                    <div class="loading-spinner"></div>
                    <p>加载评分结果中...</p>
                  </div>
                  
                  <div v-else-if="!submission.scoringData || submission.scoringData.scoring_records.length === 0" class="empty-scoring">
                    <p>暂无评分结果</p>
                  </div>
                  
                  <div v-else class="scoring-records">
                    <div
                      v-for="record in submission.scoringData.scoring_records"
                      :key="record.id"
                      class="scoring-record"
                    >
                      <div class="record-header">
                        <span class="file-name">{{ record.file_name }}</span>
                        <span :class="['grade-badge', `grade-${record.grade}`]">
                          {{ record.grade }}
                        </span>
                      </div>
                      
                      <div class="record-scores">
                        <div class="score-item">
                          <span class="score-label">基础分:</span>
                          <span class="score-value">{{ record.base_score }}</span>
                        </div>
                        <div class="score-item">
                          <span class="score-label">加分:</span>
                          <span class="score-value">{{ record.bonus_score }}</span>
                        </div>
                        <div class="score-item">
                          <span class="score-label">最终得分:</span>
                          <span class="score-value final-score">{{ record.final_score }}</span>
                        </div>
                      </div>
                      
                      <div v-if="record.veto_triggered" class="veto-warning">
                        <span class="veto-icon">⚠️</span>
                        <span class="veto-text">一票否决: {{ record.veto_reason }}</span>
                      </div>
                      
                      <div v-if="record.score_details && Object.keys(record.score_details).length > 0" class="score-details">
                        <div class="details-title">评分明细:</div>
                        <div class="details-content">
                          <div v-for="(value, key) in record.score_details" :key="key" class="detail-item">
                            <span class="detail-key">{{ key }}:</span>
                            <span class="detail-value">{{ value }}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div class="record-meta">
                        <span class="meta-item">
                          <span class="meta-label">评分方式:</span>
                          <span class="meta-value">{{ record.scoring_type === 'auto' ? '自动评分' : '人工评分' }}</span>
                        </span>
                        <span class="meta-item">
                          <span class="meta-label">评分时间:</span>
                          <span class="meta-value">{{ formatDate(record.scored_at) }}</span>
                        </span>
                        <span v-if="record.is_confirmed" class="meta-item confirmed">
                          <span class="meta-label">✓ 已确认</span>
                        </span>
                      </div>
                      
                      <!-- 异议申请按钮 -->
                      <div v-if="!record.is_confirmed && !record.has_appeal" class="record-actions">
                        <button class="btn-appeal" @click="openAppealDialog(record)">
                          📝 提交异议
                        </button>
                      </div>
                      <div v-else-if="record.has_appeal" class="appeal-status">
                        <span class="appeal-badge">已提交异议</span>
                      </div>
                      
                      <!-- 确认评分按钮 -->
                      <div v-if="!record.is_confirmed" class="record-actions">
                        <button class="btn-confirm" @click="openConfirmDialog(record)">
                          ✓ 确认评分
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 查看评分结果按钮 -->
                <div v-if="!submission.showScoring" class="view-scoring-btn">
                  <button class="btn-view-scoring" @click="loadScoringResults(submission)">
                    📊 查看评分结果
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 异议申请对话框 -->
    <div v-if="showAppealDialog" class="appeal-dialog-overlay" @click="closeAppealDialog">
      <div class="appeal-dialog" @click.stop>
        <div class="dialog-header">
          <h2 class="dialog-title">提交异议</h2>
          <button class="dialog-close" @click="closeAppealDialog">✕</button>
        </div>
        
        <div class="dialog-body">
          <!-- 评分信息展示 -->
          <div class="appeal-info">
            <div class="info-section">
              <span class="info-label">文件名称:</span>
              <span class="info-value">{{ currentAppealRecord?.file_name }}</span>
            </div>
            <div class="info-section">
              <span class="info-label">当前得分:</span>
              <span class="info-value score">{{ currentAppealRecord?.final_score }}</span>
            </div>
            <div class="info-section">
              <span class="info-label">当前等级:</span>
              <span :class="['info-value', 'grade', `grade-${currentAppealRecord?.grade}`]">
                {{ currentAppealRecord?.grade }}
              </span>
            </div>
          </div>
          
          <!-- 异议理由输入 -->
          <div class="appeal-form">
            <label class="form-label">异议理由 <span class="required">*</span></label>
            <textarea
              v-model="appealForm.reason"
              class="form-textarea"
              rows="6"
              placeholder="请详细说明您对评分的异议理由（至少20个字符）"
              @input="validateAppealReason"
            ></textarea>
            <div class="form-hint">
              <span :class="['char-count', { 'error': appealForm.reason.length < 20 && appealForm.reason.length > 0 }]">
                {{ appealForm.reason.length }}/20 字符
              </span>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeAppealDialog">取消</button>
          <button
            class="btn-submit"
            @click="submitAppeal"
            :disabled="appealForm.reason.length < 20 || submittingAppeal"
          >
            <span v-if="!submittingAppeal">提交异议</span>
            <span v-else class="loading-text">
              <span class="loading-spinner"></span>
              提交中...
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- 评分确认对话框 -->
    <div v-if="showConfirmDialog" class="confirm-dialog-overlay" @click="closeConfirmDialog">
      <div class="confirm-dialog" @click.stop>
        <div class="dialog-header">
          <h2 class="dialog-title">确认评分</h2>
          <button class="dialog-close" @click="closeConfirmDialog">✕</button>
        </div>
        
        <div class="dialog-body">
          <!-- 评分信息展示 -->
          <div class="confirm-info">
            <div class="info-section">
              <span class="info-label">文件名称:</span>
              <span class="info-value">{{ currentConfirmRecord?.file_name }}</span>
            </div>
            <div class="info-section">
              <span class="info-label">最终得分:</span>
              <span class="info-value score">{{ currentConfirmRecord?.final_score }}</span>
            </div>
            <div class="info-section">
              <span class="info-label">等级:</span>
              <span :class="['info-value', 'grade', `grade-${currentConfirmRecord?.grade}`]">
                {{ currentConfirmRecord?.grade }}
              </span>
            </div>
            <div class="info-section">
              <span class="info-label">评分方式:</span>
              <span class="info-value">{{ currentConfirmRecord?.scoring_type === 'auto' ? '自动评分' : '人工评分' }}</span>
            </div>
          </div>
          
          <!-- 确认提示 -->
          <div class="confirm-message">
            <p>确认此评分结果后，您将无法再提交异议。请仔细核对评分信息。</p>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeConfirmDialog">取消</button>
          <button
            class="btn-confirm-submit"
            @click="submitConfirm"
            :disabled="submittingConfirm"
          >
            <span v-if="!submittingConfirm">确认评分</span>
            <span v-else class="loading-text">
              <span class="loading-spinner"></span>
              确认中...
            </span>
          </button>
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
const showAppealDialog = ref(false);
const currentAppealRecord = ref<any>(null);
const submittingAppeal = ref(false);
const appealForm = ref({
  reason: ''
});
const showConfirmDialog = ref(false);
const currentConfirmRecord = ref<any>(null);
const submittingConfirm = ref(false);

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

const loadSubmissions = async () => {
  loadingSubmissions.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/teacher/materials/submissions`);
    const data = await response.json();
    submissions.value = (data.submissions || []).map(sub => ({
      ...sub,
      showScoring: false,
      loadingScoring: false,
      scoringData: null
    }));
  } catch (error) {
    console.error('加载提交记录失败:', error);
  } finally {
    loadingSubmissions.value = false;
  }
};

// 加载评分结果
const loadScoringResults = async (submission: any) => {
  submission.loadingScoring = true;
  submission.showScoring = true;
  
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/teacher/materials/submissions/${submission.submission_id}/scoring`
    );
    const data = await response.json();
    submission.scoringData = data;
  } catch (error) {
    console.error('加载评分结果失败:', error);
    submission.scoringData = {
      scoring_records: [],
      has_scoring: false,
      message: '加载评分结果失败'
    };
  } finally {
    submission.loadingScoring = false;
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

// 打开异议申请对话框
const openAppealDialog = (record: any) => {
  currentAppealRecord.value = record;
  appealForm.value.reason = '';
  showAppealDialog.value = true;
};

// 关闭异议申请对话框
const closeAppealDialog = () => {
  showAppealDialog.value = false;
  currentAppealRecord.value = null;
  appealForm.value.reason = '';
};

// 验证异议理由
const validateAppealReason = () => {
  // 实时验证，长度至少20个字符
  return appealForm.value.reason.length >= 20;
};

// 提交异议
const submitAppeal = async () => {
  if (appealForm.value.reason.length < 20) {
    alert('异议理由至少需要20个字符');
    return;
  }

  if (!currentAppealRecord.value) {
    alert('未选择评分记录');
    return;
  }

  if (!confirm('确定要提交异议吗？提交后将通知管理员进行复核。')) {
    return;
  }

  submittingAppeal.value = true;
  try {
    const response = await fetch(`${API_BASE_URL}/api/scoring/appeals`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        scoring_record_id: currentAppealRecord.value.id,
        appeal_reason: appealForm.value.reason.trim()
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '提交异议失败');
    }

    const data = await response.json();
    alert('异议提交成功！管理员将在3个工作日内进行复核。');
    
    // 标记该记录已提交异议
    currentAppealRecord.value.has_appeal = true;
    
    closeAppealDialog();
    
    // 刷新提交记录
    loadSubmissions();
  } catch (error) {
    console.error('提交异议失败:', error);
    alert(`提交异议失败: ${error instanceof Error ? error.message : '未知错误'}`);
  } finally {
    submittingAppeal.value = false;
  }
};

// 打开评分确认对话框
const openConfirmDialog = (record: any) => {
  currentConfirmRecord.value = record;
  showConfirmDialog.value = true;
};

// 关闭评分确认对话框
const closeConfirmDialog = () => {
  showConfirmDialog.value = false;
  currentConfirmRecord.value = null;
};

// 提交评分确认
const submitConfirm = async () => {
  if (!currentConfirmRecord.value) {
    alert('未选择评分记录');
    return;
  }

  if (!confirm('确定要确认此评分结果吗？确认后将无法再提交异议。')) {
    return;
  }

  submittingConfirm.value = true;
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/scoring/confirm/${currentConfirmRecord.value.id}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '确认评分失败');
    }

    const data = await response.json();
    alert('评分已确认！');
    
    // 标记该记录已确认
    currentConfirmRecord.value.is_confirmed = true;
    
    closeConfirmDialog();
    
    // 刷新提交记录
    loadSubmissions();
  } catch (error) {
    console.error('确认评分失败:', error);
    alert(`确认评分失败: ${error instanceof Error ? error.message : '未知错误'}`);
  } finally {
    submittingConfirm.value = false;
  }
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

/* 评分结果样式 */
.scoring-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #EEEEEE;
  background: #FAFAFA;
  border-radius: 8px;
  padding: 16px;
}

.scoring-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.scoring-title {
  font-size: 15px;
  font-weight: 600;
  color: #212121;
}

.btn-collapse {
  background: none;
  border: none;
  color: #1976D2;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-collapse:hover {
  background: rgba(25, 118, 210, 0.1);
}

.empty-scoring {
  text-align: center;
  padding: 24px;
  color: #757575;
  font-size: 14px;
}

.scoring-records {
  display: grid;
  gap: 12px;
}

.scoring-record {
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
}

.scoring-record:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #1976D2;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #EEEEEE;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #212121;
}

.grade-badge {
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 12px;
  text-align: center;
  min-width: 60px;
}

.grade-优秀 {
  background: #E8F5E9;
  color: #2E7D32;
}

.grade-良好 {
  background: #E3F2FD;
  color: #1565C0;
}

.grade-合格 {
  background: #FFF3E0;
  color: #E65100;
}

.grade-不合格 {
  background: #FFEBEE;
  color: #C62828;
}

.record-scores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  background: #F5F5F5;
  border-radius: 6px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-label {
  font-size: 12px;
  color: #757575;
  font-weight: 500;
}

.score-value {
  font-size: 16px;
  font-weight: 600;
  color: #212121;
}

.score-value.final-score {
  font-size: 18px;
  color: #1976D2;
}

.veto-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #FFEBEE;
  border-left: 4px solid #C62828;
  border-radius: 4px;
  margin-bottom: 12px;
}

.veto-icon {
  font-size: 18px;
}

.veto-text {
  font-size: 13px;
  color: #C62828;
  font-weight: 500;
}

.score-details {
  margin-bottom: 12px;
  padding: 12px;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
}

.details-title {
  font-size: 13px;
  font-weight: 600;
  color: #424242;
  margin-bottom: 8px;
}

.details-content {
  display: grid;
  gap: 6px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #616161;
}

.detail-key {
  font-weight: 500;
  color: #424242;
}

.detail-value {
  color: #757575;
}

.record-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: #757575;
  padding-top: 12px;
  border-top: 1px solid #EEEEEE;
}

.meta-item {
  display: flex;
  gap: 4px;
}

.meta-item.confirmed {
  color: #2E7D32;
  font-weight: 600;
}

.meta-label {
  color: #9E9E9E;
}

.meta-value {
  color: #616161;
  font-weight: 500;
}

.view-scoring-btn {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.btn-view-scoring {
  padding: 8px 16px;
  font-size: 13px;
  background: #1976D2;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-view-scoring:hover {
  background: #1565C0;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 异议申请样式 */
.record-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-appeal {
  padding: 8px 16px;
  font-size: 13px;
  background: #FF9800;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-appeal:hover {
  background: #F57C00;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.appeal-status {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.appeal-badge {
  padding: 6px 12px;
  font-size: 12px;
  background: #E3F2FD;
  color: #1565C0;
  border-radius: 12px;
  font-weight: 500;
}

/* 异议对话框 */
.appeal-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.appeal-dialog {
  background: #FFFFFF;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #FAFAFA;
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
  background: #E0E0E0;
  color: #212121;
}

.dialog-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.appeal-info {
  background: #F5F5F5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  border-left: 4px solid #FF9800;
}

.info-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #757575;
  font-weight: 500;
}

.info-value {
  color: #212121;
  font-weight: 600;
}

.info-value.score {
  font-size: 16px;
  color: #1976D2;
}

.info-value.grade {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  text-align: center;
  min-width: 60px;
}

.info-value.grade.grade-优秀 {
  background: #E8F5E9;
  color: #2E7D32;
}

.info-value.grade.grade-良好 {
  background: #E3F2FD;
  color: #1565C0;
}

.info-value.grade.grade-合格 {
  background: #FFF3E0;
  color: #E65100;
}

.info-value.grade.grade-不合格 {
  background: #FFEBEE;
  color: #C62828;
}

.appeal-form {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #424242;
  margin-bottom: 8px;
}

.required {
  color: #C62828;
  margin-left: 2px;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  outline: none;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s ease;
}

.form-textarea:focus {
  border-color: #FF9800;
  box-shadow: 0 0 0 3px rgba(255, 152, 0, 0.1);
}

.form-hint {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
  font-size: 12px;
}

.char-count {
  color: #9E9E9E;
  font-weight: 500;
}

.char-count.error {
  color: #C62828;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: #FAFAFA;
  border-top: 1px solid #EEEEEE;
}

.btn-cancel {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  background: #FFFFFF;
  color: #616161;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: #FAFAFA;
  border-color: #BDBDBD;
}

.btn-submit {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  background: #FF9800;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-submit:hover:not(:disabled) {
  background: #F57C00;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.btn-submit:disabled {
  background: #E0E0E0;
  color: #9E9E9E;
  cursor: not-allowed;
}

/* 确认评分对话框样式 */
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.confirm-dialog {
  background: #FFFFFF;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.confirm-info {
  background: #F5F5F5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  border-left: 4px solid #4CAF50;
}

.confirm-message {
  background: #E8F5E9;
  border-left: 4px solid #4CAF50;
  border-radius: 4px;
  padding: 12px 16px;
  margin-bottom: 24px;
}

.confirm-message p {
  margin: 0;
  font-size: 14px;
  color: #2E7D32;
  line-height: 1.6;
}

.btn-confirm {
  padding: 8px 16px;
  font-size: 13px;
  background: #4CAF50;
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm:hover {
  background: #45a049;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-confirm-submit {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  background: #4CAF50;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm-submit:hover:not(:disabled) {
  background: #45a049;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-confirm-submit:disabled {
  background: #E0E0E0;
  color: #9E9E9E;
  cursor: not-allowed;
}
</style>
