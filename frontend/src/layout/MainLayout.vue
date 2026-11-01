<template>
  <el-container style="height: 100vh">
    <el-aside width="210px" style="background:#111827">
      <div style="color:#fff;padding:18px 16px;font-weight:700;line-height:1.5">二次元游戏<br/>玩家行为分析</div>
      <el-menu router :default-active="$route.path" background-color="#111827" text-color="#D1D5DB" active-text-color="#fff">
        <el-menu-item v-for="p in pages" :key="p.path" :index="p.path">{{ p.title }}</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="display:flex;align-items:center;justify-content:space-between;background:#fff;border-bottom:1px solid #E5E7EB">
        <b>{{ $route.meta.title }}</b>
        <span>{{ user.username }}（{{ user.role }}）
          <el-button text @click="onLogout">退出</el-button></span>
      </el-header>
      <el-main style="background:#F9FAFB"><router-view /></el-main>
    </el-container>
  </el-container>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
const pages = [
  { path: '/dashboard', title: '总览看板' },
  { path: '/segment', title: '玩家分群' },
  { path: '/funnel', title: '行为漏斗' },
  { path: '/churn', title: '流失预警' },
  { path: '/ltv', title: 'LTV预测' },
  { path: '/experiment', title: 'A/B实验' },
  { path: '/gacha', title: '付费与抽卡' },
  { path: '/feedback', title: '版本反馈' },
  { path: '/chat', title: 'LLM智能助手' },
  { path: '/data', title: '数据管理' },
]
const user = useUserStore(); const router = useRouter()
function onLogout() { user.logout(); router.push('/') }
</script>
