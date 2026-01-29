import apiClient from './config'

// 生成评价报告
export const generateReport = (params: {
  semester: string
  reportType: string
  courseId?: string
  compareWith?: string
}) => {
  return apiClient.post('/report/generate', params)
}

// 获取报告数据
export const getReportData = (id: string) => {
  return apiClient.get(`/report/data/${id}`)
}

// 导出报告
export const exportReport = (id: string, format: 'pdf' | 'excel') => {
  return apiClient.get(`/report/export/${id}`, {
    params: { format },
    responseType: 'blob' // 导出文件需要设置响应类型为blob
  })
}

// 获取报告历史
export const getReportHistory = (params: {
  page?: number
  pageSize?: number
}) => {
  return apiClient.get('/report/history', { params })
}