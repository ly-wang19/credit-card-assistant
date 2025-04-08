import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auth } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isAuthenticated = ref(false)

  // 初始化用户状态
  const initUser = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
      isAuthenticated.value = true
    }
  }

  // 登录
  const login = async (credentials) => {
    try {
      const response = await auth.login(credentials)
      const { access_token, user: userData } = response.data
      user.value = userData
      token.value = access_token
      isAuthenticated.value = true
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const response = await auth.getProfile()
      user.value = response.data
      isAuthenticated.value = true
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return false
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    initUser,
    login,
    logout,
    getUserInfo
  }
}) 