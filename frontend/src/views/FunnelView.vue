<template>
  <div class="page-head"><h1 class="page-title">行为漏斗</h1><p class="page-sub">新手的这一程，哪一站下车的人最多，就先修哪一站。</p></div>
  <div class="grid" style="grid-template-columns: 1.7fr 1fr">
    <div class="panel"><div class="p-head"><h3 class="p-title">新手期漏斗 · 近 30 日新玩家</h3><span class="p-sub">窗口内注册 {{ fmt(newPlayers) }} 人 · 事件流水口径</span></div>
      <div class="funnel">
        <div class="f-row" v-for="(s, i) in steps" :key="s.name">
          <div class="f-bar" :style="{ width: Math.max(s.pct, 24) + '%' }"><span class="f-name">{{ s.name }}</span><span class="f-num">{{ fmt(s.count) }}</span></div>
          <div class="f-conv" v-if="i < steps.length - 1">转化 {{ s.conv }}% <em v-if="s.drop">· 流失 {{ fmt(s.drop) }} 人</em></div>
        </div>
      </div>
      <div class="callout"><b>最大流失点：</b>「{{ biggest.from }} → {{ biggest.to }}」掉队 {{ fmt(biggest.count) }} 人（占新玩家 {{ biggest.share }}%），先修这一站；流失预警里有对应人群可跟。</div>
    </div>
    <div>
      <div class="panel"><div class="p-head"><h3 class="p-title">分渠道转化</h3><span class="p-sub">新增/完成为近 30 日 · 次日回访为全期样本</span></div>
        <table class="tbl"><thead><tr><th>渠道</th><th>新增</th><th>引导完成</th><th>次日回访</th></tr></thead>
        <tbody><tr v-for="c in channels" :key="c.name"><td><b>{{ c.name }}</b></td><td>{{ fmt(c.new) }}</td><td>{{ c.completion }}%</td>
          <td><span :class="(c.d1_sample ?? 0) >= 45 ? 'up' : 'down'">{{ c.d1_sample === null ? '样本不足' : c.d1_sample + '%' }}</span></td></tr></tbody></table></div>
      <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">与大盘对比</h3></div>
        <p class="cmp">近 30 日整体转化（走到主线章节）<b>{{ compare.now }}%</b>，上一个 30 日为 {{ compare.prev }}%，
          <span :class="compare.delta_pt >= 0 ? 'up' : 'down'">{{ compare.delta_pt >= 0 ? '+' : '' }}{{ compare.delta_pt }}pt</span>。
          口径：两期均为窗口内注册的新玩家，事件来自 fact_event_log。</p></div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import request from '../api/request'
import { useGameStore } from '../stores/game'
import { fmt } from '../mock/data'

// 后端离线时的占位（演示值），接口通了整体替换
const steps = ref<any[]>([
  { name: '首次启动', count: 1000000, pct: 100, conv: 91.2, drop: 88000 },
  { name: '创建角色', count: 912400, pct: 91, conv: 83.8, drop: 147900 },
  { name: '完成序章引导', count: 764300, pct: 76, conv: 68.2, drop: 242900 },
  { name: '通关第 4 关', count: 521400, pct: 52, conv: 74.6, drop: 132300 },
  { name: '完成首抽', count: 389100, pct: 39, conv: 89.8, drop: 39600 },
  { name: '进入主线章节', count: 349500, pct: 35, conv: null, drop: 0 },
])
const biggest = ref<any>({ from: '完成序章引导', to: '通关第 4 关', count: 242900, share: 24.3 })
const channels = ref<any[]>([
  { name: '官方渠道', new: 412600, completion: 47.2, d1_sample: 46.9, tracked: 0 },
  { name: 'Bilibili', new: 268300, completion: 44.8, d1_sample: 44.2, tracked: 0 },
  { name: 'TapTap', new: 157900, completion: 40.1, d1_sample: 39.8, tracked: 0 },
  { name: '应用商店', new: 161200, completion: 35.6, d1_sample: 33.5, tracked: 0 },
])
const compare = ref<any>({ now: 41.2, prev: 39.4, delta_pt: 1.8 })
const newPlayers = ref(0)

const gameStore = useGameStore()
async function load() {
  try {
    const { data } = await request.get('/analytics/funnel', { params: { game: gameStore.game, days: 30 } })
    if (data.error) return
    steps.value = data.steps; biggest.value = data.biggest_drop
    channels.value = data.channels; compare.value = data.compare
    newPlayers.value = data.new_players
  } catch { /* 保留演示值 */ }
}
onMounted(load)
watch(() => gameStore.game, load)
</script>
<style scoped>
.funnel { display: flex; flex-direction: column; gap: 5px; }
.f-bar { height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px;
  background: linear-gradient(90deg, rgba(96,165,250,.75), rgba(129,140,248,.75), rgba(232,121,249,.75)); min-width: 240px; }
.f-name { font-weight: 700; font-size: 14px; } .f-num { font-variant-numeric: tabular-nums; font-size: 13.5px; opacity: .92; }
.f-conv { font-size: 12px; color: rgba(238,240,255,.5); padding: 1px 4px 3px; } .f-conv em { font-style: normal; color: #FCA5A5; }
.callout { margin-top: 16px; padding: 13px 16px; border-radius: 13px; background: rgba(251,191,36,.1); border: 1px solid rgba(251,191,36,.3); font-size: 13.5px; line-height: 1.65; }
.cmp { font-size: 13.5px; line-height: 1.75; color: rgba(238,240,255,.78); margin: 0; }
</style>
