import apiClient from './config'

// 获取评价列表
export const getEvaluationList = (params: {
  semester?: string
  courseName?: string
  status?: string
  page?: number
  pageSize?: number
}) => {
  return apiClient.get('/evaluation/list', { params })
}

// 获取评价详情
export const getEvaluationDetail = (id: string) => {
  return apiClient.get(`/evaluation/detail/${id}`)
}

// 获取评价进度
export const getEvaluationProgress = (id: string) => {
  return apiClient.get(`/evaluation/progress/${id}`)
}

// 获取评价计划
export const getEvaluationPlan = (id: string) => {
  return apiClient.get(`/evaluation/plan/${id}`)
}

// 导出评价数据
export const exportEvaluationData = (params: {
  semester?: string
  courseId?: string
}) => {
  return apiClient.get('/evaluation/export', { 
    params, 
    responseType: 'blob' // 导出文件需要设置响应类型为blob
  })
}