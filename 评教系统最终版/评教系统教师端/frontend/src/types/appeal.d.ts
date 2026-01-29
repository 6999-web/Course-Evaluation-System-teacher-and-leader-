// 申诉类型定义
import { AppealStatus, AppealType } from '@/types/enums';

// 申诉列表参数
export interface AppealListParams {
  page?: number;
  pageSize?: number;
  status?: AppealStatus;
  type?: AppealType;
  startTime?: string;
  endTime?: string;
  keyword?: string;
}

// 申诉项
export interface AppealItem {
  id: number;
  title: string;
  type: AppealType;
  status: AppealStatus;
  content: string;
  reason: string;
  evidence?: string[];
  creator: string;
  createTime: string;
  reviewer: string;
  reviewTime: string;
  feedback: string;
  reply?: string;
  replyTime?: string;
  relatedId: number; // 关联的评价ID或其他相关ID
}

// 申诉详情
export interface AppealDetail extends AppealItem {
  // 详细信息
  appealHistory?: {
    id: number;
    content: string;
    createTime: string;
    creator: string;
    type: 'appeal' | 'reply' | 'review';
  }[];
}

// 申诉表单数据
export interface AppealFormData {
  id?: number;
  title: string;
  type: AppealType;
  content: string;
  reason: string;
  evidence?: string[];
  relatedId: number;
}

// 申诉回复表单数据
export interface AppealReplyData {
  id: number;
  reply: string;
}

// 申诉审核表单数据
export interface AppealReviewData {
  id: number;
  status: AppealStatus;
  feedback: string;
}

// 申诉列表响应
export interface AppealListResponse {
  total: number;
  items: AppealItem[];
}

// 申诉详情响应
export interface AppealDetailResponse {
  data: AppealDetail;
}
