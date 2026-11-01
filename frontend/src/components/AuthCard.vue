<template>
  <div class="glass-card">
    <button class="close-btn" @click="$emit('close')" aria-label="关闭">✕</button>

    <!-- 密码登录 -->
    <div v-if="mode === 'password'">
      <h2 class="card-title">欢迎回来</h2>
      <p class="card-sub">欢迎回来，今天也一起看看他们吧</p>
      <div class="field"><el-input v-model="form.username" placeholder="账号" size="large" class="glass-input" /></div>
      <div class="field"><el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password class="glass-input" @keyup.enter="onLogin" /></div>
      <button class="primary-btn" :disabled="loading" @click="onLogin">{{ loading ? '登录中…' : '登 录' }}</button>
      <div class="link-row">
        <a @click="mode = 'register'">注册账号</a>
        <a @click="mode = 'forgot'">找回密码</a>
      </div>
      <div class="divider"><span>或</span></div>
      <button class="ghost-btn" @click="mode = 'sms'">切换为短信登录</button>
    </div>

    <!-- 短信登录 -->
    <div v-else-if="mode === 'sms'">
      <h2 class="card-title">短信登录</h2>
      <p class="card-sub">未注册的手机号将自动创建账号</p>
      <div class="field"><el-input v-model="form.phone" placeholder="手机号" size="large" class="glass-input" /></div>
      <div class="field code-row">
        <el-input v-model="form.code" placeholder="验证码" size="large" class="glass-input" @keyup.enter="onSmsLogin" />
        <button class="code-btn" :disabled="countdown > 0" @click="sendCode">{{ countdown > 0 ? countdown + 's' : '获取验证码' }}</button>
      </div>
      <p v-if="demoCode" class="demo-hint">演示环境验证码统一为 123456（正式环境将通过短信发送）</p>
      <button class="primary-btn" :disabled="loading" @click="onSmsLogin">{{ loading ? '登录中…' : '登 录' }}</button>
      <div class="link-row"><a @click="mode = 'register'">注册账号</a><a @click="mode = 'forgot'">找回密码</a></div>
      <div class="divider"><span>或</span></div>
      <button class="ghost-btn" @click="mode = 'password'">切换为密码登录</button>
    </div>

    <!-- 注册 -->
    <div v-else-if="mode === 'register'">
      <h2 class="card-title">注册账号</h2>
      <p class="card-sub">注册完成，即刻启程</p>
      <div class="field"><el-input v-model="form.username" placeholder="账号" size="large" class="glass-input" /></div>
      <div class="field"><el-input v-model="form.phone" placeholder="手机号" size="large" class="glass-input" /></div>
      <div class="field code-row">
        <el-input v-model="form.code" placeholder="短信验证码" size="large" class="glass-input" />
        <button class="code-btn" :disabled="countdown > 0" @click="sendCode">{{ countdown > 0 ? countdown + 's' : '获取验证码' }}</button>
      </div>
      <p v-if="demoCode" class="demo-hint">演示环境验证码统一为 123456</p>
      <div class="field"><el-input v-model="form.password" type="password" placeholder="设置密码" size="large" show-password class="glass-input" @keyup.enter="onRegister" /></div>
      <button class="primary-btn" :disabled="loading" @click="onRegister">{{ loading ? '注册中…' : '注册并登录' }}</button>
      <div class="link-row center"><a @click="mode = 'password'">已有账号，去登录</a></div>
    </div>

    <!-- 找回密码 -->
    <div v-else>
      <h2 class="card-title">找回密码</h2>
      <p class="card-sub">通过手机验证码重置密码</p>
      <div class="field"><el-input v-model="form.username" placeholder="账号" size="large" class="glass-input" /></div>
      <div class="field"><el-input v-model="form.phone" placeholder="手机号" size="large" class="glass-input" /></div>
      <div class="field code-row">
        <el-input v-model="form.code" placeholder="验证码" size="large" class="glass-input" />
        <button class="code-btn" :disabled="countdown > 0" @click="sendCode">{{ countdown > 0 ? countdown + 's' : '获取验证码' }}</button>
      </div>
      <p v-if="demoCode" class="demo-hint">演示环境验证码统一为 123456</p>
      <div class="field"><el-input v-model="form.newPassword" type="password" placeholder="新密码" size="large" show-password class="glass-input" @keyup.enter="onReset" /></div>
      <button class="primary-btn" :disabled="loading" @click="onReset">{{ loading ? '提交中…' : '重置密码' }}</button>
      <div class="link-row center"><a @click="mode = 'password'">返回登录</a></div>
    </div>

    <p v-if="err" class="err">{{ err }}</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import request from '../api/request'

const props = defineProps<{ initialMode: string }>()
defineEmits(['close'])
const mode = ref(props.initialMode || 'password')
watch(() => props.initialMode, v => { mode.value = v || 'password' })

const form = reactive({ username: 'admin', password: 'admin123', phone: '', code: '', newPassword: '' })
const loading = ref(false); const err = ref(''); const demoCode = ref(''); const countdown = ref(0)
let timer: any = null
const router = useRouter(); const user = useUserStore()

function startCountdown() {
  countdown.value = 60
  timer = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(timer) }, 1000)
}
onUnmounted(() => { if (timer) clearInterval(timer) })

async function sendCode() {
  err.value = ''
  if (!form.phone) { err.value = '请先填写手机号'; return }
  try {
    const { data } = await request.post('/auth/sms/send', { phone: form.phone })
    if (data.demo_code) demoCode.value = data.demo_code
    startCountdown()
  } catch (e: any) { err.value = e.response?.data?.detail || '验证码发送失败' }
}
function goAfterLogin() {
  const r = localStorage.getItem('post_login_redirect')
  localStorage.removeItem('post_login_redirect')
  router.push(r || '/dashboard')
}
async function onLogin() {
  loading.value = true; err.value = ''
  try { await user.login(form.username, form.password); goAfterLogin() }
  catch (e: any) { err.value = e.response?.data?.detail || '登录失败' }
  finally { loading.value = false }
}
async function onSmsLogin() {
  loading.value = true; err.value = ''
  try { await user.smsLogin(form.phone, form.code); goAfterLogin() }
  catch (e: any) { err.value = e.response?.data?.detail || '登录失败' }
  finally { loading.value = false }
}
async function onRegister() {
  loading.value = true; err.value = ''
  try { await user.register(form.username, form.password, form.phone, form.code); goAfterLogin() }
  catch (e: any) { err.value = e.response?.data?.detail || '注册失败' }
  finally { loading.value = false }
}
async function onReset() {
  loading.value = true; err.value = ''
  try {
    await request.post('/auth/password/reset', { username: form.username, phone: form.phone, code: form.code, new_password: form.newPassword })
    mode.value = 'password'; err.value = ''; demoCode.value = ''
    form.password = ''
    alert('密码已重置，请用新密码登录')
  } catch (e: any) { err.value = e.response?.data?.detail || '重置失败' }
  finally { loading.value = false }
}
</script>

<style scoped>
.glass-card::after {
  content: ''; position: absolute; inset: 0; border-radius: inherit; padding: 1px; pointer-events: none;
  background: linear-gradient(165deg, rgba(255,255,255,.38), rgba(255,255,255,.12) 34%, rgba(255,255,255,.03) 60%, rgba(255,255,255,.18));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
}
.glass-card {
  position: relative; width: 400px; max-width: calc(100vw - 40px);
  padding: 36px 34px 30px;
  border-radius: 32px;                       /* iOS 26 式大圆角 */
  background: linear-gradient(145deg, rgba(255,255,255,.28), rgba(255,255,255,.12) 55%, rgba(255,255,255,.20));
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  backdrop-filter: blur(28px) saturate(180%);
  border: 1px solid rgba(255,255,255,.45);
  box-shadow: 0 24px 54px rgba(2,6,23,.38), inset 0 1px 0 rgba(255,255,255,.30), inset 0 -1px 0 rgba(255,255,255,.08);
  color: #fff; animation: pop .28s cubic-bezier(.2,.9,.3,1.2);
}
@keyframes pop { from { transform: scale(.94) translateY(10px); opacity: 0 } to { transform: scale(1) translateY(0); opacity: 1 } }
.close-btn {
  position: absolute; top: 14px; right: 14px; width: 32px; height: 32px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,.4); background: rgba(255,255,255,.15); color: #fff; cursor: pointer; font-size: 13px;
}
.card-title { margin: 0 0 6px; font-size: 26px; font-weight: 700; text-shadow: 0 1px 8px rgba(2,6,23,.35); }
.card-sub { margin: 0 0 22px; color: rgba(255,255,255,.82); font-size: 13.5px; text-shadow: 0 1px 6px rgba(2,6,23,.3); }
.field { margin-bottom: 14px; }
.glass-input :deep(.el-input__wrapper) {
  background: rgba(255,255,255,.16); border-radius: 18px;
  box-shadow: 0 0 0 1px rgba(255,255,255,.38) inset, inset 0 1px 0 rgba(255,255,255,.35);
  padding: 4px 14px;
}
.glass-input :deep(.el-input__inner) { color: #fff; font-size: 15px; }
.glass-input :deep(.el-input__inner::placeholder) { color: rgba(255,255,255,.60); }
.glass-input :deep(.el-input__suffix) { color: rgba(255,255,255,.8); }
.primary-btn {
  width: 100%; height: 50px; margin-top: 4px; border: none; border-radius: 25px; cursor: pointer;
  background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9);
  color: #fff; font-size: 16.5px; font-weight: 700; letter-spacing: 2px;
  box-shadow: 0 10px 24px rgba(59,90,246,.40), inset 0 1px 0 rgba(255,255,255,.55);
}
.primary-btn { transition: transform .18s cubic-bezier(.34,1.56,.64,1), filter .18s ease; }
.primary-btn:active { transform: scale(.965); filter: brightness(1.13); }
.primary-btn:disabled { opacity: .65; cursor: wait; }
.ghost-btn { transition: transform .18s cubic-bezier(.34,1.56,.64,1), filter .18s ease; }
.ghost-btn:active { transform: scale(.965); filter: brightness(1.13); }
.ghost-btn {
  width: 100%; height: 46px; border-radius: 23px; cursor: pointer;
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.38); color: #fff; font-size: 14.5px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.4);
}
.link-row { display: flex; justify-content: space-between; margin-top: 16px; }
.link-row.center { justify-content: center; }
.link-row a { color: rgba(255,255,255,.92); font-size: 13.5px; cursor: pointer; text-shadow: 0 1px 4px rgba(2,6,23,.3); }
.link-row a:hover { text-decoration: underline; }
.divider { display: flex; align-items: center; gap: 12px; margin: 20px 0 14px; color: rgba(255,255,255,.75); font-size: 12.5px; }
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,.35); }
.code-row { display: flex; gap: 10px; }
.code-row .el-input { flex: 1; }
.code-btn {
  flex: 0 0 118px; border-radius: 18px; border: 1px solid rgba(255,255,255,.38);
  background: rgba(255,255,255,.18); color: #fff; cursor: pointer; font-size: 13.5px;
}
.code-btn:disabled { opacity: .55; cursor: not-allowed; }
.demo-hint { margin: -4px 0 12px; font-size: 12.5px; color: #FDE68A; text-shadow: 0 1px 4px rgba(2,6,23,.4); }
.err { margin: 14px 0 0; text-align: center; color: #FECACA; font-size: 13.5px; text-shadow: 0 1px 4px rgba(2,6,23,.45); }
</style>
