<template>
  <div class="landing">
    <div class="orb orb-a"></div><div class="orb orb-b"></div><div class="orb orb-c"></div>

    <header class="nav glass-lite">
      <div class="logo">
        <svg viewBox="0 0 24 24" class="logo-mark"><path d="M12 2 L22 12 L12 22 L2 12 Z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg>
        <span>二次元游戏 · 玩家行为分析</span>
      </div>
      <nav class="nav-links">
        <a href="#features">能做什么</a><a href="#players">玩家的一天</a><a href="#features">智能问答</a>
      </nav>
      <div class="nav-actions">
        <template v-if="loggedIn">
          <button class="btn-solid" @click="router.push('/dashboard')">进入系统</button>
        </template>
        <template v-else>
          <button class="btn-ghost" @click="openAuth('password')">登录</button>
          <button class="btn-solid" @click="openAuth('register')">注册</button>
        </template>
      </div>
    </header>

    <main class="hero">
      <div class="hero-text">
        <p class="eyebrow">PLAYER ANALYTICS FOR ANIME GAMES</p>
        <h1>看懂玩家，<br/><span class="grad">读懂版本。</span></h1>
        <p class="hero-sub">谁在玩、玩得开不开心、为什么不玩了——<br/>这个系统帮你把这些问题，一次看清楚。</p>
        <div class="hero-cta">
          <button class="btn-solid big" @click="loggedIn ? router.push('/dashboard') : openAuth('password')">{{ loggedIn ? '进入系统' : '立即登录' }}</button>
          <button class="btn-ghost big" @click="openAuth('register')">注册账号</button>
        </div>
        <div class="hero-stats">
          <div><b>10</b><span>个页面，一站看全</span></div>
          <div><b>6</b><span>样本事，件件实用</span></div>
          <div><b>2</b><span>款游戏能接：原神 · 崩铁</span></div>
          <div><b>1</b><span>个助手，有事直接问</span></div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-frame glass-lite">
          <img src="/img/play-1.jpg" alt="玩家的游戏房间" />
        </div>
        <span class="chip chip-1 glass-lite">谁是氪金大佬，一眼分清</span>
        <span class="chip chip-2 glass-lite">新版本口碑，自动汇总</span>
        <span class="chip chip-3 glass-lite">抽卡花了多少，有本账</span>
      </div>
    </main>

    <section id="players" class="showcase">
      <p class="eyebrow center">PLAYERS · 玩家的一天</p>
      <h2 class="section-title">玩家真实的样子</h2>
      <div class="show-grid">
        <figure class="show-card glass-lite">
          <img src="/img/stage.jpg" alt="一起开黑的玩家" />
          <figcaption><b>一起玩，才热闹</b><span>组队、开黑、打联机——好不好玩，先看愿不愿意拉朋友。</span></figcaption>
        </figure>
        <figure class="show-card glass-lite">
          <img src="/img/play-2.jpg" alt="认真打游戏的手" />
          <figcaption><b>认真玩的人最较真</b><span>操作、数值、平衡性，他们比谁都敏感，也最愿意说真话。</span></figcaption>
        </figure>
        <figure class="show-card glass-lite">
          <img src="/img/play-3.jpg" alt="晚上的游戏房间" />
          <figcaption><b>每天晚上准时上线</b><span>下班下课后的两小时，是他们和游戏世界约好的时间。</span></figcaption>
        </figure>
      </div>
    </section>

    <section id="features" class="features">
      <p class="eyebrow center">FEATURES · 能做什么</p>
      <h2 class="section-title">不用懂术语，也能看懂玩家</h2>
      <div class="feature-grid">
        <div v-for="(f, i) in features" :key="f.title" :class="['feature-card', 'glass-lite', { wide: i === 0 }]">
          <svg viewBox="0 0 24 24" class="f-icon" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" v-html="f.icon"></svg>
          <h3>{{ f.title }}</h3><p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <footer class="foot">
      基于 Python + Vue 构建 · 数据可以是你自己的：游戏里导出的抽卡记录、玩家评论，都能接进来<br/>
      <span class="credits">主页照片来自 Unsplash 摄影师 Ella Don、Anthony Brolin、Axville（免费图库）</span>
    </footer>

    <div v-if="authOpen" class="auth-overlay" @click.self="authOpen = false">
      <AuthCard :initial-mode="authMode" @close="authOpen = false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AuthCard from '../components/AuthCard.vue'
const router = useRouter(); const route = useRoute()
const loggedIn = ref(!!localStorage.getItem('token'))
const authOpen = ref(false); const authMode = ref('password')
function openAuth(mode: string) { authMode.value = mode; authOpen.value = true }
onMounted(() => {
  const a = route.query.auth as string
  if (a === 'login') openAuth('password')
  else if (a === 'register') openAuth('register')
})
const P = {
  chart: '<path d="M4 20h16"/><path d="M7 20v-6"/><path d="M12 20V6"/><path d="M17 20v-9"/>',
  users: '<circle cx="9" cy="8" r="3.4"/><path d="M3.6 19c.6-2.9 2.7-4.4 5.4-4.4s4.8 1.5 5.4 4.4"/><circle cx="17.2" cy="9" r="2.6"/><path d="M16.2 14.6c2.2.3 3.7 1.7 4.2 4.4"/>',
  bell: '<path d="M6 16v-5a6 6 0 1 1 12 0v5l1.4 3H4.6L6 16Z"/><path d="M10 21a2.2 2.2 0 0 0 4 0"/>',
  gem: '<path d="M6.5 3.5h11L21 9l-9 11.5L3 9l3.5-5.5Z"/><path d="M3 9h18"/><path d="M9.5 3.5 8 9l4 11.5"/><path d="M14.5 3.5 16 9l-4 11.5"/>',
  chat: '<path d="M4 4.5h16V16H9.5L4 20.5v-16Z"/><path d="M8 9.5h8"/><path d="M8 13h5"/>',
  spark: '<path d="M12 3.5 13.8 8.7 19 10.5l-5.2 1.8L12 17.5l-1.8-5.2L5 10.5l5.2-1.8L12 3.5Z"/><path d="M18.8 16.2l.7 1.9 1.9.7-1.9.7-.7 1.9-.7-1.9-1.9-.7 1.9-.7.7-1.9Z"/>'
}
const features = [
  { icon: P.chart, title: '今天有多少人玩', desc: '每天来了多少人、留下来多少、花了多少钱，打开第一页就能看到，不用等报表。' },
  { icon: P.users, title: '给玩家分分类', desc: '氪金大佬、月卡党、肝帝、剧情党——把玩家分好组，才知道对谁说什么话。' },
  { icon: P.bell, title: '谁要走了，提前知道', desc: '有人快不玩了，系统会提前提醒你，还会说明他为什么想走、怎么留住他。' },
  { icon: P.gem, title: '抽卡和花钱，有本账', desc: '每个卡池卖了多少、平均多少抽出货、歪没歪，全都算得清清楚楚。' },
  { icon: P.chat, title: '新版本，大家怎么说', desc: '玩家评论自动归好类：夸剧情的、夸角色的、骂卡顿的、催福利的，一眼看完。' },
  { icon: P.spark, title: '有问题，直接问', desc: '不想翻报表？打字问一句就行。助手会先去查数据再回答，数字都有出处，不瞎编。' },
]
</script>

<style scoped>
.landing { position: relative; min-height: 100vh; overflow: hidden; color: #fff;
  background:
    radial-gradient(900px 600px at 15% 10%, rgba(124,58,237,.55), transparent 60%),
    radial-gradient(900px 650px at 85% 15%, rgba(37,99,235,.50), transparent 60%),
    radial-gradient(1000px 700px at 75% 90%, rgba(219,39,119,.45), transparent 60%),
    radial-gradient(700px 500px at 10% 85%, rgba(8,145,178,.45), transparent 60%),
    #0B1026;
  font-family: 'Plus Jakarta Sans', 'Noto Sans SC', system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.orb { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .55; animation: float 14s ease-in-out infinite; }
.orb-a { width: 340px; height: 340px; left: 6%; top: 22%; background: #7C3AED; }
.orb-b { width: 280px; height: 280px; right: 10%; top: 8%; background: #2563EB; animation-delay: -5s; }
.orb-c { width: 300px; height: 300px; right: 22%; bottom: -6%; background: #DB2777; animation-delay: -9s; }
@keyframes float { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-26px) } }
.glass-lite {
  /* 只改边框：柔光发丝线轮廓（澎湃 OS 式）——顶部微亮、向下收暗、下缘回光；卡面与内文不动 */
  border: 1px solid transparent;
  background:
    linear-gradient(145deg, rgba(255,255,255,.20), rgba(255,255,255,.08)) padding-box,
    linear-gradient(168deg, rgba(255,255,255,.34), rgba(255,255,255,.11) 36%, rgba(255,255,255,.03) 64%, rgba(255,255,255,.15)) border-box;
  -webkit-backdrop-filter: blur(26px) saturate(150%); backdrop-filter: blur(26px) saturate(150%);
  box-shadow: 0 14px 34px rgba(2,6,23,.18), inset 0 1px 0 rgba(255,255,255,.16), inset 0 -1px 0 rgba(255,255,255,.03);
}
.nav { position: relative; z-index: 5; margin: 18px auto 0; max-width: 1180px; border-radius: 24px;
  display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; }
.logo { display: flex; align-items: center; gap: 9px; font-weight: 800; font-size: 16px; letter-spacing: .04em; }
.logo-mark { width: 22px; height: 22px; }
.nav-links { display: flex; gap: 28px; }
.nav-links a { color: rgba(255,255,255,.86); text-decoration: none; font-size: 14.5px; font-weight: 500; }
.nav-actions { display: flex; gap: 10px; }
.btn-ghost { border: 1px solid rgba(255,255,255,.45); background: rgba(255,255,255,.12); color: #fff;
  padding: 9px 22px; border-radius: 999px; cursor: pointer; font-size: 14.5px; font-family: inherit; }
.btn-solid { border: none; color: #fff; padding: 9px 22px; border-radius: 999px; cursor: pointer; font-size: 14.5px; font-weight: 700; font-family: inherit;
  background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); box-shadow: 0 8px 20px rgba(59,90,246,.35), inset 0 1px 0 rgba(255,255,255,.5); }
.btn-solid.big, .btn-ghost.big { padding: 14px 36px; font-size: 16px; }
.eyebrow { font-size: 12px; font-weight: 700; letter-spacing: .32em; color: rgba(255,255,255,.66); margin: 0 0 18px; }
.eyebrow.center { text-align: center; }
.hero { position: relative; z-index: 4; max-width: 1180px; margin: 0 auto; padding: 84px 20px 26px;
  display: grid; grid-template-columns: 1.05fr .95fr; gap: 48px; align-items: center; }
.hero h1 { font-size: clamp(46px, 5.6vw, 74px); line-height: 1.14; margin: 0 0 20px; font-weight: 900; letter-spacing: .01em; text-shadow: 0 4px 30px rgba(2,6,23,.45); }
.grad { background: linear-gradient(90deg, #93C5FD, #C4B5FD, #F0ABFC); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-sub { font-size: 17.5px; line-height: 1.8; color: rgba(255,255,255,.88); margin: 0 0 32px; text-shadow: 0 2px 12px rgba(2,6,23,.4); }
.hero-cta { display: flex; gap: 14px; margin-bottom: 40px; }
.hero-stats { display: flex; gap: 34px; flex-wrap: wrap; }
.hero-stats div { display: flex; flex-direction: column; gap: 2px; }
.hero-stats b { font-size: 30px; font-weight: 800; line-height: 1; }
.hero-stats span { font-size: 12.5px; color: rgba(255,255,255,.72); }
.hero-visual { position: relative; }
.hero-frame { border-radius: 28px; padding: 10px; transform: rotate(1.2deg); }
.hero-frame img { display: block; width: 100%; height: 380px; object-fit: cover; border-radius: 20px; }
.chip { position: absolute; padding: 9px 16px; border-radius: 999px; font-size: 13px; font-weight: 500; white-space: nowrap; }
.chip-1 { top: 22px; left: -26px; transform: rotate(-2deg); }
.chip-2 { bottom: 64px; right: -18px; transform: rotate(1.6deg); }
.chip-3 { bottom: -14px; left: 34px; transform: rotate(-1deg); }
.showcase, .features { position: relative; z-index: 4; max-width: 1180px; margin: 74px auto 0; padding: 0 20px; }
.section-title { text-align: center; font-size: 34px; font-weight: 900; margin: 0 0 30px; letter-spacing: .01em; }
.show-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.show-card { margin: 0; border-radius: 26px; overflow: hidden; padding: 0; }
.show-card img { display: block; width: 100%; height: 215px; object-fit: cover; }
.show-card figcaption { padding: 16px 18px 18px; display: flex; flex-direction: column; gap: 5px; }
.show-card b { font-size: 16px; }
.show-card span { font-size: 13.5px; line-height: 1.6; color: rgba(255,255,255,.80); }
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.feature-card { border-radius: 26px; padding: 26px 24px; }
.feature-card.wide { grid-column: span 2; }
.feature-card h3 { margin: 12px 0 8px; font-size: 18px; font-weight: 700; }
.feature-card p { margin: 0; color: rgba(255,255,255,.82); font-size: 14px; line-height: 1.7; }
.f-icon { width: 30px; height: 30px; color: #C4B5FD; }
.foot { position: relative; z-index: 4; text-align: center; color: rgba(255,255,255,.60); font-size: 12.5px; line-height: 1.9; padding: 54px 20px 34px; }
.credits { color: rgba(255,255,255,.42); font-size: 12px; }
.auth-overlay { position: fixed; inset: 0; z-index: 50; display: flex; align-items: center; justify-content: center;
  background: rgba(6,8,20,.42); -webkit-backdrop-filter: blur(10px) saturate(140%); backdrop-filter: blur(10px) saturate(140%); }
@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; padding-top: 56px; }
  .show-grid, .feature-grid { grid-template-columns: 1fr; }
  .feature-card.wide { grid-column: span 1; }
  .nav-links { display: none; }
  .chip-1 { left: 4px; } .chip-2 { right: 4px; }
}
</style>
