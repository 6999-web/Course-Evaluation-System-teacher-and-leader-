import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('../views/Auth.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true },
    props: route => ({
      activeNav: route.query.activeNav || 'monitoring'
    })
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查认证状态
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  
  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    if (!token) {
      // 未登录，跳转到登录页
      next('/auth')
    } else {
      // 已登录，允许访问
      next()
    }
  } else {
    // 不需要认证的路由 - 允许所有用户访问登录页
    next()
  }
})

export default router
