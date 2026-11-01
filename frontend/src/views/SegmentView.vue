<template>
  <div class="page-head"><h1 class="page-title">玩家分群</h1><p class="page-sub">众生百态，各有归处——把人分好组，才知道对谁说什么话。</p></div>
  <div class="grid" style="grid-template-columns: repeat(4, 1fr)">
    <div class="panel seg" v-for="g in groups" :key="g.name">
      <div class="seg-top"><h3>{{ g.name }}</h3><span class="badge" :class="g.cls">{{ g.share }}</span></div>
      <p class="seg-count">{{ g.count }} <span>人</span></p>
      <p class="seg-desc">{{ g.desc }}</p>
      <div class="seg-bar"><span>付费率 {{ g.pay }}%</span><div class="bar-track"><div class="bar-fill" :style="{ width: g.pay + '%' }"></div></div></div>
    </div>
  </div>
  <div class="grid" style="grid-template-columns: 1.2fr 1.8fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">人群画像 · RFM 散点</h3><span class="p-sub">横轴近度 R · 纵轴频次 F · 点大小为金额 M</span></div>
      <ChartBox :option="scatterOpt" :height="300" /></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">分组明细</h3><span class="p-sub">RFM 五分位 8 类 + 行为标签</span></div>
      <table class="tbl"><thead><tr><th>分组</th><th>人数</th><th>人均月付费</th><th>次日留存</th><th>运营建议</th></tr></thead>
      <tbody><tr v-for="g in groups" :key="g.name"><td><b>{{ g.name }}</b></td><td>{{ g.count }}</td><td>¥{{ g.arppu }}</td><td>{{ g.ret }}%</td><td class="advice">{{ g.advice }}</td></tr></tbody></table></div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartBox from '../components/ChartBox.vue'
import { ax, TIP, PALETTE, rng } from '../mock/data'
const groups = [
  { name: '氪金大佬', count: '3,842', share: '3.0%', cls: 'b-amber', desc: '出手阔绰，新卡池首日必到场', pay: 96, arppu: 2860, ret: 88, advice: '新角色提前透出，专属客服跟进' },
  { name: '稳定中R', count: '11,205', share: '8.7%', cls: 'b-purple', desc: '每月预算固定，理性消费', pay: 82, arppu: 486, ret: 79, advice: '礼包性价比要算得清清楚楚' },
  { name: '月卡党', count: '34,716', share: '27.0%', cls: 'b-blue', desc: '细水长流，月卡从不断供', pay: 64, arppu: 68, ret: 76, advice: '月卡福利别缩水，断签提醒要温柔' },
  { name: '肝帝', count: '16,930', share: '13.2%', cls: 'b-green', desc: '在线时长拉满，体力永远不够', pay: 21, arppu: 42, ret: 81, advice: '给足挑战内容，他们是社区的火种' },
  { name: '剧情党', count: '19,884', share: '15.5%', cls: 'b-blue', desc: '为故事而来，版本主线必追', pay: 18, arppu: 36, ret: 69, advice: '剧情质量就是他们的留存' },
  { name: '收藏党', count: '9,468', share: '7.4%', cls: 'b-purple', desc: '图鉴洁癖，限定必收', pay: 57, arppu: 320, ret: 74, advice: '复刻排期提前公布，别让他们错过' },
  { name: '摇摆玩家', count: '21,307', share: '16.6%', cls: 'b-amber', desc: '来去随心，活动好就回来', pay: 24, arppu: 58, ret: 52, advice: '用回归活动和热点话题拉他们一把' },
  { name: '沉睡玩家', count: '11,188', share: '8.7%', cls: 'b-red', desc: '已 30 天未登录，多半已离站', pay: 9, arppu: 25, ret: 18, advice: '大版本节点发召回，附专属回归礼' },
]
const scatterOpt = computed(() => {
  const mk = (seed: number, cx: number, cy: number, n: number, color: string, name: string) => {
    const r = rng(seed); const data = Array.from({ length: n }, () => [Math.max(1, cx + (r() - 0.5) * 26), Math.max(1, cy + (r() - 0.5) * 22), 20 + r() * 260])
    return { name, type: 'scatter', data, itemStyle: { color, opacity: 0.75 }, symbolSize: (v: number[]) => 6 + v[2] / 22 }
  }
  return { tooltip: { ...TIP, trigger: 'item', formatter: (p: any) => `${p.seriesName}<br/>近度 ${p.value[0].toFixed(0)} · 频次 ${p.value[1].toFixed(0)} · 月付费 ¥${p.value[2].toFixed(0)}` },
    legend: { textStyle: { color: 'rgba(238,240,255,.75)', fontSize: 12 }, top: 0 },
    grid: { left: 8, right: 14, top: 34, bottom: 0, containLabel: true },
    xAxis: { type: 'value', name: 'R 近度', ...ax }, yAxis: { type: 'value', name: 'F 频次', ...ax },
    series: [ mk(3, 82, 78, 42, PALETTE[4], '价值人群'), mk(9, 55, 48, 60, PALETTE[0], '成长人群'), mk(15, 24, 20, 54, PALETTE[5], '风险人群') ] }
})
</script>
<style scoped>
.seg-top { display: flex; justify-content: space-between; align-items: center; }
.seg-top h3 { margin: 0; font-size: 16.5px; font-weight: 800; }
.seg-count { font-size: 25px; font-weight: 800; margin: 12px 0 4px; font-variant-numeric: tabular-nums; }
.seg-count span { font-size: 13px; font-weight: 500; color: rgba(238,240,255,.55); }
.seg-desc { margin: 0 0 14px; font-size: 13px; color: rgba(238,240,255,.68); line-height: 1.55; min-height: 40px; }
.seg-bar span { font-size: 12px; color: rgba(238,240,255,.55); display: block; margin-bottom: 6px; }
.advice { color: rgba(238,240,255,.72); font-size: 13px; }
</style>
