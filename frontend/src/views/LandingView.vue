<template>
  <div class="landing">
    <div class="orb orb-a"></div><div class="orb orb-b"></div><div class="orb orb-c"></div>

    <header class="nav glass-lite">
      <div class="logo">
        <svg viewBox="0 0 24 24" class="logo-mark"><path d="M12 2 L22 12 L12 22 L2 12 Z" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg>
        <span>二次元游戏 · 玩家行为分析</span>
      </div>
      <nav class="nav-links">
        <a href="#features">能做什么</a><a href="#players">玩家的一程</a><a href="#features">智能问答</a>
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
        <h1>与玩家相逢，<br/><span class="grad">读懂这一程。</span></h1>
        <p class="hero-sub">初来乍到的新面孔、夜夜赴约的老朋友、悄然离站的身影——<br/>他们为何而来，为何停留，又为何离开。答案，都藏在这一程里。</p>
        <div class="hero-cta">
          <button class="btn-solid big" @click="loggedIn ? router.push('/dashboard') : openAuth('password')">{{ loggedIn ? '进入系统' : '立即登录' }}</button>
          <button class="btn-ghost big" @click="openAuth('register')">注册账号</button>
        </div>
        <div class="hero-stats">
          <div><b>10</b><span>个页面，一程看完</span></div>
          <div><b>6</b><span>个模块，各守一站</span></div>
          <div><b>2</b><span>款游戏能接：原神 · 崩铁</span></div>
          <div><b>1</b><span>个助手，随问随答</span></div>
        </div>
      </div>
      <div class="hero-visual">
        <div class="hero-frame glass-lite">
          <img src="/img/play-1.jpg" alt="玩家的游戏房间" />
        </div>
        <span class="chip chip-1 glass-lite">谁在为爱一掷千金</span>
        <span class="chip chip-2 glass-lite">新版本的心声，替你收好</span>
        <span class="chip chip-3 glass-lite">每一抽，都记在账上</span>
      </div>
    </main>

    <section id="players" class="showcase">
      <p class="eyebrow center">PLAYERS · 玩家的一程</p>
      <h2 class="section-title">旅途中的人们</h2>
      <div class="show-grid">
        <figure class="show-card glass-lite">
          <img src="/img/stage.jpg" alt="一起开黑的玩家" />
          <figcaption><b>愿同行的人，一直在身边</b><span>组队、开黑、攻坚。朋友还在，故事就不会落幕；朋友离开，往往也不是一个人离开。</span></figcaption>
        </figure>
        <figure class="show-card glass-lite">
          <img src="/img/play-2.jpg" alt="认真打游戏的手" />
          <figcaption><b>愿真心话，有处可说</b><span>数值、手感、平衡——他们在意的，比谁都多；想说的话，也比谁都真。新版本往哪走，先听听他们的。</span></figcaption>
        </figure>
        <figure class="show-card glass-lite">
          <img src="/img/play-3.jpg" alt="晚上的游戏房间" />
          <figcaption><b>愿每一晚，都有人赴约</b><span>放学、下班，屏幕一盏盏亮起。这是他们与这个世界定下的约定，日日如此，风雨无阻。</span></figcaption>
        </figure>
      </div>
    </section>

    <section id="features" class="features">
      <p class="eyebrow center">FEATURES · 沿途六站</p>
      <h2 class="section-title big">答案，都在这一程里</h2>
      <p class="section-summary">一段旅途，总要有人记录。谁在清晨抵达，谁在深夜离开；谁为心仪的角色攒了很久的原石，谁又在评论里留下长长的一段话。六个模块守在沿途的每一站，把这些都替你记下来——想看的时候，翻开便是。</p>
      <div class="feature-grid">
        <div v-for="f in modules" :key="f.title" class="feature-card glass-lite">
          <svg viewBox="0 0 24 24" class="f-icon" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" v-html="f.icon"></svg>
          <h3>{{ f.title }}</h3>
          <p class="f-desc">{{ f.desc }}</p>
          <ul class="f-points">
            <li v-for="pt in f.points" :key="pt">
              <svg viewBox="0 0 24 24" class="check" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9" stroke-opacity=".45"/><path d="M8.5 12.2 11 14.7 15.6 9.6"/></svg>
              <span>{{ pt }}</span>
            </li>
          </ul>
          <a class="f-entry" @click="openEntry(f.path)">进入{{ f.title }} <span class="arrow">→</span></a>
        </div>
      </div>
      <div class="summary-bar glass-lite">
        <b>写在最后</b><span>愿每一位玩家的来与去，都被认真记得。</span>
      </div>
    </section>

    <footer class="foot">
      数据可以是你自己的：游戏里导出的抽卡记录、留在评论区的心里话，都能在此安放。<br/>
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
const modules = [
  { icon: P.chart, path: '/dashboard', title: '总览看板', desc: '今日的世界，热闹依旧吗',
    points: ['今天有多少新面孔抵达', '老朋友回来了多少', '今天的流水有多少', '哪天最热闹，哪天最安静'] },
  { icon: P.users, path: '/segment', title: '玩家分群', desc: '众生百态，各有归处',
    points: ['一掷千金的大佬，名单在此', '月卡党、肝帝、剧情党，各有多少人', '每一组人，心头好各不相同', '哪一组人，最近来得少了'] },
  { icon: P.bell, path: '/churn', title: '流失预警', desc: '在离站之前，先留住他',
    points: ['谁的脚步，正在变慢', '他想离开的理由，写在数据里', '先留哪一批，最值得', '挽留之后，又回来了多少人'] },
  { icon: P.gem, path: '/gacha', title: '付费与抽卡', desc: '每一抽，都算数',
    points: ['哪个卡池，最受欢迎', '平均多少抽，迎来金光', '保底歪掉的次数，也记得清', '大佬们的心头好，是哪一位'] },
  { icon: P.chat, path: '/feedback', title: '版本反馈', desc: '这一程，风评如何',
    points: ['夸得最多的，是哪一处', '骂得最凶的，又是哪一处', '大家最盼着的更新是什么', '比起上一程，口碑回暖了吗'] },
  { icon: P.spark, path: '/chat', title: '智能助手', desc: '有事，问它便好',
    points: ['打字问一句，答案就来', '把新版本，总结成一段话', '某位玩家近况，随口可查', '句句有出处，不编造'] },
]
function openEntry(path: string) {
  if (localStorage.getItem('token')) { router.push(path); return }
  localStorage.setItem('post_login_redirect', path)
  openAuth('password')
}
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
  background: linear-gradient(145deg, rgba(255,255,255,.20), rgba(255,255,255,.08));
  -webkit-backdrop-filter: blur(20px) saturate(160%); backdrop-filter: blur(20px) saturate(160%);
  border: 1px solid rgba(255,255,255,.32);
  box-shadow: 0 12px 32px rgba(2,6,23,.28), inset 0 1px 0 rgba(255,255,255,.5);
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
.show-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.show-card { margin: 0; border-radius: 26px; overflow: hidden; padding: 0; }
.show-card img { display: block; width: 100%; height: 215px; object-fit: cover; }
.show-card figcaption { padding: 16px 18px 18px; display: flex; flex-direction: column; gap: 5px; }
.show-card b { font-size: 16px; }
.show-card span { font-size: 13.5px; line-height: 1.6; color: rgba(255,255,255,.80); }
.showcase, .features { position: relative; z-index: 4; max-width: 1180px; margin: 84px auto 0; padding: 0 20px; }
.section-title { text-align: center; font-size: 34px; font-weight: 900; margin: 0 0 30px; letter-spacing: .01em; }
.section-title.big { font-size: 40px; margin-bottom: 18px; }
.section-summary { max-width: 780px; margin: 0 auto 44px; text-align: center; font-size: 16px; line-height: 1.9; color: rgba(255,255,255,.86); }
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
.feature-card { border-radius: 26px; padding: 32px 30px 28px; display: flex; flex-direction: column; }
.feature-card h3 { margin: 14px 0 6px; font-size: 20px; font-weight: 800; }
.f-desc { margin: 0 0 18px; color: rgba(255,255,255,.88); font-size: 14.5px; }
.f-icon { width: 32px; height: 32px; color: #C4B5FD; }
.f-points { list-style: none; margin: 0 0 22px; padding: 16px 0 0; border-top: 1px solid rgba(255,255,255,.16); display: flex; flex-direction: column; gap: 11px; flex: 1; }
.f-points li { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; line-height: 1.55; color: rgba(255,255,255,.84); }
.f-points .check { flex: 0 0 17px; width: 17px; height: 17px; margin-top: 2px; color: #A5B4FC; }
.f-entry { font-size: 15px; font-weight: 700; color: #C7D2FE; cursor: pointer; }
.f-entry .arrow { display: inline-block; transition: transform .18s ease; }
.f-entry:hover .arrow { transform: translateX(4px); }
.f-entry:hover { text-decoration: underline; }
.summary-bar { margin-top: 22px; border-radius: 22px; padding: 20px 28px; display: flex; gap: 14px; align-items: baseline; justify-content: center; text-align: center; flex-wrap: wrap; }
.summary-bar b { font-size: 16px; color: #FDE68A; white-space: nowrap; }
.summary-bar span { font-size: 15px; color: rgba(255,255,255,.9); }
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
