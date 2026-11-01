import { defineStore } from 'pinia'
import request from '../api/request'
export const useUserStore = defineStore('user', {
  state: () => ({ username: localStorage.getItem('username') || '', role: localStorage.getItem('role') || '' }),
  actions: {
    setSession(data: any) {
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('role', data.role)
      this.username = data.username; this.role = data.role
    },
    async login(username: string, password: string) {
      const { data } = await request.post('/auth/login', { username, password })
      this.setSession(data)
    },
    async register(username: string, password: string, phone: string, code: string) {
      const { data } = await request.post('/auth/register', { username, password, phone, code })
      this.setSession(data)
    },
    async smsLogin(phone: string, code: string) {
      const { data } = await request.post('/auth/sms/login', { phone, code })
      this.setSession(data)
    },
    logout() { localStorage.clear(); this.username = ''; this.role = '' }
  }
})
