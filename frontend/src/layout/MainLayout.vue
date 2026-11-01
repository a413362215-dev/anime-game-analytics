<template>
  <div class="app-shell shell">
    <aside class="side panel-flat">
      <div class="brand">
        <svg viewBox="0 0 24 24" class="brand-mark" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3 21 12 12 21 3 12Z"/><path d="M12 8 16 12 12 16 8 12Z"/></svg>
        <div><b>二次元游戏</b><span>玩家行为分析</span></div>
      </div>
      <nav class="menu">
        <RouterLink v-for="p in pages" :key="p.path" :to="p.path" class="mi" active-class="on">
          <svg viewBox="0 0 24 24" class="mi-icon" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" v-html="p.icon"></svg>
          <span>{{ p.title }}</span>
        </RouterLink>
      </nav>
      <div class="side-foot">
        <div class="user-chip"><span class="avatar">{{ (user.username || 'A').slice(0, 1).toUpperCase() }}</span>
          <div class="u-meta"><b>{{ user.username }}</b><span>{{ user.role === 'admin' ? '管理员' : '分析师' }}</span></div>
        </div>
        <button class="btn-g logout" @click="onLogout">退出登录</button>
      </div>
    </aside>
    <div class="main">
      <header class="topbar">
        <div class="crumb">主页 <i>/</i> {{ $route.meta.title }}</div>
        <div class="top-right">
          <span class="demo-badge">演示数据</span>
          <div class="game-switch">
            <button :class="{ on: game === 'gi' }" @click="game = 'gi'">原神</button>
            <button :class="{ on: game === 'hsr' }" @click="game = 'hsr'">星穹铁道</button>
          </div>
          <span class="today">2026 年 11 月 1 日 · 版本 5.2</span>
        </div>
      </header>
      <main class="content"><router-view /></main>
    </div>
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
.shell { display: flex; min-height: 100vh; }
.side { width: 228px; flex: 0 0 228px; position: sticky; top: 0; height: 100vh; display: flex; flex-direction: column;
  padding: 22px 16px 18px; background: linear-gradient(170deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
  border-right: 1px solid rgba(255,255,255,.12); -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px); }
.brand { display: flex; gap: 11px; align-items: center; padding: 2px 8px 20px; }
.brand-mark { width: 30px; height: 30px; color: #A5B4FC; flex: 0 0 30px; }
.brand b { display: block; font-size: 16.5px; font-weight: 800; letter-spacing: .02em; }
.brand span { display: block; font-size: 12px; color: rgba(238,240,255,.55); margin-top: 2px; }
.menu { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.mi { display: flex; align-items: center; gap: 11px; padding: 10.5px 13px; border-radius: 13px; color: rgba(238,240,255,.78);
  text-decoration: none; font-size: 14.5px; font-weight: 500; transition: all .22s ease; }
.mi-icon { width: 19px; height: 19px; flex: 0 0 19px; opacity: .85; }
.mi:hover { background: rgba(255,255,255,.07); color: #fff; }
.mi.on { background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); color: #fff; font-weight: 700;
  box-shadow: 0 8px 20px rgba(99,102,241,.35), inset 0 1px 0 rgba(255,255,255,.45); }
.mi.on .mi-icon { opacity: 1; }
.side-foot { border-top: 1px solid rgba(255,255,255,.1); padding-top: 15px; display: flex; flex-direction: column; gap: 12px; }
.user-chip { display: flex; align-items: center; gap: 10px; padding: 0 6px; }
.avatar { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; font-weight: 800; font-size: 14px; color: #fff;
  background: linear-gradient(135deg, #60A5FA, #E879F9); }
.u-meta b { display: block; font-size: 13.5px; } .u-meta span { font-size: 11.5px; color: rgba(238,240,255,.55); }
.logout { width: 100%; }
.main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 28px 4px; }
.crumb { font-size: 13px; color: rgba(238,240,255,.55); } .crumb i { font-style: normal; margin: 0 6px; opacity: .6; }
.top-right { display: flex; align-items: center; gap: 14px; }
.game-switch { display: flex; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.13); border-radius: 999px; padding: 3px; }
.game-switch button { border: none; background: transparent; color: rgba(238,240,255,.7); font-family: inherit; font-size: 12.5px; font-weight: 600;
  padding: 5px 14px; border-radius: 999px; cursor: pointer; transition: all .22s ease; }
.game-switch button.on { background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); color: #fff; }
.today { font-size: 12.5px; color: rgba(238,240,255,.55); }
.content { padding: 14px 28px 34px; max-width: 1460px; width: 100%; margin: 0 auto; }
</style>
