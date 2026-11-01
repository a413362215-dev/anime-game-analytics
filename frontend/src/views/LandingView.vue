<template>
  <div class="landing">
    <div class="orb orb-a"></div><div class="orb orb-b"></div><div class="orb orb-c"></div>

    <header class="nav glass-lite">
      <div class="logo">◈ 二次元游戏玩家行为分析</div>
      <nav class="nav-links">
        <a href="#features">功能模块</a><a href="#features">数据接入</a><a href="#features">LLM 助手</a>
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
      <h1>看懂玩家，<span class="grad">读懂版本</span></h1>
      <p class="hero-sub">玩家行为分析 × 版本反馈分析 × LLM 智能助手<br/>为二次元游戏运营而生的数据分析系统</p>
      <div class="hero-cta">
        <button class="btn-solid big" @click="loggedIn ? router.push('/dashboard') : openAuth('password')">{{ loggedIn ? '进入系统' : '立即登录' }}</button>
        <button class="btn-ghost big" @click="openAuth('register')">注册账号</button>
      </div>
      <div class="stat-strip glass-lite">
        <div><b>10</b><span>功能页面</span></div>
        <div><b>30</b><span>数据表设计</span></div>
        <div><b>3</b><span>LTV 模型</span></div>
        <div><b>完整版</b><span>A/B 实验框架</span></div>
        <div><b>原神·崩铁</b><span>数据可接入</span></div>
      </div>
    </main>

    <section id="features" class="features">
      <div v-for="f in features" :key="f.title" class="feature-card glass-lite">
        <div class="f-icon">{{ f.icon }}</div>
        <h3>{{ f.title }}</h3><p>{{ f.desc }}</p>
      </div>
    </section>

    <footer class="foot">基于 Python + Vue 构建 · 数据来源：模拟数据与玩家授权导入（UIGF / Enka / HoYoLAB）</footer>

    <!-- 登录/注册悬浮层：点主页按钮才出现，居中液态玻璃卡片 -->
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
const features = [
  { icon: '📊', title: '玩家行为分析', desc: 'DAU、留存 Cohort、行为漏斗，一眼看清玩家在哪流失' },
  { icon: '👥', title: '玩家分群', desc: 'RFM 五分位 + K-Means，大R、肝帝、剧情党各归其类' },
  { icon: '⚠️', title: '流失预警', desc: 'XGBoost 预测 + SHAP 解释，告诉你每个玩家为什么要走' },
  { icon: '💎', title: 'LTV 与抽卡', desc: 'Cox / XGBoost / BG-NBD 三模型算价值，卡池保底歪率全量化' },
  { icon: '💬', title: '版本反馈', desc: 'BERT 情感 + 六方面评价 + 话题挖掘，新版本口碑一目了然' },
  { icon: '🤖', title: 'LLM 智能助手', desc: '自然语言查数、知识库问答、自动生成版本复盘报告' },
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
  font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
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
.logo { font-weight: 800; font-size: 16.5px; letter-spacing: .5px; }
.nav-links { display: flex; gap: 26px; }
.nav-links a { color: rgba(255,255,255,.85); text-decoration: none; font-size: 14.5px; }
.nav-actions { display: flex; gap: 10px; }
.btn-ghost { border: 1px solid rgba(255,255,255,.45); background: rgba(255,255,255,.12); color: #fff;
  padding: 9px 22px; border-radius: 999px; cursor: pointer; font-size: 14.5px; }
.btn-solid { border: none; color: #fff; padding: 9px 22px; border-radius: 999px; cursor: pointer; font-size: 14.5px; font-weight: 700;
  background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); box-shadow: 0 8px 20px rgba(59,90,246,.35), inset 0 1px 0 rgba(255,255,255,.5); }
.btn-solid.big, .btn-ghost.big { padding: 13px 34px; font-size: 16px; }
.hero { position: relative; z-index: 4; text-align: center; padding: 92px 20px 30px; }
.hero h1 { font-size: 56px; margin: 0 0 18px; font-weight: 800; letter-spacing: 1px; text-shadow: 0 4px 30px rgba(2,6,23,.45); }
.grad { background: linear-gradient(90deg, #93C5FD, #C4B5FD, #F0ABFC); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-sub { font-size: 18px; line-height: 1.75; color: rgba(255,255,255,.88); margin: 0 0 34px; text-shadow: 0 2px 12px rgba(2,6,23,.4); }
.hero-cta { display: flex; gap: 14px; justify-content: center; margin-bottom: 44px; }
.stat-strip { max-width: 860px; margin: 0 auto; border-radius: 24px; display: flex; justify-content: space-around; padding: 18px 10px; }
.stat-strip div { display: flex; flex-direction: column; gap: 3px; }
.stat-strip b { font-size: 19px; }
.stat-strip span { font-size: 12.5px; color: rgba(255,255,255,.78); }
.features { position: relative; z-index: 4; max-width: 1180px; margin: 56px auto 0; padding: 0 20px;
  display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; }
.feature-card { border-radius: 26px; padding: 24px 22px; }
.feature-card h3 { margin: 10px 0 8px; font-size: 17.5px; }
.feature-card p { margin: 0; color: rgba(255,255,255,.82); font-size: 14px; line-height: 1.65; }
.f-icon { font-size: 26px; }
.foot { position: relative; z-index: 4; text-align: center; color: rgba(255,255,255,.55); font-size: 12.5px; padding: 44px 0 30px; }
.auth-overlay { position: fixed; inset: 0; z-index: 50; display: flex; align-items: center; justify-content: center;
  background: rgba(6,8,20,.42); -webkit-backdrop-filter: blur(10px) saturate(140%); backdrop-filter: blur(10px) saturate(140%); }
@media (max-width: 720px) { .nav-links { display: none } .hero h1 { font-size: 38px } }
</style>
