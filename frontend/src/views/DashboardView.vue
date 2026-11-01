<template>
  <div class="page-head"><h1 class="page-title">总览看板</h1><p class="page-sub">今日的世界，热闹依旧吗——先看一眼全局，再决定今天做什么。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label">
      <p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p>
      <p class="kpi-foot">较昨日 <span :class="k.up ? 'up' : 'down'">{{ k.delta }}</span> · {{ k.note }}</p>
    </div>
  </div>
  <div class="grid" style="grid-template-columns: 2fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">近 30 日 · 活跃与流水</h3><span class="p-sub">周末与版本日会明显抬头</span></div>
      <ChartBox :option="trendOpt" :height="288" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">今日动态</h3><span class="p-sub">沿途记事</span></div>
      <div class="feed">
        <div class="feed-item" v-for="f in feed" :key="f.text"><span class="badge" :class="f.cls">{{ f.tag }}</span>
          <div><p>{{ f.text }}</p><span>{{ f.time }}</span></div></div>
      </div></div>
  </div>
  <p v-if="fromDb" class="src-note">本页数字来自数据库聚合（模拟生成的 180 天数据），切换顶栏游戏可看另一款。</p>
  <div class="grid" style="grid-template-columns: 1fr 1fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">卡池收入 TOP 5</h3><span class="p-sub">本版本累计</span></div><ChartBox :option="bannerOpt" :height="218" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">玩家构成</h3><span class="p-sub">按付费习惯分</span></div><ChartBox :option="mixOpt" :height="218" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">留存一眼</h3><span class="p-sub">近 4 期新玩家</span></div><ChartBox :option="retOpt" :height="218" /></div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import request from '../api/request'
import { useGameStore } from '../stores/game'
import { DAYS, series, ax, TIP, LEG, PALETTE, fmt } from '../mock/data'

// 先用前端演示值占位，后端有响应就整体换成数据库聚合（阶段 2 起总览页读真库）
const kpis = ref<any[]>([
  { label: '今日活跃玩家', value: '—', delta: '', up: true, note: '正在从数据库读取…' },
  { label: '新增玩家', value: '—', delta: '', up: true, note: '' },
  { label: '今日流水', value: '—', delta: '', up: true, note: '' },
  { label: '次日留存', value: '—', delta: '', up: true, note: '' },
])
const feed = ref<any[]>([])
const trendDays = ref<string[]>(DAYS)
const trendDau = ref<number[]>(series(112000, 0.14, 7))
const trendRev = ref<number[]>(series(44, 0.3, 21))
const bannerNames = ref<string[]>(['月下拾光', '星海巡航', '花间四杰', '云间候月', '常驻祈愿'])
const bannerVals = ref<number[]>([486, 352, 289, 176, 158])
const mixData = ref<any[]>([
  { value: 46, name: '零氪', itemStyle: { color: '#60A5FA' } }, { value: 27, name: '月卡党', itemStyle: { color: '#818CF8' } },
  { value: 18, name: '中R', itemStyle: { color: '#E879F9' } }, { value: 9, name: '大R', itemStyle: { color: '#FBBF24' } }])
const retWeeks = ref<string[]>(['10/06 期', '10/13 期', '10/20 期', '10/27 期'])
const retD1 = ref<number[]>([44.1, 45.6, 46.9, 46.8])
const retD7 = ref<number[]>([26.3, 27.8, 28.4, 29.1])
const fromDb = ref(false)

const gameStore = useGameStore()
async function load() {
  try {
    const { data } = await request.get('/analytics/overview', { params: { game: gameStore.game } })
    if (data.error) return
    kpis.value = data.kpis
    feed.value = data.feed
    trendDays.value = data.trend.days; trendDau.value = data.trend.dau; trendRev.value = data.trend.revenue_wan
    bannerNames.value = data.banner_top.map((b: any) => b.name); bannerVals.value = data.banner_top.map((b: any) => b.amount_wan)
    const colors: Record<string, string> = { '零氪': '#60A5FA', '月卡党': '#818CF8', '中R': '#E879F9', '大R': '#FBBF24' }
    mixData.value = data.mix.map((m: any) => ({ value: m.value, name: m.name, itemStyle: { color: colors[m.name] || '#818CF8' } }))
    retWeeks.value = data.retention.weeks; retD1.value = data.retention.d1; retD7.value = data.retention.d7
    fromDb.value = true
  } catch { /* 后端没起时保留演示值，不白屏 */ }
}
onMounted(load)
watch(() => gameStore.game, load)

const trendOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 8, top: 34, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: trendDays.value, ...ax, axisLine: ax.axisLine, axisLabel: ax.axisLabel },
  yAxis: [{ type: 'value', name: '活跃', ...ax }, { type: 'value', name: '流水(万)', splitLine: { show: false }, axisLabel: ax.axisLabel }],
  series: [
    { name: '活跃玩家', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.4 }, color: PALETTE[0], areaStyle: { color: 'rgba(129,140,248,.16)' }, data: trendDau.value },
    { name: '流水(万元)', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'none', lineStyle: { width: 2.4 }, color: PALETTE[1], data: trendRev.value },
  ],
}))
const bannerOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 16, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', ...ax }, yAxis: { type: 'category', inverse: true, data: bannerNames.value, axisLabel: ax.axisLabel, axisLine: { show: false } },
  series: [{ type: 'bar', data: bannerVals.value, barWidth: 13, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#60A5FA' }, { offset: 1, color: '#E879F9' }] }, borderRadius: [0, 7, 7, 0] }, label: { show: true, position: 'right', color: 'rgba(238,240,255,.7)', fontSize: 11.5, formatter: '¥{c}万' } }],
}))
const mixOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, bottom: 0, left: 'center' },
  series: [{ type: 'pie', radius: ['52%', '74%'], center: ['50%', '44%'], itemStyle: { borderColor: 'rgba(10,14,39,.9)', borderWidth: 2 },
    label: { color: 'rgba(238,240,255,.8)', fontSize: 11.5, formatter: (p: any) => `${p.name} ${Math.round(p.percent)}%` }, data: mixData.value }],
}))
const retOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 8, top: 32, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: retWeeks.value, axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', max: 70, ...ax, axisLabel: { ...ax.axisLabel, formatter: '{value}%' } },
  series: [
    { name: '次日留存', type: 'bar', barWidth: 11, color: PALETTE[2], itemStyle: { borderRadius: [5, 5, 0, 0] }, data: retD1.value },
    { name: '7 日留存', type: 'bar', barWidth: 11, color: PALETTE[1], itemStyle: { borderRadius: [5, 5, 0, 0] }, data: retD7.value },
  ],
}))
</script>
<style scoped>
.feed { display: flex; flex-direction: column; gap: 15px; }
.src-note { margin: 16px 2px 0; font-size: 12px; color: rgba(238,240,255,.45); }
.feed-item { display: flex; gap: 11px; align-items: flex-start; }
.feed-item p { margin: 0; font-size: 13.5px; line-height: 1.55; }
.feed-item span { font-size: 11.5px; color: rgba(238,240,255,.45); }
.feed-item .badge { margin-top: 1px; }
</style>
