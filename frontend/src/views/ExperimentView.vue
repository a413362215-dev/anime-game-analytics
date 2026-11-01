<template>
  <div class="page-head"><h1 class="page-title">A/B 实验</h1><p class="page-sub">改动是好是坏，不吵，让数据说话——而且要说得算数。</p></div>
  <div class="panel">
    <div class="p-head"><h3 class="p-title">实验详情 · 新手礼包改版</h3><span class="badge b-green">已达显著 · 建议全量</span></div>
    <div class="grid" style="grid-template-columns: 1.3fr 1fr">
      <div><ChartBox :option="ciOpt" :height="212" /></div>
      <div class="stats">
        <div class="stat-row"><span>首充率提升</span><b>+1.30 pt</b></div>
        <div class="stat-row"><span>95% 置信区间</span><b>[+0.42, +2.18]</b></div>
        <div class="stat-row"><span>Z 检验 p 值</span><b>0.003</b></div>
        <div class="stat-row"><span>CUPED 修正后</span><b>+1.21 pt</b></div>
        <div class="stat-row"><span>贝叶斯胜率（B 优于 A）</span><b>97.3%</b></div>
        <div class="stat-row"><span>分组方式</span><b>UID 哈希 · 稳定不串组</b></div>
      </div>
    </div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">全部实验</h3><span class="p-sub">哈希稳定分组 · 同一玩家不会两边跑</span></div>
    <table class="tbl"><thead><tr><th>实验</th><th>状态</th><th>流量</th><th>核心指标</th><th>结果</th><th>结论</th></tr></thead>
    <tbody><tr v-for="e in exps" :key="e.name"><td><b>{{ e.name }}</b></td><td><span class="badge" :class="e.cls">{{ e.status }}</span></td>
      <td>{{ e.traffic }}</td><td>{{ e.metric }}</td><td :class="e.good ? 'up' : ''">{{ e.result }}</td><td class="advice">{{ e.verdict }}</td></tr></tbody></table></div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { ax, TIP } from '../mock/data'
const ciOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 30, top: 26, bottom: 0, containLabel: true },
  xAxis: { type: 'value', min: 6, max: 12, ...ax, axisLabel: { ...ax.axisLabel, formatter: '{value}%' } },
  yAxis: { type: 'category', data: ['实验组 B（新礼包）', '对照组 A（旧礼包）'], axisLabel: ax.axisLabel, axisLine: { show: false } },
  series: [
    { type: 'bar', barWidth: 20, data: [9.7, 8.4], itemStyle: { color: (p: any) => p.dataIndex === 0 ? '#E879F9' : '#60A5FA', borderRadius: [0, 8, 8, 0] }, label: { show: true, position: 'right', color: '#EEF0FF', fontSize: 12.5, formatter: '{c}%' } },
    { type: 'custom', renderItem: (params: any, api: any) => { const y = api.coord([0, params.dataIndex])[1]; const x1 = api.coord([params.dataIndex === 0 ? 8.82 : 7.83, params.dataIndex])[0]; const x2 = api.coord([params.dataIndex === 0 ? 10.58 : 8.97, params.dataIndex])[0]; return { type: 'line', shape: { x1, y1: y, x2, y2: y }, style: { stroke: '#FBBF24', lineWidth: 2.5 } } }, data: [0, 1], tooltip: { show: false } },
  ],
}))
const exps = [
  { name: '新手礼包改版', status: '已结束', cls: 'b-green', traffic: '50% 新玩家', metric: '首充率', result: '+1.30 pt', good: true, verdict: '全量上线' },
  { name: '卡池保底可视化', status: '运行中', cls: 'b-blue', traffic: '30% 全量', metric: '抽卡转化', result: '+0.84 pt', good: true, verdict: '继续观察 3 天' },
  { name: '回归礼包加码', status: '运行中', cls: 'b-blue', traffic: '回流玩家 50%', metric: '回流次留', result: '+2.10 pt', good: true, verdict: '样本量还差 18%' },
  { name: '商城首屏排序', status: '已结束', cls: 'b-gray', traffic: '20% 全量', metric: '商城点击率', result: '-0.12 pt', good: false, verdict: '无显著差异，下线' },
  { name: '体力补给提醒', status: '已结束', cls: 'b-amber', traffic: '40% 全量', metric: '日均时长', result: '+3.4 分钟', good: true, verdict: '显著但投诉率微升，暂缓' },
]
</script>
<style scoped>
.stats { display: flex; flex-direction: column; justify-content: center; gap: 13px; padding-left: 8px; }
.stat-row { display: flex; justify-content: space-between; font-size: 13.5px; border-bottom: 1px dashed rgba(255,255,255,.1); padding-bottom: 9px; }
.stat-row span { color: rgba(238,240,255,.6); } .stat-row b { font-variant-numeric: tabular-nums; }
.advice { color: rgba(238,240,255,.72); font-size: 13px; }
</style>
