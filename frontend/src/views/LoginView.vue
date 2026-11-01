<template>
  <div style="display:flex;height:100vh;align-items:center;justify-content:center;background:#111827">
    <el-card style="width:360px">
      <h2 style="text-align:center;margin:8px 0 4px">二次元游戏玩家行为分析系统</h2>
      <p style="text-align:center;color:#6B7280;margin:0 0 16px">阶段1 骨架 · 登录验收页</p>
      <el-form @submit.prevent="onLogin">
        <el-form-item><el-input v-model="form.username" placeholder="用户名（admin）" /></el-form-item>
        <el-form-item><el-input v-model="form.password" type="password" placeholder="密码（admin123）" show-password /></el-form-item>
        <el-button type="primary" style="width:100%" :loading="loading" @click="onLogin">登录</el-button>
        <p v-if="err" style="color:#DC2626;text-align:center">{{ err }}</p>
      </el-form>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
const form = reactive({ username: 'admin', password: 'admin123' })
const loading = ref(false); const err = ref('')
const router = useRouter(); const user = useUserStore()
async function onLogin() {
  loading.value = true; err.value = ''
  try { await user.login(form.username, form.password); router.push('/dashboard') }
  catch { err.value = '登录失败：检查后端是否启动、账号密码是否正确' }
  finally { loading.value = false }
}
</script>
