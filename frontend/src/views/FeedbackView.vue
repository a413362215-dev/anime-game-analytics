<template>
  <div class="page-head"><h1 class="page-title">版本反馈</h1><p class="page-sub">新版本的心声，替你收好——夸的骂的，都来自评论区、社区与问卷。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p><p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1.5fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">好评率走势 · 5.2 上线后 30 天</h3><span class="p-sub">虚线为 5.1 同期</span></div><ChartBox :option="trendOpt" :height="252" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">六个方面 · 好评率</h3><span class="p-sub">方面级情感分析</span></div><ChartBox :option="aspectOpt" :height="252" /></div>
  </div>
  <div class="grid" style="grid-template-columns: 1fr 1.6fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">大家在聊什么</h3><span class="p-sub">话题热度 TOP</span></div>
      <div class="topics"><span class="chip-tag big" v-for="t in topics" :key="t.name" :style="{ fontSize: t.size + 'px' }">{{ t.name }} <em>{{ t.hot }}</em></span></div>
      <table class="tbl" style="margin-top: 16px"><thead><tr><th>版本对比</th><th>5.1</th><th>5.2</th></tr></thead>
      <tbody><tr><td>整体好评率</td><td>63.2%</td><td><span class="up">68.4%</span></td></tr>
      <tr><td>差评主因</td><td>卡顿</td><td>体力不够</td></tr>
      <tr><td>最受夸奖</td><td>美术</td><td>新剧情</td></tr></tbody></table></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">原声摘录</h3><span class="p-sub">带情感与方面标签 · 可溯源</span></div>
      <div class="cmt" v-for="c in comments" :key="c.text">
        <div class="cmt-top"><b>{{ c.user }}</b><span class="badge" :class="c.cls">{{ c.sent }}</span><span class="chip-tag">{{ c.aspect }}</span><span class="cmt-src">{{ c.src }}</span></div>
        <p>{{ c.text }}</p></div></div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { DAYS, series, ax, TIP, LEG, PALETTE } from '../mock/data'
const kpis = [
  { label: '本版本评价总量', value: '48,210', note: '社区 + 评论区 + 问卷' },
  { label: '整体好评率', value: '68.4%', note: '较 5.1 +5.2pt' },
  { label: '最热话题', value: '新主线剧情', note: '提及 12,483 次' },
  { label: '最需改进', value: '体力恢复', note: '差评里占 31%' },
]
const trendOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, top: 0 }, grid: { left: 8, right: 10, top: 32, bottom: 0, containLabel: true },
  xAxis: { type: 'category', data: DAYS, axisLabel: ax.axisLabel, axisLine: ax.axisLine },
  yAxis: { type: 'value', min: 40, max: 90, ...ax, axisLabel: { ...ax.axisLabel, formatter: '{value}%' } },
  series: [
    { name: '5.2 好评率', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2.4 }, color: PALETTE[3], areaStyle: { color: 'rgba(52,211,153,.13)' }, data: series(66, 0.12, 31).map(v => Math.min(84, v)) },
    { name: '5.1 同期', type: 'line', smooth: true, symbol: 'none', lineStyle: { width: 2, type: 'dashed' }, color: 'rgba(238,240,255,.45)', data: series(61, 0.12, 47).map(v => Math.min(78, v)) },
  ],
}))
const aspectOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 24, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', max: 100, ...ax, axisLabel: { ...ax.axisLabel, formatter: '{value}%' } },
  yAxis: { type: 'category', inverse: true, axisLabel: ax.axisLabel, axisLine: { show: false }, data: ['剧情', '角色', '美术音乐', '玩法', '抽卡福利', '优化卡顿'] },
  series: [{ type: 'bar', barWidth: 12, data: [86, 82, 79, 71, 58, 44],
    itemStyle: { color: (p: any) => [PALETTE[3], PALETTE[3], PALETTE[0], PALETTE[0], '#FBBF24', '#F87171'][p.dataIndex], borderRadius: [0, 6, 6, 0] },
    label: { show: true, position: 'right', color: 'rgba(238,240,255,.75)', fontSize: 11.5, formatter: '{c}%' } }],
}))
const topics = [
  { name: '新主线剧情', hot: '12.5k', size: 16 }, { name: '体力不够用', hot: '8.1k', size: 14.5 },
  { name: '新角色强度', hot: '7.6k', size: 14.5 }, { name: '拍照模式', hot: '5.2k', size: 13.5 },
  { name: '加载变快了', hot: '4.8k', size: 13.5 }, { name: '联机掉线', hot: '3.9k', size: 13 },
  { name: '周边联动', hot: '3.1k', size: 12.5 }, { name: '配音彩蛋', hot: '2.7k', size: 12.5 },
]
const comments = [
  { user: '云堇的小跟班', sent: '好评', cls: 'b-green', aspect: '剧情', src: '米游社 · 5.2 讨论区', text: '这一章把三年前的伏笔全收了，结尾那段过场我看哭了，新版本的心声就该先夸剧情组。' },
  { user: '体力焦虑症', sent: '差评', cls: 'b-red', aspect: '玩法', src: 'TapTap 评论', text: '活动和日常都想肝，体力根本不够用，每天上线先算体力账，玩游戏像上班。' },
  { user: '理智抽卡人', sent: '中评', cls: 'b-amber', aspect: '抽卡福利', src: 'B站评论区', text: '新角色是真香，但连着两个池子都吃满大保底，钱包遭不住。保底进度能看见之后心里好受多了。' },
  { user: '帧数观察员', sent: '好评', cls: 'b-green', aspect: '优化卡顿', src: '米游社 · 5.2 讨论区', text: '这次优化是真下了功夫，老手机跑新地图稳 60 帧，发热也小了，给优化组加鸡腿。' },
]
</script>
<style scoped>
.topics { display: flex; flex-wrap: wrap; gap: 9px; }
.topics .chip-tag { padding: 7px 13px; } .topics em { font-style: normal; color: #A5B4FC; font-size: 11.5px; margin-left: 4px; }
.cmt { padding: 13px 0; border-bottom: 1px solid rgba(255,255,255,.07); } .cmt:last-child { border-bottom: none; }
.cmt-top { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.cmt-src { margin-left: auto; font-size: 11.5px; color: rgba(238,240,255,.45); }
.cmt p { margin: 8px 0 0; font-size: 13.5px; line-height: 1.7; color: rgba(238,240,255,.82); }
</style>
