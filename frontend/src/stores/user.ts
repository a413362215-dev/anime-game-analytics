import { defineStore } from 'pinia'
import request from '../api/request'
export const useUserStore = defineStore('user', {
  state: () => ({ username: localStorage.getItem('username') || '', role: localStorage.getItem('role') || '' }),
  actions: {
    async login(username: string, password: string) {
      const { data } = await request.post('/auth/login', { username, password })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('role', data.role)
      this.username = data.username; this.role = data.role
    },
    logout() { localStorage.clear(); this.username = ''; this.role = '' }
  }
})
