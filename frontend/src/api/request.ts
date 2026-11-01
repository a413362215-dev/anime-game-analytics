import axios from 'axios'
const request = axios.create({ baseURL: '/api', timeout: 15000 })
request.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
request.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) { localStorage.removeItem('token'); location.href = '/login' }
  return Promise.reject(err)
})
export default request
