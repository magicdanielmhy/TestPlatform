import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('token') || '' }),
  actions: {
    async login(username, password) {
      const { data } = await api.post('/api/auth/login', { username, password })
      this.token = data.access_token
      localStorage.setItem('token', data.access_token)
    },
    logout() {
      this.token = ''
      localStorage.removeItem('token')
    }
  }
})
