/**
 * 异议申请相关 API
 */

import apiClient from './config'
import { AppealStatus } from '@/types/enums'

// 提交异议申请
export const submitAppeal = (data: {
  scoring_record_id: number
  appeal_reason: string
}) => {
  return apiClient.post('/api/appeals', data)
}

// 获取异议列表
export const getAppeals = (params?: {
  status?: string
  teacher_id?: string
}) => {
  return apiClient.get('/api/appeals', { params })
}

// 获取异议详情
export const getAppealDetail = (appealId: number) => {
  return apiClient.get(`/api/appeals/${appealId}`)
}

// 管理员审核异议
export const reviewAppeal = (appealId: number, data: {
  status: AppealStatus
  review_comment?: string
  new_score?: number
}) => {
  return apiClient.post(`/api/appeals/${appealId}/review`, data)
}

// 管理员回复异议
export const replyAppeal = (appealId: number, data: {
  reply_content: string
}) => {
  return apiClient.post(`/api/appeals/${appealId}/reply`, data)
}

// 撤销异议申请
export const withdrawAppeal = (appealId: number) => {
  return apiClient.post(`/api/appeals/${appealId}/withdraw`)
}