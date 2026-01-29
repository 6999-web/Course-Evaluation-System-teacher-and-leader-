/**
 * API 请求工具
 * 自动添加认证令牌到请求头
 */

const API_BASE_URL = 'http://120.26.29.145:8000'

/**
 * 获取存储的令牌
 */
export function getToken(): string | null {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
}

/**
 * 保存令牌
 */
export function setToken(token: string, remember: boolean = false): void {
  const storage = remember ? localStorage : sessionStorage
  storage.setItem('access_token', token)
}

/**
 * 删除令牌
 */
export function removeToken(): void {
  localStorage.removeItem('access_token')
  sessionStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
  sessionStorage.removeItem('user_info')
}

/**
 * 获取用户信息
 */
export function getUserInfo(): any {
  const userInfo = localStorage.getItem('user_info') || sessionStorage.getItem('user_info')
  return userInfo ? JSON.parse(userInfo) : null
}

/**
 * 发送认证请求
 */
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken()
  
  // 初始化请求头
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }
  
  // 安全地合并自定义请求头
  if (options.headers) {
    const customHeaders = new Headers(options.headers)
    customHeaders.forEach((value, key) => {
      headers[key] = value
    })
  }
  
  // 如果有令牌，添加到请求头
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  })
  
  // 如果返回 401，说明令牌失效，清除令牌并跳转到登录页
  if (response.status === 401) {
    removeToken()
    window.location.href = '/auth'
  }
  
  return response
}

/**
 * GET 请求
 */
export async function apiGet(endpoint: string): Promise<any> {
  const response = await apiRequest(endpoint, { method: 'GET' })
  return response.json()
}

/**
 * POST 请求
 */
export async function apiPost(endpoint: string, data: any): Promise<any> {
  const response = await apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  })
  return response.json()
}

/**
 * PUT 请求
 */
export async function apiPut(endpoint: string, data: any): Promise<any> {
  const response = await apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
  return response.json()
}

/**
 * DELETE 请求
 */
export async function apiDelete(endpoint: string): Promise<any> {
  const response = await apiRequest(endpoint, { method: 'DELETE' })
  return response.json()
}

/**
 * 登出
 */
export async function logout(): Promise<void> {
  try {
    await apiPost('/api/logout', {})
  } catch (error) {
    console.error('登出错误:', error)
  } finally {
    removeToken()
    window.location.href = '/auth'
  }
}
