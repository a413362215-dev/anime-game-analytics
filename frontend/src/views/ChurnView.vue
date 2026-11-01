<template>
  <div class="page-head"><h1 class="page-title">流失预警</h1><p class="page-sub">在离站之前，先留住他——模型每天清晨更新一次名单。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p>
      <p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1fr 1.4fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">风险分层</h3><span class="p-sub">全体活跃玩家</span></div><ChartBox :option="riskOpt" :height="232" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">他们为什么想走</h3><span class="p-sub">影响程度（SHAP 重要性）</span></div><ChartBox :option="factorOpt" :height="232" /></div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">高风险玩家 · TOP 名单</h3><span class="p-sub">按风险分排序 · 点开可看单人解释</span></div>
    <table class="tbl"><thead><tr><th>玩家</th><th>分组</th><th>风险分</th><th>主要原因</th><th>上次活跃</th><th>建议动作</th><th></th></tr></thead>
    <tbody><tr v-for="p in players" :key="p.uid">
      <td><b>{{ p.name }}</b><span class="uid">UID {{ p.uid }}</span></td><td>{{ p.seg }}</td>
      <td><span class="badge" :class="p.score >= 90 ? 'b-red' : 'b-amber'">{{ p.score }}</span></td>
      <td><span class="chip-tag" v-for="r in p.reasons" :key="r" style="margin-right: 6px">{{ r }}</span></td>
      <td>{{ p.last }}</td><td class="advice">{{ p.action }}</td>
      <td><button class="btn-g" style="padding: 5px 13px; font-size: 12.5px">加入挽留</button></td></tr></tbody></table></div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { ax, TIP, LEG } from '../mock/data'
const kpis = [
  { label: '高风险玩家', value: '12,483', note: '未来 14 天大概率离站' },
  { label: '中风险玩家', value: '38,210', note: '活跃正在下滑，先观察' },
  { label: '近 30 日已挽回', value: '2,146', note: '收到召回后重新登录' },
  { label: '挽回成功率', value: '31.4%', note: '高于上期 +2.2pt' },
]
const riskOpt = computed(() => ({
  tooltip: TIP, legend: { ...LEG, bottom: 0, left: 'center' },
  series: [{ type: 'pie', radius: ['54%', '76%'], center: ['50%', '44%'], itemStyle: { borderColor: 'rgba(10,14,39,.9)', borderWidth: 2 },
    label: { color: 'rgba(238,240,255,.8)', fontSize: 11.5 },
    data: [ { value: 12483, name: '高风险', itemStyle: { color: '#F87171' } }, { value: 38210, name: '中风险', itemStyle: { color: '#FBBF24' } }, { value: 77847, name: '安稳', itemStyle: { color: '#34D399' } } ] }],
}))
const factorOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 22, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', ...ax }, yAxis: { type: 'category', inverse: true, axisLabel: ax.axisLabel, axisLine: { show: false },
    data: ['距上次登录天数', '周活跃时长下降', '日常任务未完成', '副本失败率上升', '好友相继离站', '卡池连败（非酋）'] },
  series: [{ type: 'bar', barWidth: 12, data: [0.31, 0.24, 0.16, 0.12, 0.1, 0.07],
    itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#F87171' }, { offset: 1, color: '#FBBF24' }] }, borderRadius: [0, 6, 6, 0] } }],
}))
const players = [
  { name: '夜樱未眠', uid: '800123417', seg: '氪金大佬', score: 94, reasons: ['9 天未登录', '周活 -72%'], last: '11/01 前', action: '专属客服问候 + 限定返场预告' },
  { name: '提瓦特闲人', uid: '800276531', seg: '月卡党', score: 92, reasons: ['月卡断供', '日常连缺 5 天'], last: '10/30', action: '月卡续费提醒，语气要轻' },
  { name: '非酋本酋', uid: '800391204', seg: '收藏党', score: 91, reasons: ['连续 2 池未出货', '活跃 -64%'], last: '10/29', action: '保底进度可视化 + 心意礼包' },
  { name: '肝帝阿泽', uid: '800455882', seg: '肝帝', score: 88, reasons: ['长草期无事可做', '周活 -58%'], last: '10/31', action: '高难挑战预告，提前透出' },
  { name: '剧情追更中', uid: '800517730', seg: '剧情党', score: 86, reasons: ['主线已通关', '登录间隔变长'], last: '10/30', action: '下一章剧情线索推送' },
  { name: '月亮邮递员', uid: '800602149', seg: '稳定中R', score: 85, reasons: ['好友 3 人离站', '周活 -51%'], last: '10/31', action: '组队活动邀请，拉回社交圈' },
]
</script>
<style scoped>
.uid { display: block; font-size: 11.5px; color: rgba(238,240,255,.45); margin-top: 2px; }
.advice { color: rgba(238,240,255,.72); font-size: 13px; }
</style>
