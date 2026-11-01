<template>
  <div class="page-head"><h1 class="page-title">行为漏斗</h1><p class="page-sub">新手的这一程，哪一站下车的人最多，就先修哪一站。</p></div>
  <div class="grid" style="grid-template-columns: 1.7fr 1fr">
    <div class="panel"><div class="p-head"><h3 class="p-title">新手期漏斗 · 近 7 日新玩家</h3><span class="p-sub">从首次启动到次日回访</span></div>
      <div class="funnel">
        <div class="f-row" v-for="(s, i) in steps" :key="s.name">
          <div class="f-bar" :style="{ width: s.pct + '%' }"><span class="f-name">{{ s.name }}</span><span class="f-num">{{ s.count }}</span></div>
          <div class="f-conv" v-if="i < steps.length - 1">转化 {{ s.conv }}% <em v-if="s.drop">· 流失 {{ s.drop }} 人</em></div>
        </div>
      </div>
      <div class="callout"><b>最大流失点：</b>「完成新手引导 → 通关首个秘境」掉队 24.3 万人，第 4 关 BOSS 难度是主因，流失预警里已有对应人群。</div>
    </div>
    <div>
      <div class="panel"><div class="p-head"><h3 class="p-title">分渠道转化</h3><span class="p-sub">次日回访率</span></div>
        <table class="tbl"><thead><tr><th>渠道</th><th>新增</th><th>次日回访</th></tr></thead>
        <tbody><tr v-for="c in channels" :key="c.name"><td><b>{{ c.name }}</b></td><td>{{ c.new }}</td><td><span :class="c.good ? 'up' : 'down'">{{ c.ret }}%</span></td></tr></tbody></table></div>
      <div class="panel" style="margin-top: 18px"><div class="p-head"><h3 class="p-title">与大盘对比</h3></div>
        <p class="cmp">本期整体转化 <b>41.2%</b>，高于上期 <span class="up">+1.8pt</span>；主要进步来自新手引导时长缩短 40 秒（见 A/B 实验「新手礼包改版」同批改动）。</p></div>
    </div>
  </div>
</template>
<script setup lang="ts">
const steps = [
  { name: '首次启动', count: '1,000,000', pct: 100, conv: 91.2, drop: '88,000' },
  { name: '创建角色', count: '912,400', pct: 91, conv: 83.8, drop: '147,900' },
  { name: '完成新手引导', count: '764,300', pct: 76, conv: 68.2, drop: '242,900' },
  { name: '通关首个秘境', count: '521,400', pct: 52, conv: 74.6, drop: '132,300' },
  { name: '在线满 30 分钟', count: '389,100', pct: 39, conv: 24.9, drop: '292,300' },
  { name: '完成首次付费', count: '96,800', pct: 19, conv: null, drop: '' },
]
const channels = [
  { name: '官方渠道', new: '412,600', ret: 46.9, good: true },
  { name: 'Bilibili', new: '268,300', ret: 44.2, good: true },
  { name: 'TapTap', new: '157,900', ret: 39.8, good: true },
  { name: '应用商店', new: '161,200', ret: 33.5, good: false },
]
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
