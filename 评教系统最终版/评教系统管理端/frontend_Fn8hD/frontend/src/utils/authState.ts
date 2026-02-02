/**
 * 全局认证状态管理
 * 用于确保所有组件在Token准备好后再发起API请求
 */

import { ref } from 'vue';

// 认证状态
export const isAuthReady = ref(false);
export const authError = ref<string | null>(null);

// 等待认证准备就绪的Promise
let authReadyPromise: Promise<void> | null = null;

/**
 * 标记认证已准备就绪
 */
export function setAuthReady() {
  isAuthReady.value = true;
  authError.value = null;
  console.log('✅ 认证状态已就绪');
}

/**
 * 标记认证失败
 */
export function setAuthError(error: string) {
  isAuthReady.value = false;
  authError.value = error;
  console.error('❌ 认证失败:', error);
}

/**
 * 重置认证状态
 */
export function resetAuthState() {
  isAuthReady.value = false;
  authError.value = null;
  authReadyPromise = null;
}

/**
 * 等待认证准备就绪
 * 如果已经就绪，立即返回
 * 如果未就绪，等待最多5秒
 */
export async function waitForAuth(): Promise<boolean> {
  // 如果已经就绪，直接返回
  if (isAuthReady.value) {
    return true;
  }
  
  // 如果已经有等待Promise，复用它
  if (authReadyPromise) {
    await authReadyPromise;
    return isAuthReady.value;
  }
  
  // 创建新的等待Promise
  authReadyPromise = new Promise((resolve) => {
    const maxWaitTime = 5000; // 最多等待5秒
    const checkInterval = 100; // 每100ms检查一次
    let elapsed = 0;
    
    const timer = setInterval(() => {
      elapsed += checkInterval;
      
      if (isAuthReady.value) {
        clearInterval(timer);
        resolve();
      } else if (elapsed >= maxWaitTime) {
        clearInterval(timer);
        console.warn('⚠️ 等待认证超时');
        resolve();
      }
    }, checkInterval);
  });
  
  await authReadyPromise;
  authReadyPromise = null;
  
  return isAuthReady.value;
}

/**
 * 检查Token是否存在
 */
export function hasToken(): boolean {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  return !!token;
}
