/**
 * 材料分发与回收相关 API
 */

import { apiRequest } from './api';

const API_BASE_URL = 'http://localhost:8001';

// 获取认证token
const getAuthToken = () => {
  // 优先从 localStorage 获取，其次从 sessionStorage 获取
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || '';
};

// 通用请求函数 - 使用统一的apiRequest来处理认证
async function request(url: string, options: RequestInit = {}) {
  try {
    const response = await apiRequest(url, options);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '请求失败' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    return response.json();
  } catch (error: any) {
    console.error('API请求错误:', error);
    throw error;
  }
}

/**
 * 生成考评表
 */
export async function generateEvaluationForm(data: {
  name: string;
  start_date: string;
  end_date: string;
  dimensions: string[];
  participants: string[];
}) {
  return request('/api/evaluation-forms/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 获取考评表列表
 */
export async function getEvaluationForms() {
  return request('/api/evaluation-forms');
}

/**
 * 获取考评表详情
 */
export async function getEvaluationForm(formId: string) {
  return request(`/api/evaluation-forms/${formId}`);
}

/**
 * 分发材料
 */
export async function distributeMaterials(data: {
  material_ids: string[];
  material_types: string[];
  distribution_type: 'batch' | 'targeted';
  target_teachers: string[];
}) {
  return request('/api/materials/distribute', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 获取分发记录
 */
export async function getDistributionRecords(params?: {
  start_date?: string;
  end_date?: string;
  teacher_id?: string;
}) {
  const queryString = params
    ? '?' + new URLSearchParams(params as any).toString()
    : '';
  return request(`/api/materials/distribution-records${queryString}`);
}

/**
 * 获取提交材料列表
 */
export async function getMaterialSubmissions(params?: {
  status?: string;
  teacher_id?: string;
}) {
  const queryString = params
    ? '?' + new URLSearchParams(params as any).toString()
    : '';
  return request(`/api/materials/submissions${queryString}`);
}

/**
 * 更新审核状态
 */
export async function updateReviewStatus(
  submissionId: string,
  data: {
    status: 'approved' | 'rejected' | 'needs_revision';
    feedback?: string;
  }
) {
  return request(`/api/materials/submissions/${submissionId}/review`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 下载材料
 */
export function downloadMaterial(fileId: string) {
  const token = getAuthToken();
  const url = `${API_BASE_URL}/api/materials/download/${fileId}`;
  
  // 创建隐藏的a标签进行下载
  const link = document.createElement('a');
  link.href = token ? `${url}?token=${token}` : url;
  link.download = fileId;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * 获取所有教师列表（用于分发目标选择）
 */
export async function getTeachers() {
  // 临时返回模拟数据，实际应从后端API获取
  return {
    teachers: [
      { teacher_id: 'teacher_001', teacher_name: '张三', department: '计算机学院' },
      { teacher_id: 'teacher_002', teacher_name: '李四', department: '电子工程学院' },
      { teacher_id: 'teacher_003', teacher_name: '王五', department: '人文学院' },
      { teacher_id: 'teacher_004', teacher_name: '赵六', department: '数学学院' },
      { teacher_id: 'teacher_005', teacher_name: '孙七', department: '物理学院' },
    ]
  };
}
