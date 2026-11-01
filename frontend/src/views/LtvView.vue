<template>
  <div class="page-head"><h1 class="page-title">LTV 预测</h1><p class="page-sub">一位玩家会在这里走多远，花多少——三种算法一起估，再互相印证。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p><p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1.6fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">累计 LTV 曲线 · 10 月新玩家队列</h3><span class="p-sub">实线为已发生的 30 天，虚线为各模型外推</span></div>
      <ChartBox :option="curveOpt" :height="292" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">三模型对比</h3><span class="p-sub">时间切分验证</span></div>
      <table class="tbl"><thead><tr><th>模型</th><th>MAE</th><th>RMSE</th></tr></thead>
      <tbody><tr v-for="m in models" :key="m.name"><td><b>{{ m.name }}</b><span class="m-note">{{ m.note }}</span></td><td>{{ m.mae }}</td><td>{{ m.rmse }}</td></tr></tbody></table>
      <p class="honest">验证口径：只用玩家前 7 天行为预测后续，特征按时间切分，杜绝「用未来猜过去」式的虚假高分。</p></div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">各注册月队列 · 90 日 LTV 预测</h3><span class="p-sub">单位：元 / 人</span></div>
    <ChartBox :option="cohortOpt" :height="216" /></div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { ax, TIP, LEG, PALETTE } from '../mock/data'
const kpis = [
  { label: '新玩家 30 日 LTV', value: '¥86.4', note: '较上期队列 +5.1%' },
  { label: '新玩家 90 日 LTV（预测）', value: '¥212.7', note: '三模型中位数' },
  { label: '付费玩家 LTV', value: '¥694', note: '占新玩家 14.2%' },
  { label: '回本周期（CAC 口径）', value: '23 天', note: '按当前买量成本估算' },
]
const models = [
  { name: 'XGBoost 回归', note: '7/30/90 天三段预测', mae: '18.6', rmse: '31.2' },
  { name: 'BG/NBD + Gamma-Gamma', note: '经典概率模型，稳', mae: '21.4', rmse: '35.8' },
  { name: 'Cox 生存分析', note: '先估留存，再叠付费', mae: '23.9', rmse: '38.1' },
]
const days = Array.from({ length: 91 }, (_, i) => i)
const actual = days.map(d => d <= 30 ? Math.round(212 * (1 - Math.exp(-d / 16)) * 0.62) : null)
const xgb = days.map(d => Math.round(218 * (1 - Math.exp(-d / 17))))
const bgnbd = days.map(d => Math.round(205 * (1 - Math.exp(-d / 19))))
const curveOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 12, top: 34, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: days, name: '注册后天数', axisLabel: { ...ax.axisLabel, interval: 14 }, axisLine: ax.axisLine },
  yAxis: { type: 'value', name: '累计 ¥', ...ax },
  series: [
    { name: '实测（前 30 天）', type: 'line', data: actual, symbol: 'none', lineStyle: { width: 2.6 }, color: '#EEF0FF' },
    { name: 'XGBoost', type: 'line', data: xgb, symbol: 'none', lineStyle: { width: 2, type: 'dashed' }, color: PALETTE[0] },
    { name: 'BG/NBD+GG', type: 'line', data: bgnbd, symbol: 'none', lineStyle: { width: 2, type: 'dashed' }, color: PALETTE[1] },
  ],
}))
const cohortOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 12, top: 10, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: ['5 月', '6 月', '7 月', '8 月', '9 月', '10 月'], axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', ...ax },
  series: [{ type: 'bar', barWidth: 34, data: [168, 175, 189, 196, 204, 213],
    itemStyle: { color: { type: 'linear', x: 0, y: 1, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#60A5FA' }, { offset: 1, color: '#E879F9' }] }, borderRadius: [8, 8, 0, 0] },
    label: { show: true, position: 'top', color: 'rgba(238,240,255,.75)', fontSize: 12, formatter: '¥{c}' } }],
}))
</script>
<style scoped>
.m-note { display: block; font-size: 11.5px; color: rgba(238,240,255,.45); margin-top: 2px; }
.honest { margin: 14px 0 0; font-size: 12.5px; line-height: 1.7; color: rgba(238,240,255,.6); background: rgba(52,211,153,.08); border: 1px solid rgba(52,211,153,.25); padding: 11px 14px; border-radius: 12px; }
</style>
