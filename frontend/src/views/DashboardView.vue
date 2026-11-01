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
  <div class="grid" style="grid-template-columns: 1fr 1fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">卡池收入 TOP 5</h3><span class="p-sub">本版本累计</span></div><ChartBox :option="bannerOpt" :height="218" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">玩家构成</h3><span class="p-sub">按付费习惯分</span></div><ChartBox :option="mixOpt" :height="218" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">留存一眼</h3><span class="p-sub">近 4 期新玩家</span></div><ChartBox :option="retOpt" :height="218" /></div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { DAYS, series, ax, TIP, LEG, PALETTE } from '../mock/data'
const kpis = [
  { label: '今日活跃玩家', value: '128,540', delta: '+4.2%', up: true, note: '周六晚间高峰未到' },
  { label: '新增玩家', value: '8,642', delta: '+11.3%', up: true, note: '新版本预热带来一波' },
  { label: '今日流水', value: '¥486,200', delta: '+7.9%', up: true, note: '新卡池开启第 3 天' },
  { label: '次日留存', value: '46.8%', delta: '-0.6pt', up: false, note: '新手期流失略有抬头' },
]
const feed = [
  { tag: '版本', cls: 'b-purple', text: '5.2 版本「流光拾遗之旅」开启第 3 天，活跃创近 30 日新高', time: '今天 09:20' },
  { tag: '卡池', cls: 'b-blue', text: '限定卡池「月下拾光」收入进入版本 TOP 2', time: '今天 08:45' },
  { tag: '预警', cls: 'b-red', text: '新手引导第 4 关流失率较昨日上升 2.1pt，已同步流失预警', time: '今天 08:10' },
  { tag: '反馈', cls: 'b-amber', text: '版本反馈新增 3,214 条，「优化卡顿」话题热度上升', time: '昨天 23:40' },
  { tag: '实验', cls: 'b-green', text: '实验「新手礼包改版」达到显著，胜率 97.3%', time: '昨天 21:15' },
]
const trendOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 8, top: 34, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: DAYS, ...ax, axisLine: ax.axisLine, axisLabel: ax.axisLabel },
  yAxis: [{ type: 'value', name: '活跃', ...ax }, { type: 'value', name: '流水(万)', splitLine: { show: false }, axisLabel: ax.axisLabel }],
  series: [
    { name: '活跃玩家', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.4 }, color: PALETTE[0], areaStyle: { color: 'rgba(129,140,248,.16)' }, data: series(112000, 0.14, 7) },
    { name: '流水(万元)', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'none', lineStyle: { width: 2.4 }, color: PALETTE[1], data: series(44, 0.3, 21) },
  ],
}))
const bannerOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 16, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', ...ax }, yAxis: { type: 'category', inverse: true, data: ['月下拾光', '星海巡航', '花间四杰', '云间候月', '常驻祈愿'], axisLabel: ax.axisLabel, axisLine: { show: false } },
  series: [{ type: 'bar', data: [486, 352, 289, 176, 158], barWidth: 13, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#60A5FA' }, { offset: 1, color: '#E879F9' }] }, borderRadius: [0, 7, 7, 0] }, label: { show: true, position: 'right', color: 'rgba(238,240,255,.7)', fontSize: 11.5, formatter: '¥{c}万' } }],
}))
const mixOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, bottom: 0, left: 'center' },
  series: [{ type: 'pie', radius: ['52%', '74%'], center: ['50%', '44%'], itemStyle: { borderColor: 'rgba(10,14,39,.9)', borderWidth: 2 },
    label: { color: 'rgba(238,240,255,.8)', fontSize: 11.5 },
    data: [ { value: 46, name: '零氪', itemStyle: { color: '#60A5FA' } }, { value: 27, name: '月卡党', itemStyle: { color: '#818CF8' } }, { value: 18, name: '中R', itemStyle: { color: '#E879F9' } }, { value: 9, name: '大R', itemStyle: { color: '#FBBF24' } } ] }],
}))
const retOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 8, top: 32, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: ['10/06 期', '10/13 期', '10/20 期', '10/27 期'], axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', max: 60, ...ax, axisLabel: { ...ax.axisLabel, formatter: '{value}%' } },
  series: [
    { name: '次日留存', type: 'bar', barWidth: 11, color: PALETTE[2], itemStyle: { borderRadius: [5, 5, 0, 0] }, data: [44.1, 45.6, 46.9, 46.8] },
    { name: '7 日留存', type: 'bar', barWidth: 11, color: PALETTE[1], itemStyle: { borderRadius: [5, 5, 0, 0] }, data: [26.3, 27.8, 28.4, 29.1] },
  ],
}))
</script>
<style scoped>
.feed { display: flex; flex-direction: column; gap: 15px; }
.feed-item { display: flex; gap: 11px; align-items: flex-start; }
.feed-item p { margin: 0; font-size: 13.5px; line-height: 1.55; }
.feed-item span { font-size: 11.5px; color: rgba(238,240,255,.45); }
.feed-item .badge { margin-top: 1px; }
</style>
