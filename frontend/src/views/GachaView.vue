<template>
  <div class="page-head"><h1 class="page-title">付费与抽卡</h1><p class="page-sub">每一抽，都算数——谁在为爱一掷千金，账要算得清清楚楚。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p><p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1.2fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">出货抽数分布</h3><span class="p-sub">第几抽迎来金光 · 71-80 抽的尖峰就是软保底</span></div><ChartBox :option="histOpt" :height="248" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">各卡池抽数</h3><span class="p-sub">近 180 天累计（抽）</span></div><ChartBox :option="poolOpt" :height="248" /></div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">大佬抽卡榜</h3><span class="p-sub">近 180 天 · 按总抽数排序 · 抽卡为样本口径</span></div>
    <table class="tbl"><thead><tr><th>玩家</th><th>总抽数</th><th>累计消费</th><th>五星数</th><th>平均出货</th><th>最爱卡池</th></tr></thead>
    <tbody><tr v-for="p in tops" :key="p.name + p.uid_tail"><td><b>{{ p.name }}</b><span class="uid" style="display: block; margin-left: 0">UID ··{{ p.uid_tail }}</span></td><td>{{ fmt(p.pulls) }}</td><td>¥{{ fmt(p.spend) }}</td><td>{{ p.five }}</td>
      <td>{{ p.avg_pity }} 抽</td><td><span class="chip-tag">{{ p.pool }}</span></td></tr></tbody></table></div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import request from '../api/request'
import { useGameStore } from '../stores/game'
import { ax, TIP, fmt } from '../mock/data'

const kpis = ref<any[]>([
  { label: '累计总抽数', value: '—', note: '正在从数据库读取…' },
  { label: '五星出货率', value: '—', note: '' },
  { label: '平均出货抽数', value: '—', note: '' },
  { label: '深保底占比', value: '—', note: '' },
])
const histBuckets = ref<string[]>(['1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90'])
const histCounts = ref<number[]>([42100, 39800, 35200, 31600, 28900, 26400, 24800, 31200, 48600])
const poolNames = ref<string[]>(['月下拾光', '星海巡航', '花间四杰', '云间候月', '常驻祈愿'])
const poolVals = ref<number[]>([286, 214, 158, 117, 89])
const tops = ref<any[]>([])

const gameStore = useGameStore()
async function load() {
  try {
    const { data } = await request.get('/analytics/gacha', { params: { game: gameStore.game } })
    if (data.error) return
    kpis.value = data.kpis
    histBuckets.value = data.hist.buckets; histCounts.value = data.hist.counts
    poolNames.value = data.pools.map((p: any) => p.name); poolVals.value = data.pools.map((p: any) => p.pulls)
    tops.value = data.tops
  } catch { /* 保留演示值 */ }
}
onMounted(load)
watch(() => gameStore.game, load)

const histOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 10, top: 12, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: histBuckets.value, name: '抽数', axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', name: '出货次数', ...ax },
  series: [{ type: 'bar', barWidth: '62%', data: histCounts.value,
    itemStyle: { color: (p: any) => p.dataIndex >= 7 ? '#FBBF24' : '#818CF8', borderRadius: [6, 6, 0, 0] } }],
}))
const poolOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 34, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', ...ax }, yAxis: { type: 'category', inverse: true, axisLabel: ax.axisLabel, axisLine: { show: false }, data: poolNames.value },
  series: [{ type: 'bar', barWidth: 13, data: poolVals.value,
    itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#60A5FA' }, { offset: 1, color: '#E879F9' }] }, borderRadius: [0, 7, 7, 0] },
    label: { show: true, position: 'right', color: 'rgba(238,240,255,.7)', fontSize: 11.5, formatter: (p: any) => fmt(p.value) } }],
}))
</script>
