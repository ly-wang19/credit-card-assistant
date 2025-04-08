<template>
  <nav class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <router-link to="/" class="text-2xl font-bold text-primary-600">
              智慧金融科技
            </router-link>
          </div>
          <div class="hidden sm:ml-8 sm:flex sm:space-x-4">
            <router-link 
              v-for="item in navItems" 
              :key="item.path"
              :to="item.path"
              class="inline-flex items-center px-3 py-2 rounded-md text-sm font-medium"
              :class="[
                $route.path === item.path 
                  ? 'bg-primary-50 text-primary-700' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              ]"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <template v-if="isAuthenticated">
            <el-dropdown>
              <span class="flex items-center cursor-pointer hover:bg-gray-50 px-3 py-2 rounded-md">
                <el-avatar :size="32" class="mr-2">{{ userInitials }}</el-avatar>
                <span class="text-gray-700">{{ username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push('/profile')">
                    <i class="fas fa-user mr-2"></i>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleLogout">
                    <i class="fas fa-sign-out-alt mr-2"></i>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-secondary">登录</router-link>
            <router-link to="/register" class="btn-primary">注册</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 导航项
const navItems = [
  { name: '首页', path: '/' },
  { name: '信用卡列表', path: '/cards' },
  { name: 'AI助手', path: '/chat' },
  { name: '信用卡对比', path: '/compare' }
]

// 用户状态
const isAuthenticated = computed(() => userStore.isAuthenticated)
const username = computed(() => userStore.user?.username || '')
const userInitials = computed(() => {
  const name = userStore.user?.username || ''
  return name ? name.charAt(0).toUpperCase() : ''
})

// 处理退出登录
const handleLogout = async () => {
  userStore.logout()
  await router.push('/login')
}

// 监听路由变化，检查登录状态
watch(route, async () => {
  console.log('Route changed, checking auth state...')
  if (userStore.token && !userStore.user) {
    console.log('Token exists but no user data, fetching user info...')
    try {
      const success = await userStore.getUserInfo()
      console.log('User info fetch result:', success)
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      // 如果获取用户信息失败，可能是token过期
      userStore.logout()
      await router.push('/login')
    }
  }
})

// 初始化检查登录状态
userStore.initUser()
</script>

<style scoped>
.btn-primary {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500;
}

.btn-secondary {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500;
}
</style> 