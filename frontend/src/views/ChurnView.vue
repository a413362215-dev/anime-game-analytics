<template>
  <div class="page-head"><h1 class="page-title">流失预警</h1><p class="page-sub">在离站之前，先留住他——用前 14 天的行为，预测未来 14 天的离站。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel" v-for="k in kpis" :key="k.label"><p class="kpi-label">{{ k.label }}</p><p class="kpi-num">{{ k.value }}</p>
      <p class="kpi-foot">{{ k.note }}</p></div>
  </div>
  <div class="grid" style="grid-template-columns: 1fr 1.4fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">风险分层</h3><span class="p-sub">测试集玩家按风险分位分层 · 标注为各层实际流失率</span></div><ChartBox :option="riskOpt" :height="232" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">他们为什么想走</h3><span class="p-sub">影响程度（SHAP 重要性）</span></div><ChartBox :option="factorOpt" :height="232" /></div>
  </div>
  <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">当前高风险名单</h3><span class="p-sub">注册满两周、最近仍在活跃的玩家 · 按风险分排序 · 原因来自单人 SHAP</span></div>
    <table class="tbl"><thead><tr><th>玩家</th><th>分组</th><th>风险分</th><th>主要原因</th><th>上次活跃</th><th>建议动作</th></tr></thead>
    <tbody><tr v-for="p in players" :key="p.name + p.uid_tail">
      <td><b>{{ p.name }}</b><span class="uid">UID ··{{ p.uid_tail }}</span></td><td>{{ p.segment }}</td>
      <td><span class="badge" :class="p.score >= 40 ? 'b-red' : 'b-amber'">{{ p.score }}</span></td>
      <td><span class="chip-tag" v-for="r in p.reasons" :key="r" style="margin-right: 6px">{{ r }}</span></td>
      <td>{{ p.last }}</td><td class="advice">{{ p.action }}</td></tr></tbody></table>
    <p class="method-note" v-if="meta">方法论（防泄漏）：特征只用注册后前 {{ meta.obs_window }} 天数据，标签是其后 {{ meta.pred_window }} 天内离站并经 14 天沉默确认；{{ meta.split_note }}；训练 {{ fmt(meta.train_n) }} 人 / 测试 {{ fmt(meta.test_n) }} 人，模型带单调约束（活跃越多、风险越低）。AUC {{ meta.auc }} 是这批数据的真实水平——用「距今未活跃天数」当特征能刷到接近 1.0，那是泄漏，不是本事。</p></div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import request from '../api/request'
import { useGameStore } from '../stores/game'
import { ax, TIP, LEG, fmt } from '../mock/data'

const kpis = ref<any[]>([])
const tiers = ref<any[]>([])
const importance = ref<any[]>([])
const players = ref<any[]>([])
const meta = ref<any>(null)
const gameStore = useGameStore()
async function load() {
  try {
    const { data } = await request.get('/analytics/churn', { params: { game: gameStore.game } })
    if (data.error) return
    kpis.value = data.kpis; tiers.value = data.tiers
    importance.value = data.importance; players.value = data.live; meta.value = data
  } catch { /* 后端离线时保持空态 */ }
}
onMounted(load)
watch(() => gameStore.game, load)

const riskOpt = computed(() => ({
  tooltip: { ...TIP, formatter: (p: any) => `${p.name}：${fmt(p.value)} 人<br/>该层实际流失率 ${tiers.value.find(t => t.name === p.name)?.churn_rate}%` },
  legend: { ...LEG, bottom: 0, left: 'center' },
  series: [{ type: 'pie', radius: ['54%', '76%'], center: ['50%', '44%'], itemStyle: { borderColor: 'rgba(10,14,39,.9)', borderWidth: 2 },
    label: { color: 'rgba(238,240,255,.8)', fontSize: 11.5 },
    data: tiers.value.map(t => ({ value: t.count, name: t.name, itemStyle: { color: t.color } })) }],
}))
const factorOpt = computed(() => ({
  tooltip: TIP, grid: { left: 8, right: 22, top: 6, bottom: 0, containLabel: true },
  xAxis: { type: 'value', ...ax }, yAxis: { type: 'category', inverse: true, axisLabel: ax.axisLabel, axisLine: { show: false },
    data: importance.value.slice(0, 6).map(i => i.name) },
  series: [{ type: 'bar', barWidth: 12, data: importance.value.slice(0, 6).map(i => i.value),
    itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#F87171' }, { offset: 1, color: '#FBBF24' }] }, borderRadius: [0, 6, 6, 0] } }],
}))
</script>
<style scoped>
.uid { display: block; font-size: 11.5px; color: rgba(238,240,255,.45); margin-top: 2px; }
.advice { color: rgba(238,240,255,.72); font-size: 13px; }
.method-note { margin: 14px 2px 0; font-size: 12.5px; line-height: 1.65; color: rgba(238,240,255,.55); }
</style>
