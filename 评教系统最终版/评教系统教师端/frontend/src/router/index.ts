import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import EvaluationView from '@/views/EvaluationView.vue'
import ReportView from '@/views/ReportView.vue'
import BatchOperationView from '@/views/BatchOperationView.vue'
import PersonalGrowthProfileView from '@/views/PersonalGrowthProfileView.vue'
import EvaluationTrendPredictionView from '@/views/EvaluationTrendPredictionView.vue'
import TestView from '@/views/TestView.vue'
import MaterialView from '@/views/MaterialView.vue'
import MaterialSubmission from '@/views/MaterialSubmission.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView
  },
  {
    path: '/evaluation',
    name: 'evaluation',
    component: EvaluationView
  },
  {
    path: '/report',
    name: 'report',
    component: ReportView
  },
  {
    path: '/batch',
    name: 'batch',
    component: BatchOperationView
  },
  {
    path: '/profile',
    name: 'profile',
    component: PersonalGrowthProfileView
  },
  {
    path: '/trend',
    name: 'trend',
    component: EvaluationTrendPredictionView
  },
  {
    path: '/materials',
    name: 'materials',
    component: MaterialView
  },
  {
    path: '/submission',
    name: 'submission',
    component: MaterialSubmission
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router