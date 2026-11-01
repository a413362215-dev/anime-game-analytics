<template>
  <div class="app-shell">
    <header class="float-nav app-nav">
      <RouterLink to="/dashboard" class="brand">
        <svg viewBox="0 0 24 24" class="brand-mark" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3 21 12 12 21 3 12Z"/><path d="M12 8 16 12 12 16 8 12Z"/></svg>
        <span class="brand-name">玩家行为分析</span>
      </RouterLink>
      <nav class="icons">
        <RouterLink v-for="p in pages" :key="p.path" :to="p.path" class="ni" active-class="on" :title="p.title">
          <svg viewBox="0 0 24 24" class="ni-icon" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" v-html="p.icon"></svg>
          <span class="ni-label">{{ p.title }}</span>
        </RouterLink>
      </nav>
      <div class="nav-right">
        <span class="demo-badge">演示数据</span>
        <div class="game-switch">
          <button :class="{ on: game === 'gi' }" @click="game = 'gi'">原神</button>
          <button :class="{ on: game === 'hsr' }" @click="game = 'hsr'">崩铁</button>
        </div>
        <span class="avatar" :title="user.username + '（' + (user.role === 'admin' ? '管理员' : '分析师') + '）'">{{ (user.username || 'A').slice(0, 1).toUpperCase() }}</span>
        <button class="icon-btn" title="退出登录" @click="onLogout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3"/><path d="M16 17l5-5-5-5M21 12H9"/></svg>
        </button>
      </div>
    </header>
    <div class="meta-row">
      <span>主页 <i>/</i> {{ $route.meta.title }}</span>
      <span>2026 年 11 月 1 日 · 版本 5.2</span>
    </div>
    <main class="content"><router-view /></main>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
const I = {
  chart: '<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/>',
  users: '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c.6-3 2.8-4.5 5.5-4.5S13.9 16 14.5 19"/><circle cx="17" cy="9" r="2.6"/><path d="M15.5 14.6c2.3.1 4.2 1.5 4.8 4.4"/>',
  funnel: '<path d="M4 4h16l-6.2 7.2V19l-3.6 2v-9.8L4 4Z"/>',
  bell: '<path d="M6 16v-5a6 6 0 1 1 12 0v5l1.2 2.4a.6.6 0 0 1-.5.9H5.3a.6.6 0 0 1-.5-.9L6 16Z"/><path d="M10 21a2.2 2.2 0 0 0 4 0"/>',
  trend: '<path d="M3 17.5 8.5 11l3.5 3L18.5 6"/><path d="M14.8 6h3.7v3.7"/>',
  flask: '<path d="M10 3h4M11 3v5.2L5.6 17a2.4 2.4 0 0 0 2.1 3.6h8.6a2.4 2.4 0 0 0 2.1-3.6L13 8.2V3"/><path d="M8 14.5h8"/>',
  gem: '<path d="M7 4h10l3.5 5L12 20 3.5 9 7 4Z"/><path d="M3.5 9h17M12 20 9 9l1.8-5M12 20 15 9l-1.8-5"/>',
  chat: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v7a2.5 2.5 0 0 1-2.5 2.5H12l-4.5 4v-4H6.5A2.5 2.5 0 0 1 4 12.5v-7Z"/><path d="M8 8.5h8M8 11.5h5"/>',
  spark: '<path d="M12 3.5 13.8 10 20.5 12 13.8 14 12 20.5 10.2 14 3.5 12 10.2 10 12 3.5Z"/><path d="M19 3.8v3M17.5 5.3h3"/>',
  db: '<ellipse cx="12" cy="5.5" rx="7" ry="2.8"/><path d="M5 5.5v13c0 1.6 3.1 2.9 7 2.9s7-1.3 7-2.9v-13"/><path d="M5 12c0 1.6 3.1 2.9 7 2.9s7-1.3 7-2.9"/>',
}
const pages = [
  { path: '/dashboard', title: '总览看板', icon: I.chart },
  { path: '/segment', title: '玩家分群', icon: I.users },
  { path: '/funnel', title: '行为漏斗', icon: I.funnel },
  { path: '/churn', title: '流失预警', icon: I.bell },
  { path: '/ltv', title: 'LTV预测', icon: I.trend },
  { path: '/experiment', title: 'A/B实验', icon: I.flask },
  { path: '/gacha', title: '付费与抽卡', icon: I.gem },
  { path: '/feedback', title: '版本反馈', icon: I.chat },
  { path: '/chat', title: 'LLM智能助手', icon: I.spark },
  { path: '/data', title: '数据管理', icon: I.db },
]
const user = useUserStore(); const router = useRouter()
const game = ref('gi')
function onLogout() { user.logout(); router.push('/') }
</script>
<style scoped>
.app-nav { display: flex; align-items: center; gap: 14px; width: min(1440px, calc(100% - 36px)); margin: 13px auto 0; padding: 8px 10px 8px 18px; }
.brand { display: flex; align-items: center; gap: 9px; color: #fff; text-decoration: none; flex: 0 0 auto; }
.brand-mark { width: 24px; height: 24px; color: #A5B4FC; }
.brand-name { font-size: 14.5px; font-weight: 800; letter-spacing: .03em; white-space: nowrap; }
.icons { display: flex; align-items: center; gap: 2px; margin: 0 auto; }
.ni { display: flex; align-items: center; border-radius: 999px; padding: 9px 10px; color: rgba(238,240,255,.78); text-decoration: none;
  transition: background .25s ease, color .25s ease, box-shadow .25s ease; }
.ni-icon { width: 20px; height: 20px; flex: 0 0 20px; transition: transform .3s cubic-bezier(.34,1.45,.64,1); }
.ni-label { max-width: 0; opacity: 0; overflow: hidden; white-space: nowrap; font-size: 13.5px; font-weight: 600;
  transition: max-width .34s cubic-bezier(.34,1.3,.64,1), opacity .22s ease, margin .34s cubic-bezier(.34,1.3,.64,1); }
.ni:hover { background: rgba(255,255,255,.1); color: #fff; }
.ni:hover .ni-icon, .ni.on .ni-icon { transform: scale(1.14); }
.ni:hover .ni-label, .ni.on .ni-label { max-width: 96px; opacity: 1; margin-left: 8px; }
.ni.on { background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); color: #fff;
  box-shadow: 0 8px 20px rgba(99,102,241,.4), inset 0 1px 0 rgba(255,255,255,.45); }
.nav-right { display: flex; align-items: center; gap: 11px; flex: 0 0 auto; }
.game-switch { display: flex; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.13); border-radius: 999px; padding: 3px; }
.game-switch button { border: none; background: transparent; color: rgba(238,240,255,.7); font-family: inherit; font-size: 12.5px; font-weight: 600;
  padding: 5px 13px; border-radius: 999px; cursor: pointer; transition: all .22s ease; }
.game-switch button.on { background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); color: #fff; }
.avatar { width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center; font-weight: 800; font-size: 13.5px; color: #fff;
  background: linear-gradient(135deg, #60A5FA, #E879F9); cursor: default; }
.icon-btn { width: 34px; height: 34px; border-radius: 50%; border: 1px solid rgba(255,255,255,.3); background: rgba(255,255,255,.08);
  color: #fff; cursor: pointer; display: grid; place-items: center; transition: all .25s ease; }
.icon-btn svg { width: 17px; height: 17px; }
.icon-btn:hover { background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); border-color: transparent; }
.meta-row { display: flex; justify-content: space-between; width: min(1440px, calc(100% - 36px)); margin: 13px auto 0; padding: 0 8px;
  font-size: 12.5px; color: rgba(238,240,255,.5); }
.meta-row i { font-style: normal; margin: 0 6px; opacity: .6; }
.content { padding: 10px 28px 34px; max-width: 1460px; width: 100%; margin: 0 auto; }
@media (max-width: 1180px) { .brand-name, .demo-badge { display: none; } }
@media (max-width: 860px) { .game-switch, .meta-row { display: none; } .icons { overflow-x: auto; } }
</style>
