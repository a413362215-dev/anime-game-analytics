<template>
  <div class="page-head"><h1 class="page-title">玩家分群</h1><p class="page-sub">众生百态，各有归处——把人分好组，才知道对谁说什么话。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel seg" v-for="g in groups" :key="g.key">
      <div class="seg-top"><h3>{{ g.name }}</h3><span class="badge" :class="g.cls">{{ g.share }}%</span></div>
      <p class="seg-count">{{ fmt(g.count) }} <span>人</span></p>
      <p class="seg-desc">{{ g.desc }}</p>
      <div class="seg-bar"><span>付费率 {{ g.pay_rate }}%</span><div class="bar-track"><div class="bar-fill" :style="{ width: g.pay_rate + '%' }"></div></div></div>
    </div>
  </div>
  <div class="grid" style="grid-template-columns: 1.2fr 1.8fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">人群画像 · RFM 散点</h3><span class="p-sub">横轴近度（越右越近）· 纵轴活跃频次 · 点大小为累计消费</span></div>
      <ChartBox :option="scatterOpt" :height="300" />
      <p class="km-note" v-if="kmeans">K-Means 交叉验证（k=4，轮廓系数 {{ kmeans.silhouette }}）：{{ kmeans.clusters.map((c: any) => `${c.name} ${fmt(c.count)} 人`).join(' · ') }}——规则分群与算法聚类大体重合，分组不是拍脑袋。</p></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">分组明细</h3><span class="p-sub">RFM 规则 8 类（R 近度 / F 活跃频次 / M 金额带）· 快照 {{ runDate }}</span></div>
      <table class="tbl"><thead><tr><th>分组</th><th>人数</th><th>人均近 30 天付费</th><th>人均累计消费</th><th>运营建议</th></tr></thead>
      <tbody><tr v-for="g in groups" :key="g.key"><td><b>{{ g.name }}</b></td><td>{{ fmt(g.count) }}</td><td>¥{{ fmt(g.avg_monetary_30d) }}</td><td>¥{{ fmt(g.avg_spend) }}</td><td class="advice">{{ g.advice }}</td></tr></tbody></table>
      <p class="km-note">口径：R 取近度天数，F 为近 30 天会话天数（样本）+ 付费次数（全量），M 为 180 天累计消费金额带。沉睡过半是注册基数的真实形状——六个月里大多数人来了又走。</p></div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import request from '../api/request'
import { useGameStore } from '../stores/game'
import { ax, TIP, PALETTE, fmt } from '../mock/data'

const groups = ref<any[]>([])
const scatter = ref<Record<string, number[][]>>({})
const kmeans = ref<any>(null)
const runDate = ref('')
const gameStore = useGameStore()
async function load() {
  try {
    const { data } = await request.get('/analytics/segments', { params: { game: gameStore.game } })
    if (data.error) return
    groups.value = data.groups; scatter.value = data.scatter
    kmeans.value = data.kmeans; runDate.value = data.run_date
  } catch { /* 后端离线时保持空态 */ }
}
onMounted(load)
watch(() => gameStore.game, load)

const scatterOpt = computed(() => ({
  tooltip: { ...TIP, trigger: 'item', formatter: (p: any) => `${p.seriesName}<br/>近度 ${p.value[0]} · 频次 ${p.value[1]} · 累计消费 ¥${p.value[2]}` },
  legend: { textStyle: { color: 'rgba(238,240,255,.75)', fontSize: 12 }, top: 0 },
  grid: { left: 8, right: 14, top: 34, bottom: 0, containLabel: true },
  xAxis: { type: 'value', name: 'R 近度', max: 180, ...ax }, yAxis: { type: 'value', name: 'F 频次', ...ax },
  series: Object.entries(scatter.value).map(([name, data], i) => ({
    name, type: 'scatter', data, itemStyle: { color: PALETTE[i % PALETTE.length], opacity: 0.75 },
    symbolSize: (v: number[]) => Math.min(6 + v[2] / 50, 26),
  })),
}))
</script>
<style scoped>
.seg-top { display: flex; justify-content: space-between; align-items: center; }
.seg-top h3 { margin: 0; font-size: 16.5px; font-weight: 800; }
.seg-count { font-size: 25px; font-weight: 800; margin: 12px 0 4px; font-variant-numeric: tabular-nums; }
.seg-count span { font-size: 13px; font-weight: 500; color: rgba(238,240,255,.55); }
.seg-desc { margin: 0 0 14px; font-size: 13px; color: rgba(238,240,255,.68); line-height: 1.55; min-height: 40px; }
.seg-bar span { font-size: 12px; color: rgba(238,240,255,.55); display: block; margin-bottom: 6px; }
.advice { color: rgba(238,240,255,.72); font-size: 13px; }
.km-note { margin: 12px 2px 0; font-size: 12.5px; line-height: 1.6; color: rgba(238,240,255,.55); }
</style>
