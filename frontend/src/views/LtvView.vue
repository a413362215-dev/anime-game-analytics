<template>
  <div class="page-head"><h1 class="page-title">LTV 预测</h1><p class="page-sub">一位玩家会在这里走多远，花多少——三种算法一起估，再互相印证。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p><p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1.6fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">累计 LTV 曲线 · 测试队列</h3><span class="p-sub">实线为实测累计，虚线为各模型外推（按实测累积形态展开）</span></div>
      <ChartBox :option="curveOpt" :height="292" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">三模型对比</h3><span class="p-sub">时间切分验证 · 测试 {{ fmt(testN) }} 人</span></div>
      <table class="tbl"><thead><tr><th>模型</th><th>MAE</th><th>Spearman</th></tr></thead>
      <tbody><tr v-for="m in models" :key="m.name"><td><b>{{ m.name }}</b><span class="m-note">{{ NOTES[m.name] }}</span></td><td>{{ m.mae }}</td><td>{{ m.spearman }}</td></tr></tbody></table>
      <p class="honest">验证口径：只用玩家前 30 天（校准窗）预测第 31~90 天消费，按注册日期切分训练/测试。没有哪个模型全赢：回归金额最准、Cox 排序最好、BG/NBD 对 79% 无交易玩家是盲区（付费子集 Spearman 单列在明细数据里）。</p></div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">各注册月队列 · 90 日 LTV</h3><span class="p-sub">单位：元 / 人 · 深色为实测、浅色为三模型中位数预测</span></div>
    <ChartBox :option="cohortOpt" :height="216" /></div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import request from '../api/request'
import { useGameStore } from '../stores/game'
import { ax, TIP, LEG, PALETTE, fmt } from '../mock/data'

const NOTES: Record<string, string> = {
  'BG/NBD + Gamma-Gamma': '经典概率模型，只认交易记录',
  'LightGBM 回归': '行为特征直接回归，金额最准',
  'Cox 生存 + 付费率': '先估留存再叠付费，排序最好',
}
const kpis = ref<any[]>([])
const models = ref<any[]>([])
const curve = ref<any>(null)
const cohorts = ref<any[]>([])
const testN = ref(0)
const gameStore = useGameStore()
async function load() {
  try {
    const { data } = await request.get('/analytics/ltv', { params: { game: gameStore.game } })
    if (data.error) return
    kpis.value = data.kpis; models.value = data.models; curve.value = data.curve
    cohorts.value = data.cohorts; testN.value = data.test_n
  } catch { /* 后端离线时保持空态 */ }
}
onMounted(load)
watch(() => gameStore.game, load)

const curveOpt = computed(() => {
  if (!curve.value) return {}
  const names = Object.keys(curve.value.models)
  return {
    tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 12, top: 34, bottom: 0, containLabel: true },
    xAxis: { type: 'category', data: curve.value.days, name: '注册后天数', axisLabel: { ...ax.axisLabel }, axisLine: ax.axisLine },
    yAxis: { type: 'value', name: '累计 ¥', ...ax },
    series: [
      { name: '实测累计', type: 'line', data: curve.value.actual, symbol: 'none', lineStyle: { width: 2.6 }, color: '#EEF0FF' },
      ...names.map((n: string, i: number) => ({ name: n, type: 'line', data: curve.value.models[n], symbol: 'none',
        lineStyle: { width: 2, type: 'dashed' }, color: PALETTE[i % PALETTE.length] })),
    ],
  }
})
const cohortOpt = computed(() => ({
  tooltip: { ...TIP, formatter: (p: any) => `${p.name} 月注册队列<br/>90 日 LTV ¥${p.value}（${cohorts.value[p.dataIndex]?.kind}）` },
  grid: { left: 8, right: 10, top: 12, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: cohorts.value.map(c => `${c.month}月`), axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', name: '¥ / 人', ...ax },
  series: [{ type: 'bar', barWidth: '52%',
    data: cohorts.value.map(c => ({ value: c.value, itemStyle: { color: c.kind === '实测' ? '#818CF8' : 'rgba(129,140,248,.38)', borderRadius: [6, 6, 0, 0] } })),
    label: { show: true, position: 'top', color: 'rgba(238,240,255,.7)', fontSize: 11.5 } }],
}))
</script>
<style scoped>
.m-note { display: block; font-size: 11.5px; color: rgba(238,240,255,.45); margin-top: 2px; }
.honest { margin: 12px 2px 0; font-size: 12.5px; line-height: 1.65; color: rgba(238,240,255,.55); }
</style>
