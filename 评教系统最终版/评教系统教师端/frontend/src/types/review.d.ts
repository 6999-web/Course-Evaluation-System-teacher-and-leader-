// 审核反馈类型定义
import { ReviewStatus, ReviewType } from '@/types/enums';

// 审核反馈列表参数
export interface ReviewListParams {
  page?: number;
  pageSize?: number;
  status?: ReviewStatus;
  type?: ReviewType;
  startTime?: string;
  endTime?: string;
  keyword?: string;
}

// 审核反馈项
export interface ReviewItem {
  id: number;
  title: string;
  content: string;
  type: ReviewType;
  status: ReviewStatus;
  creator: string;
  createTime: string;
  reviewer: string;
  reviewTime: string;
  feedback: string;
  attachments?: string[];
  relatedId: number; // 关联的改进计划ID或申诉ID
}

// 审核反馈详情
export interface ReviewDetail extends ReviewItem {
  // 详细信息
  reviewComments?: string[];
  revisionHistory?: {
    id: number;
    content: string;
    createTime: string;
    creator: string;
  }[];
}

// 审核反馈表单数据
export interface ReviewFormData {
  id?: number;
  title: string;
  content: string;
  type: ReviewType;
  status: ReviewStatus;
  feedback: string;
  attachments?: string[];
  relatedId: number;
}

// 审核反馈列表响应
export interface ReviewListResponse {
  total: number;
  items: ReviewItem[];
}

// 审核反馈详情响应
export interface ReviewDetailResponse {
  data: ReviewDetail;
}

// 审核操作参数
export interface ReviewActionParams {
  id: number;
  status: ReviewStatus;
  feedback: string;
  attachments?: string[];
}
