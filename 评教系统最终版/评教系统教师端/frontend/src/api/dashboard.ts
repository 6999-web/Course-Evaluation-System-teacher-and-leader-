import apiClient from './config'

// 获取仪表盘统计数据
export const getDashboardStats = () => {
  return apiClient.get('/dashboard/stats')
}

// 获取评价趋势数据
export const getEvaluationTrend = (params: {
  timeRange: string
  teacherId?: string
}) => {
  return apiClient.get('/dashboard/trend', { params })
}

// 获取评价维度分析数据
export const getDimensionAnalysis = (params: {
  semester: string
  teacherId?: string
}) => {
  return apiClient.get('/dashboard/dimension', { params })
}

// 获取最近评价数据
export const getRecentEvaluations = (params: {
  limit?: number
  teacherId?: string
}) => {
  return apiClient.get('/dashboard/recent-evaluations', { params })
}