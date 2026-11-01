<template>
  <div class="page-head"><h1 class="page-title">数据管理</h1><p class="page-sub">数据从哪来，由你决定——游戏里导出的、社区里说的，都能在此安放。</p></div>
  <div class="grid" style="grid-template-columns: repeat(3, 1fr)">
    <div class="panel src" v-for="s in sources" :key="s.name">
      <div class="seg-top"><h3>{{ s.name }}</h3><span class="badge" :class="s.cls">{{ s.status }}</span></div>
      <p class="src-desc">{{ s.desc }}</p>
      <div class="src-meta"><span>最近同步 · {{ s.last }}</span><span>累计 {{ s.rows }} 条</span></div>
      <button class="btn-g" style="width: 100%">{{ s.action }}</button>
    </div>
  </div>
  <div class="grid" style="grid-template-columns: 1.5fr 1fr; margin-top: 18px">
    <div class="panel"><div class="p-head"><h3 class="p-title">同步任务</h3><span class="p-sub">重复导入不会重复入库（按 external_id 去重）</span></div>
      <table class="tbl"><thead><tr><th>任务</th><th>来源</th><th>导入</th><th>跳过重复</th><th>状态</th></tr></thead>
      <tbody><tr v-for="j in jobs" :key="j.name"><td><b>{{ j.name }}</b><span class="uid">{{ j.time }}</span></td><td>{{ j.src }}</td><td>{{ j.add }}</td><td>{{ j.skip }}</td>
        <td><span class="badge" :class="j.cls">{{ j.status }}</span></td></tr></tbody></table></div>
    <div class="panel"><div class="p-head"><h3 class="p-title">字段映射 · UIGF 示例</h3><span class="p-sub">外部字段 → 标准字段</span></div>
      <table class="tbl"><thead><tr><th>UIGF 字段</th><th>标准表字段</th></tr></thead>
      <tbody><tr v-for="m in maps" :key="m.a"><td><code>{{ m.a }}</code></td><td><code>{{ m.b }}</code></td></tr></tbody></table>
      <p class="safe">安全约定：authkey 约 1 天有效，只做一次性导入；凭证加密存储、不打日志、不用作其他用途。读不到全服大盘数据——那是发行方内网的事，这里不假装能读。</p></div>
  </div>
</template>
<script setup lang="ts">
const sources = [
  { name: '原神 · 抽卡记录 (UIGF)', status: '可导入', cls: 'b-green', desc: '从游戏祈愿历史导出的标准格式文件，一键入库', last: '今天 10:24', rows: '12,480', action: '导入 UIGF 文件' },
  { name: '星穹铁道 · 抽卡记录 (SRGF)', status: '可导入', cls: 'b-green', desc: '跃迁记录的标准导出格式，字段自动映射', last: '昨天 21:03', rows: '8,214', action: '导入 SRGF 文件' },
  { name: 'Enka · 角色展柜', status: '已连接', cls: 'b-blue', desc: '凭 UID 读取公开的角色展柜，补全角色与圣遗物', last: '今天 09:41', rows: '3,906', action: '按 UID 同步' },
  { name: 'HoYoLAB / 米游社', status: '已连接', cls: 'b-blue', desc: '经 genshin.py 读取账号公开数据与社区帖子', last: '今天 08:15', rows: '26,340', action: '立即同步' },
  { name: '评论与反馈文件', status: '可导入', cls: 'b-green', desc: 'TapTap / B站 / 应用商店评论导出的 CSV、Excel', last: '10/30 18:22', rows: '48,210', action: '导入 CSV / Excel' },
  { name: '自定义数据源', status: '待配置', cls: 'b-gray', desc: 'REST 接口或数据库直连，自己写一个适配器即可', last: '尚未同步', rows: '0', action: '新建适配器' },
]
const jobs = [
  { name: 'UIGF 导入 #1042', time: '今天 10:24', src: '原神 UIGF', add: '1,240', skip: '312', status: '成功', cls: 'b-green' },
  { name: '评论文件导入 #1041', time: '今天 09:58', src: 'CSV 文件', add: '3,214', skip: '0', status: '成功', cls: 'b-green' },
  { name: 'Enka 展柜同步 #1040', time: '今天 09:41', src: 'Enka', add: '86', skip: '12', status: '成功', cls: 'b-green' },
  { name: '米游社同步 #1039', time: '今天 08:15', src: 'HoYoLAB', add: '1,502', skip: '438', status: '部分成功', cls: 'b-amber' },
]
const maps = [
  { a: 'uid', b: 'player.external_uid' }, { a: 'item_id', b: 'gacha_log.item_id' },
  { a: 'gacha_type', b: 'gacha_log.banner_type' }, { a: 'time', b: 'gacha_log.pulled_at' },
  { a: 'id（祈愿记录）', b: 'gacha_log.external_id' },
]
</script>
<style scoped>
.seg-top { display: flex; justify-content: space-between; align-items: center; }
.seg-top h3 { margin: 0; font-size: 15.5px; font-weight: 800; }
.src-desc { font-size: 13px; line-height: 1.6; color: rgba(238,240,255,.68); margin: 10px 0 13px; min-height: 42px; }
.src-meta { display: flex; justify-content: space-between; font-size: 12px; color: rgba(238,240,255,.5); margin-bottom: 14px; }
.uid { display: block; font-size: 11.5px; color: rgba(238,240,255,.45); margin-top: 2px; }
code { font-size: 12.5px; color: #A5B4FC; }
.safe { margin: 14px 0 0; font-size: 12.5px; line-height: 1.7; color: rgba(238,240,255,.6); background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.25); padding: 11px 14px; border-radius: 12px; }
</style>
