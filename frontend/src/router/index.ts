import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('../views/LoginView.vue') },
    {
      path: '/', component: MainLayout, redirect: '/dashboard',
      children: [
      { path: 'dashboard', name: 'DashboardView', component: () => import('../views/DashboardView.vue'), meta: { title: '总览看板' } },
      { path: 'segment', name: 'SegmentView', component: () => import('../views/SegmentView.vue'), meta: { title: '玩家分群' } },
      { path: 'funnel', name: 'FunnelView', component: () => import('../views/FunnelView.vue'), meta: { title: '行为漏斗' } },
      { path: 'churn', name: 'ChurnView', component: () => import('../views/ChurnView.vue'), meta: { title: '流失预警' } },
      { path: 'ltv', name: 'LtvView', component: () => import('../views/LtvView.vue'), meta: { title: 'LTV预测' } },
      { path: 'experiment', name: 'ExperimentView', component: () => import('../views/ExperimentView.vue'), meta: { title: 'A/B实验' } },
      { path: 'gacha', name: 'GachaView', component: () => import('../views/GachaView.vue'), meta: { title: '付费与抽卡' } },
      { path: 'feedback', name: 'FeedbackView', component: () => import('../views/FeedbackView.vue'), meta: { title: '版本反馈' } },
      { path: 'chat', name: 'ChatView', component: () => import('../views/ChatView.vue'), meta: { title: 'LLM智能助手' } },
      { path: 'data', name: 'DataView', component: () => import('../views/DataView.vue'), meta: { title: '数据管理' } }
      ]
    }
  ]
})
router.beforeEach(to => {
  if (to.path !== '/login' && !localStorage.getItem('token')) return '/login'
})
export default router
