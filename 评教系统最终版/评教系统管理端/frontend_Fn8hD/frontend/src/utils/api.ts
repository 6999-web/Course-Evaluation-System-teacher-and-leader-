/**
 * API 请求工具
 * 自动添加认证令牌到请求头
 */

const API_BASE_URL = 'http://localhost:8001'

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

// 自动登录锁，防止多个请求同时触发自动登录
let autoLoginPromise: Promise<string | null> | null = null

/**
 * 自动登录函数
 */
async function autoLogin(): Promise<string | null> {
  // 如果已经有自动登录在进行中，等待它完成
  if (autoLoginPromise) {
    return autoLoginPromise
  }
  
  autoLoginPromise = (async () => {
    try {
      console.log('尝试自动登录...')
      const loginResponse = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'admin123'
        })
      })
      
      if (loginResponse.ok) {
        const loginData = await loginResponse.json()
        const token = loginData.token.access_token
        
        // 保存新的token
        localStorage.setItem('access_token', token)
        localStorage.setItem('user_info', JSON.stringify(loginData.user))
        sessionStorage.setItem('access_token', token)
        sessionStorage.setItem('user_info', JSON.stringify(loginData.user))
        
        console.log('自动登录成功')
        return token
      }
      
      console.log('自动登录失败')
      return null
    } catch (error) {
      console.error('自动登录错误:', error)
      return null
    } finally {
      // 清除锁
      autoLoginPromise = null
    }
  })()
  
  return autoLoginPromise
}

/**
 * 发送认证请求
 */
export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  let token = getToken()
  
  // 如果没有token，先尝试自动登录
  if (!token) {
    console.log('未检测到token，尝试自动登录...')
    token = await autoLogin()
    
    if (!token) {
      // 自动登录失败，跳转到登录页
      window.location.href = '/auth'
      throw new Error('未授权')
    }
  }
  
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
  
  // 添加令牌到请求头
  headers['Authorization'] = `Bearer ${token}`
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  })
  
  // 如果返回 401，说明令牌失效，尝试自动登录并重试
  if (response.status === 401) {
    console.log('检测到401错误，token可能已过期，尝试重新登录...')
    
    const newToken = await autoLogin()
    
    if (newToken) {
      // 使用新token重试请求
      const retryHeaders = { ...headers }
      retryHeaders['Authorization'] = `Bearer ${newToken}`
      
      const retryResponse = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: retryHeaders
      })
      
      if (retryResponse.ok || retryResponse.status !== 401) {
        console.log('重试请求成功')
        return retryResponse
      }
    }
    
    // 如果自动登录失败，清除token并跳转到登录页
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
