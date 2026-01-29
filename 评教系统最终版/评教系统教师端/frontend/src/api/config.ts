import axios from 'axios'

// 创建Axios实例
const apiClient = axios.create({
  baseURL: '/api',  // 基础URL，会自动拼接在请求URL前面
  timeout: 10000,  // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么，比如添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    return response.data
  },
  (error) => {
    // 对响应错误做点什么
    if (error.response) {
      // 请求已发出，服务器返回状态码不在2xx范围
      console.error('API Error:', error.response.data)
      console.error('Status:', error.response.status)
      
      // 处理401未授权错误
      if (error.response.status === 401) {
        // 清除token并跳转到登录页
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('Network Error:', error.request)
    } else {
      // 请求配置出错
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient