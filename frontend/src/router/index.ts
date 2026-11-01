import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'

const pages = [
  ['dashboard', 'DashboardView', '总览看板'],
  ['segment', 'SegmentView', '玩家分群'],
  ['funnel', 'FunnelView', '行为漏斗'],
  ['churn', 'ChurnView', '流失预警'],
  ['ltv', 'LtvView', 'LTV预测'],
  ['experiment', 'ExperimentView', 'A/B实验'],
  ['gacha', 'GachaView', '付费与抽卡'],
  ['feedback', 'FeedbackView', '版本反馈'],
  ['chat', 'ChatView', 'LLM智能助手'],
  ['data', 'DataView', '数据管理'],
] as const

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/LandingView.vue') },
    { path: '/login', redirect: '/?auth=login' },
    {
      path: '/app', component: MainLayout,
      children: [
        { path: '', redirect: '/dashboard' },
        ...pages.map(([p, n, t]) => ({
          path: '/' + p, name: n,
          component: () => import(`../views/${n}.vue`),
          meta: { title: t }
        }))
      ]
    }
  ]
})
router.beforeEach(to => {
  const inApp = to.path !== '/' && to.path !== '/login'
  if (inApp && !localStorage.getItem('token')) return { path: '/', query: { auth: 'login' } }
})
export default router
