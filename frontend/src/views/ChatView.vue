<template>
  <div class="page-head"><h1 class="page-title">LLM 智能助手</h1><p class="page-sub">有事，问它便好——每个数字都先去库里查过，句句有出处。</p></div>
  <div class="grid chat-grid" style="grid-template-columns: 260px 1fr">
    <div class="panel sessions">
      <div class="p-head"><h3 class="p-title">历史会话</h3></div>
      <div class="sess" v-for="(s, i) in sessions" :key="s" :class="{ on: i === 0 }">{{ s }}</div>
      <button class="btn-g" style="width: 100%; margin-top: 12px">+ 新建会话</button>
      <p class="sess-note">助手能做的事：查数（ChatBI）、翻文档（RAG）、照着数据写总结。不会的事：编数字——查不到它会直说。</p>
    </div>
    <div class="panel convo">
      <div class="msgs" ref="msgBox">
        <div v-for="(m, i) in msgs" :key="i" :class="['msg', m.role]">
          <div class="bubble">
            <p v-for="(line, j) in m.text.split('\n')" :key="j">{{ line }}</p>
            <div class="tool-card" v-if="m.tool">
              <div class="tool-head"><span class="badge b-blue">工具调用</span><code>{{ m.tool.name }}</code></div>
              <p class="tool-body">{{ m.tool.detail }}</p>
            </div>
            <div class="cites" v-if="m.cites"><span class="chip-tag" v-for="c in m.cites" :key="c">出处 · {{ c }}</span></div>
          </div>
        </div>
      </div>
      <div class="suggest">
        <button class="chip-tag q" v-for="q in suggestions" :key="q" @click="ask(q)">{{ q }}</button>
      </div>
      <div class="composer">
        <input v-model="input" placeholder="问点什么，比如：上周哪个卡池卖得最好？" @keyup.enter="ask(input)" />
        <button class="btn-p" @click="ask(input)">发送</button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick } from 'vue'
interface Msg { role: 'user' | 'ai'; text: string; tool?: { name: string; detail: string }; cites?: string[] }
const sessions = ['5.2 版本口碑总结', '高风险玩家名单解读', '国庆活动复盘', '新卡池收入对比', '新手漏斗怎么了']
const suggestions = ['今天活跃怎么样？', '谁最可能流失？', '把 5.2 版本总结成一段话', '哪个卡池卖得最好？']
const msgs = ref<Msg[]>([
  { role: 'user', text: '把 5.2 版本总结成一段话' },
  { role: 'ai', text: '5.2「流光拾遗之旅」上线 30 天，整体好评率 68.4%，较 5.1 提升 5.2 个百分点。剧情是最受夸奖的部分（方面级好评 86%），其次是角色与美术音乐；主要槽点集中在体力恢复速度与联机掉线。活跃与流水在版本首周冲高后回落到高于 5.1 同期的水平，限定池「月下拾光」为版本收入第一。\n一句话：内容赢了口碑，体力拖了后腿。',
    tool: { name: 'get_version_feedback(version="5.2") + get_daily_kpi(range="30d")', detail: '情感与话题来自 feedback_analysis · 活跃与流水来自 agg_daily_kpi，均为今日凌晨的例行计算结果' },
    cites: ['版本反馈页 · 方面级情感', '总览看板 · 近 30 日'] },
])
const input = ref('')
const msgBox = ref<HTMLElement>()
function scroll() { nextTick(() => { if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight }) }
function answer(q: string): Msg {
  if (/活跃|多少人|DAU/i.test(q)) return { role: 'ai', text: '今天活跃玩家 128,540，较昨日 +4.2%。新增 8,642 人，是近两周最高——新版本预热的短视频投放带来的量，主要落在官方渠道与 Bilibili。晚间 20 点还有一波高峰没到，预计全天能到 13.6 万上下。', tool: { name: 'query_daily_kpi(date="today")', detail: 'agg_daily_kpi · 今日行，更新时间 23:00' }, cites: ['总览看板'] }
  if (/流失|走/.test(q)) return { role: 'ai', text: '当前高风险玩家 12,483 人，中风险 38,210 人。高风险里最常见的原因是「距上次登录天数」变长和「周活跃时长下降」，占一半以上。名单前列有几位氪金大佬（比如「夜樱未眠」，9 天未登录），建议先由专属客服轻轻问候一句，别一上来就发礼包。', tool: { name: 'get_churn_list(risk="high", limit=50)', detail: 'churn_prediction · 今晨例行更新，模型版本 v12' }, cites: ['流失预警页'] }
  if (/卡池|卖得最好|抽卡/.test(q)) return { role: 'ai', text: '本版本卖得最好的是限定池「月下拾光」：累计 286 万抽、收入 ¥486 万，排第二的「星海巡航」是 214 万抽。整体平均 54.2 抽出一个五星，歪率 46.3%，都在公示概率的正常范围内。', tool: { name: 'get_gacha_stats(version="5.2")', detail: 'gacha_log + payment_order 汇总，今日凌晨计算' }, cites: ['付费与抽卡页'] }
  if (/总结|版本/.test(q)) return { role: 'ai', text: '5.2 版本一句话：剧情封神、优化给力、体力挨骂。好评率 68.4%（+5.2pt），流水由「月下拾光」领跑；如果下个版本只改一件事，先改体力恢复速度——它是差评里占比 31% 的第一名。', tool: { name: 'get_version_feedback(version="5.2")', detail: 'feedback_analysis · 48,210 条评价' }, cites: ['版本反馈页'] }
  return { role: 'ai', text: '这个问题我先记下了。演示阶段我只接了四个话题：活跃、流失、卡池、版本总结——点下面的快捷问题就能看到我查数的全过程（包括工具调用记录）。接上真实模型与数据层后，问题就不受这个限制了。' }
}
function ask(q: string) {
  const text = (q || '').trim(); if (!text) return
  msgs.value.push({ role: 'user', text }); input.value = ''; scroll()
  setTimeout(() => { msgs.value.push(answer(text)); scroll() }, 420)
}
</script>
<style scoped>
.chat-grid { align-items: start; }
.sessions .sess { padding: 10px 13px; border-radius: 12px; font-size: 13.5px; color: rgba(238,240,255,.75); cursor: pointer; margin-bottom: 4px; }
.sessions .sess:hover { background: rgba(255,255,255,.06); }
.sessions .sess.on { background: rgba(129,140,248,.18); color: #fff; font-weight: 600; }
.sess-note { font-size: 12.5px; line-height: 1.75; color: rgba(238,240,255,.55); margin: 14px 2px 0; }
.convo { display: flex; flex-direction: column; height: calc(100vh - 178px); min-height: 480px; }
.msgs { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; padding-right: 6px; }
.msg { display: flex; } .msg.user { justify-content: flex-end; }
.bubble { max-width: 76%; padding: 13px 16px; border-radius: 17px; font-size: 14px; line-height: 1.75; }
.msg.user .bubble { background: linear-gradient(135deg, #60A5FA, #818CF8 55%, #E879F9); color: #fff; border-bottom-right-radius: 6px; }
.msg.ai .bubble { background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.12); border-bottom-left-radius: 6px; }
.bubble p { margin: 0 0 6px; } .bubble p:last-child { margin-bottom: 0; }
.tool-card { margin-top: 10px; background: rgba(10,14,39,.45); border: 1px solid rgba(96,165,250,.3); border-radius: 12px; padding: 10px 13px; }
.tool-head { display: flex; align-items: center; gap: 9px; } .tool-head code { font-size: 12px; color: #93C5FD; }
.tool-body { font-size: 12px !important; color: rgba(238,240,255,.6); margin-top: 6px !important; }
.cites { display: flex; gap: 7px; margin-top: 10px; flex-wrap: wrap; }
.suggest { display: flex; gap: 8px; flex-wrap: wrap; padding: 13px 0 11px; border-top: 1px solid rgba(255,255,255,.09); margin-top: 13px; }
.chip-tag.q { cursor: pointer; font-family: inherit; } .chip-tag.q:hover { border-color: rgba(165,180,252,.6); color: #fff; }
.composer { display: flex; gap: 10px; }
.composer input { flex: 1; height: 46px; border-radius: 999px; border: 1px solid rgba(255,255,255,.22); background: rgba(255,255,255,.07);
  color: #fff; padding: 0 19px; font-size: 14px; font-family: inherit; outline: none; }
.composer input:focus { border-color: rgba(165,180,252,.7); }
.composer .btn-p { padding: 0 26px; }
</style>
