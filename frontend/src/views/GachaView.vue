<template>
  <div class="page-head"><h1 class="page-title">付费与抽卡</h1><p class="page-sub">每一抽，都算数——谁在为爱一掷千金，账要算得清清楚楚。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p><p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1.2fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">出货抽数分布</h3><span class="p-sub">第几抽迎来金光</span></div><ChartBox :option="histOpt" :height="248" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">各卡池抽数</h3><span class="p-sub">本版本累计（万抽）</span></div><ChartBox :option="poolOpt" :height="248" /></div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">大佬抽卡榜</h3><span class="p-sub">本版本 · 按消费排序</span></div>
    <table class="tbl"><thead><tr><th>玩家</th><th>总抽数</th><th>累计消费</th><th>五星数</th><th>平均出货</th><th>最爱卡池</th></tr></thead>
    <tbody><tr v-for="p in tops" :key="p.name"><td><b>{{ p.name }}</b></td><td>{{ p.pulls }}</td><td>¥{{ p.spend }}</td><td>{{ p.five }}</td>
      <td>{{ p.avg }} 抽</td><td><span class="chip-tag">{{ p.pool }}</span></td></tr></tbody></table></div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { ax, TIP, PALETTE } from '../mock/data'
const kpis = [
  { label: '本版本总抽数', value: '864.2 万', note: '较上版本 +12.6%' },
  { label: '五星出货率', value: '1.86%', note: '含保底 · 符合公示概率' },
  { label: '平均出货抽数', value: '54.2 抽', note: '中位数 47 抽' },
  { label: '保底歪率', value: '46.3%', note: '大保底触发占比 31%' },
]
const histOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 10, top: 12, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: ['1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90'], name: '抽数', axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', name: '出货次数', ...ax },
  series: [{ type: 'bar', barWidth: '62%', data: [42100, 39800, 35200, 31600, 28900, 26400, 24800, 31200, 48600],
    itemStyle: { color: (p: any) => p.dataIndex >= 7 ? '#FBBF24' : '#818CF8', borderRadius: [6, 6, 0, 0] } }],
}))
const poolOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 20, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', ...ax }, yAxis: { type: 'category', inverse: true, axisLabel: ax.axisLabel, axisLine: { show: false },
    data: ['月下拾光（限定）', '星海巡航（限定）', '花间四杰（复刻）', '云间候月（复刻）', '常驻祈愿'] },
  series: [{ type: 'bar', barWidth: 13, data: [286, 214, 158, 117, 89],
    itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#60A5FA' }, { offset: 1, color: '#E879F9' }] }, borderRadius: [0, 7, 7, 0] },
    label: { show: true, position: 'right', color: 'rgba(238,240,255,.7)', fontSize: 11.5 } }],
}))
const tops = [
  { name: '夜樱未眠', pulls: '4,820', spend: '78,400', five: 86, avg: 56, pool: '月下拾光' },
  { name: '星尘旅者', pulls: '3,915', spend: '63,250', five: 74, avg: 53, pool: '星海巡航' },
  { name: '满命收藏家', pulls: '3,560', spend: '59,800', five: 71, avg: 50, pool: '花间四杰' },
  { name: '月亮邮递员', pulls: '2,940', spend: '47,120', five: 52, avg: 57, pool: '月下拾光' },
  { name: '为爱发电中', pulls: '2,610', spend: '41,930', five: 49, avg: 53, pool: '云间候月' },
]
</script>
