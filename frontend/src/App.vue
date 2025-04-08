<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from './components/Navbar.vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

onMounted(async () => {
  console.log('App mounted, initializing user state...')
  userStore.initUser()
  
  if (userStore.token) {
    console.log('Token found, fetching user info...')
    try {
      const success = await userStore.getUserInfo()
      console.log('User info fetch result:', success)
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }
})
</script>

<style>
/* 自定义样式可以放在这里 */
</style> 