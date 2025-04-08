<template>
  <div class="min-h-screen bg-gray-100 flex flex-col justify-start py-8 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-4 text-center text-3xl font-extrabold text-gray-900">登录您的账户</h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        或者
        <router-link to="/register" class="font-medium text-indigo-600 hover:text-indigo-500">
          注册新账户
        </router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">邮箱地址</label>
            <div class="mt-1">
              <input 
                id="email" 
                v-model="email" 
                type="email" 
                required
                autocomplete="email"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">密码</label>
            <div class="mt-1">
              <input 
                id="password" 
                v-model="password" 
                type="password" 
                required
                autocomplete="current-password"
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input 
                id="remember-me" 
                v-model="rememberMe" 
                type="checkbox"
                class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
              <label for="remember-me" class="ml-2 block text-sm text-gray-900">记住我</label>
            </div>
          </div>

          <div>
            <button 
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const email = ref('')
    const password = ref('')
    const rememberMe = ref(false)
    const loading = ref(false)

    const handleLogin = async () => {
      if (loading.value) return
      loading.value = true
      
      try {
        const success = await userStore.login({
          username: email.value,
          password: password.value
        })
        
        if (success) {
          if (rememberMe.value) {
            localStorage.setItem('email', email.value)
          }
          
          const userInfoSuccess = await userStore.getUserInfo()
          if (!userInfoSuccess) {
            ElMessage.warning('登录成功但获取用户信息失败，请刷新页面重试')
          }
          
          ElMessage.success('登录成功')
          // 确保在路由跳转前等待一下状态更新
          await new Promise(resolve => setTimeout(resolve, 100))
          await router.push('/chat')
        } else {
          ElMessage.error('登录失败：用户名或密码错误')
        }
      } catch (error) {
        console.error('Login error:', error)
        if (error.response?.status === 401) {
          ElMessage.error('用户名或密码错误')
        } else {
          ElMessage.error(error.response?.data?.detail || '登录失败：服务器错误')
        }
      } finally {
        loading.value = false
      }
    }

    return {
      email,
      password,
      rememberMe,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 60px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  margin-top: 20px;
  background-color: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.login-form {
  margin-top: 20px;
}

.login-form-item {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  margin-top: 20px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #606266;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
}

.register-link a:hover {
  color: #66b1ff;
}
</style> 