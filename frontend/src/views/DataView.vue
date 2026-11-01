<template>
  <div class="page-head"><h1 class="page-title">数据管理</h1><p class="page-sub">数据从哪来，由你决定——游戏里导出的、社区里说的，都能在此安放。</p></div>
  <p v-if="msg" class="import-msg">{{ msg }}</p>
  <div class="grid" style="grid-template-columns: repeat(3, 1fr)">
    <div class="panel src" v-for="s in sources" :key="s.code">
      <div class="seg-top"><h3>{{ s.name }}</h3><span class="badge" :class="statusCls(s.status)">{{ statusLabel(s.status) }}</span></div>
      <p class="src-desc">{{ s.description }}</p>
      <div class="src-meta"><span>最近同步 · {{ s.last_sync_at }}</span><span>累计 {{ fmt(s.total_rows) }} 条</span></div>
      <button class="btn-g" style="width: 100%" @click="onAction(s)">{{ actionLabel(s) }}</button>
    </div>
  </div>
  <input ref="fileInput" type="file" accept=".json,application/json" style="display: none" @change="onFile" />
  <div class="grid" style="grid-template-columns: 1.5fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">同步任务</h3><span class="p-sub">重复导入不会重复入库（按 external_id 去重）</span></div>
      <table class="tbl"><thead><tr><th>任务</th><th>来源</th><th>导入</th><th>跳过重复</th><th>状态</th></tr></thead>
      <tbody><tr v-for="j in jobs" :key="j.title + j.time"><td><b>{{ j.title }}</b><span class="uid">{{ j.time }}</span></td><td>{{ j.source }}</td><td>{{ fmt(j.added) }}</td><td>{{ fmt(j.skipped) }}</td>
        <td><span class="badge" :class="j.status === 'success' ? 'b-green' : j.status === 'partial' ? 'b-amber' : 'b-red'">{{ j.status === 'success' ? '成功' : j.status === 'partial' ? '部分成功' : '失败' }}</span></td></tr></tbody></table></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">字段映射 · UIGF 示例</h3><span class="p-sub">外部字段 → 标准字段</span></div>
      <table class="tbl"><thead><tr><th>UIGF 字段</th><th>标准表字段</th></tr></thead>
      <tbody><tr v-for="m in maps" :key="m.a"><td><code>{{ m.a }}</code></td><td><code>{{ m.b }}</code></td></tr></tbody></table>
      <p class="safe">安全约定：authkey 约 1 天有效，只做一次性导入；凭证加密存储、不打日志、不用作其他用途。读不到全服大盘数据——那是发行方内网的事，这里不假装能读。</p></div>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import request from '../api/request'
import { fmt } from '../mock/data'

const sources = ref<any[]>([])
const jobs = ref<any[]>([])
const msg = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const pendingGame = ref<'gi' | 'hsr'>('gi')

const statusLabel = (s: string) => ({ ready: '可导入', connected: '已连接', pending: '待配置' } as any)[s] || s
const statusCls = (s: string) => ({ ready: 'b-green', connected: 'b-blue', pending: 'b-gray' } as any)[s] || 'b-gray'
const actionLabel = (s: any) => ({
  uigf: '导入 UIGF 文件', srgf: '导入 SRGF 文件', enka: '按 UID 同步', hoyolab: '立即同步',
  feedback_csv: '导入 CSV / Excel', custom: '新建适配器', simulator: '重新生成模拟数据',
} as any)[s.code] || '打开'

async function load() {
  try {
    const [a, b] = await Promise.all([request.get('/data/sources'), request.get('/data/tasks')])
    sources.value = a.data; jobs.value = b.data
  } catch { msg.value = '后端未连接：数据源列表读不到，请先启动后端服务。' }
}
onMounted(load)

function onAction(s: any) {
  if (s.code === 'uigf' || s.code === 'srgf') {
    pendingGame.value = s.code === 'uigf' ? 'gi' : 'hsr'
    fileInput.value?.click()
  } else if (s.code === 'feedback_csv') {
    msg.value = '评论 CSV 导入会在版本反馈阶段（阶段 8）接通；现在库里的反馈来自模拟生成器。'
  } else if (s.code === 'simulator') {
    msg.value = '模拟数据在后端启动时自动生成（已有数据时跳过）；想重看生成过程，删掉后端 dev.db 再重启即可。'
  } else {
    msg.value = `「${s.name}」会在后续阶段接通，当前先用导入与模拟数据跑通全链路。`
  }
}

async function onFile(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (!f) return
  const fd = new FormData(); fd.append('file', f); fd.append('game', pendingGame.value)
  msg.value = '正在导入…'
  try {
    const { data } = await request.post('/ingest/gacha', fd)
    msg.value = data.error || `导入完成：新增 ${data.added} 条，跳过重复 ${data.skipped} 条（文件共 ${data.total_in_file} 条）。再导一次同一文件，新增会是 0。`
    await load()
  } catch { msg.value = '导入失败：后端没有响应。' }
  (e.target as HTMLInputElement).value = ''
}

const maps = [
  { a: 'uid', b: 'player.external_uid' }, { a: 'item_id', b: 'gacha_log.item_id' },
  { a: 'gacha_type', b: 'gacha_log.banner_type' }, { a: 'time', b: 'gacha_log.pulled_at' },
  { a: 'id（祈愿记录）', b: 'gacha_log.external_id' },
]
</script>
<style scoped>
.src-desc { font-size: 13px; color: rgba(238,240,255,.6); line-height: 1.65; min-height: 42px; }
.src-meta { display: flex; justify-content: space-between; font-size: 12px; color: rgba(238,240,255,.45); margin: 12px 0 14px; }
.safe { font-size: 12px; line-height: 1.7; color: rgba(238,240,255,.5); margin-top: 14px; }
.import-msg { margin: 0 0 14px; padding: 10px 14px; border-radius: 12px; font-size: 13px;
  background: rgba(129,140,248,.12); border: 1px solid rgba(129,140,248,.35); color: #C7D2FE; }
</style>
