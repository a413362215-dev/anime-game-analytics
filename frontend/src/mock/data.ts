// 演示数据（前端 mock）：数值均为演示用，阶段 2 接入真实数据层后替换
export const PALETTE = ['#818CF8', '#E879F9', '#60A5FA', '#34D399', '#FBBF24', '#F87171', '#A5B4FC', '#F0ABFC']
export function rng(seed: number) { let a = seed; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296 } }
export const DAYS: string[] = Array.from({ length: 30 }, (_, i) => { const d = new Date(2026, 9, 3 + i); return `${d.getMonth() + 1}/${d.getDate()}` })
export function series(base: number, amp: number, seed: number, weekendBoost = 0.22): number[] {
  const r = rng(seed); return DAYS.map((_, i) => { const wk = (i % 7 === 5 || i % 7 === 6) ? 1 + weekendBoost : 1; const v = base * (1 + Math.sin(i / 4.6) * amp * 0.5 + (r() - 0.5) * amp) * wk; return Math.round(v) })
}
export const ax = {
  axisLabel: { color: 'rgba(238,240,255,.55)', fontSize: 11.5 },
  axisLine: { lineStyle: { color: 'rgba(255,255,255,.14)' } },
  splitLine: { lineStyle: { color: 'rgba(255,255,255,.07)' } },
}
export const TIP = { trigger: 'axis', backgroundColor: 'rgba(13,17,40,.92)', borderColor: 'rgba(255,255,255,.18)', textStyle: { color: '#EEF0FF', fontSize: 12.5 } }
export const LEG = { textStyle: { color: 'rgba(238,240,255,.75)', fontSize: 12 }, icon: 'roundRect', itemWidth: 14, itemHeight: 4 }
export const fmt = (n: number) => n.toLocaleString('zh-CN')
