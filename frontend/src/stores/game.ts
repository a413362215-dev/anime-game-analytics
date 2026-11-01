import { defineStore } from 'pinia'
// 当前查看的游戏：顶栏切换后，所有接了真实数据的页面统一跟着换
export const useGameStore = defineStore('game', {
  state: () => ({ game: (localStorage.getItem('game') || 'gi') as 'gi' | 'hsr' }),
  actions: { setGame(g: 'gi' | 'hsr') { this.game = g; localStorage.setItem('game', g) } },
})
