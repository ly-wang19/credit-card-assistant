import axios from 'axios'

// 创建需要认证的API实例
const authApi = axios.create({
  baseURL: 'https://credit-card-assistant-api.onrender.com/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 创建公开API实例
const publicApi = axios.create({
  baseURL: 'https://credit-card-assistant-api.onrender.com/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 认证API的请求拦截器
authApi.interceptors.request.use(
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

// 认证API的响应拦截器
authApi.interceptors.response.use(
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
  register: (data) => authApi.post('/auth/register', data),
  login: (data) => authApi.post('/auth/login', new URLSearchParams({
    username: data.username,
    password: data.password,
    grant_type: 'password'
  }).toString(), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  }),
  getProfile: () => authApi.get('/auth/me')
}

// 信用卡相关API（使用认证API实例）
export const cards = {
  getAll: () => authApi.get('/cards'),
  getById: (id) => authApi.get(`/cards/${id}`),
  getDetail: (id) => authApi.get(`/cards/${id}`),
  compare: (ids) => authApi.post('/cards/compare', { card_ids: ids })
}

// 聊天相关API（需要认证）
export const chat = {
  sendMessage: (message) => authApi.post('/chat', { message }),
  getHistory: () => authApi.get('/chat/history'),
  newConversation: () => authApi.post('/chat/new'),
  clearHistory: () => authApi.delete('/chat/history'),
  deleteMessage: (messageId) => authApi.delete(`/chat/message/${messageId}`)
}

export default authApi 