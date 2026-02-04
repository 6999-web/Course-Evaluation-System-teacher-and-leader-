// 审核反馈相关API
import request from './config'
import type { 
  ReviewListParams, 
  ReviewListResponse, 
  ReviewDetailResponse, 
  ReviewFormData, 
  ReviewActionParams
} from '../types/review'

/**
 * 获取审核反馈列表
 */
export function getReviewList(params: ReviewListParams): Promise<ReviewListResponse> {
  return request({
    url: '/api/reviews',
    method: 'get',
    params
  })
}

/**
 * 获取审核反馈详情
 */
export function getReviewDetail(id: number): Promise<ReviewDetailResponse> {
  return request({
    url: `/api/reviews/${id}`,
    method: 'get'
  })
}

/**
 * 创建审核反馈
 */
export function createReview(data: ReviewFormData): Promise<any> {
  return request({
    url: '/api/reviews',
    method: 'post',
    data
  })
}

/**
 * 更新审核反馈
 */
export function updateReview(id: number, data: Partial<ReviewFormData>): Promise<any> {
  return request({
    url: `/api/reviews/${id}`,
    method: 'put',
    data
  })
}

/**
 * 执行审核操作
 */
export function reviewAction(params: ReviewActionParams): Promise<any> {
  return request({
    url: '/api/reviews/action',
    method: 'post',
    data: params
  })
}

/**
 * 删除审核反馈
 */
export function deleteReview(id: number): Promise<any> {
  return request({
    url: `/api/reviews/${id}`,
    method: 'delete'
  })
}

/**
 * 获取审核统计数据
 */
export function getReviewStats(): Promise<any> {
  return request({
    url: '/api/reviews/stats',
    method: 'get'
  })
}

/**
 * 确认评分结果
 */
export function confirmScore(scoringRecordId: number): Promise<any> {
  return request({
    url: `/api/scoring/confirm/${scoringRecordId}`,
    method: 'post'
  })
}
