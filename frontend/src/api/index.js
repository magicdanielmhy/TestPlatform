import axios from 'axios'

const api = axios.create({ baseURL: '', timeout: 20000 })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response && err.response.status
    const isLogin = err.config && String(err.config.url).includes('/api/auth/login')
    if (status === 401 && !isLogin) {
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
