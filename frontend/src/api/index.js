import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api', // 修改为正确的API路径
  timeout: 10000, // 增加超时时间到10秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关API
export const auth = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', new URLSearchParams({
    username: data.username,
    password: data.password,
    grant_type: 'password'
  }).toString(), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }),
  getProfile: () => api.get('/auth/me')
}

// 信用卡相关API
export const cards = {
  getAll: () => api.get('/cards'),
  getDetail: (id) => api.get(`/cards/${id}`),
  compare: (ids) => api.post('/cards/compare', { card_ids: ids })
}

// 聊天相关API
export const chat = {
  sendMessage: (message) => api.post('/chat', { message }),
  getHistory: () => api.get('/chat/history')
}

export default api 