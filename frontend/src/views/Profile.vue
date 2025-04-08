<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 个人信息卡片 -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
        <div class="bg-primary-600 text-white p-6">
          <h1 class="text-2xl font-bold">个人中心</h1>
        </div>
        
        <div class="p-6">
          <!-- 头像上传 -->
          <div class="flex items-center mb-8">
            <div class="relative">
              <img 
                :src="profile.avatar_url || '/default-avatar.png'" 
                class="w-24 h-24 rounded-full object-cover"
                alt="头像"
              >
              <label 
                class="absolute bottom-0 right-0 bg-primary-600 text-white p-2 rounded-full cursor-pointer hover:bg-primary-700"
              >
                <i class="fas fa-camera"></i>
                <input 
                  type="file" 
                  class="hidden" 
                  accept="image/*"
                  @change="handleAvatarUpload"
                >
              </label>
            </div>
            <div class="ml-6">
              <h2 class="text-xl font-semibold">{{ profile.username }}</h2>
              <p class="text-gray-600">{{ profile.email }}</p>
            </div>
          </div>
          
          <!-- 个人信息表单 -->
          <form @submit.prevent="updateProfile" class="space-y-6">
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label class="block text-sm font-medium text-gray-700">用户名</label>
                <input 
                  v-model="profileForm.username" 
                  type="text"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">邮箱</label>
                <input 
                  v-model="profileForm.email" 
                  type="email"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">姓名</label>
                <input 
                  v-model="profileForm.full_name" 
                  type="text"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">手机号码</label>
                <input 
                  v-model="profileForm.phone" 
                  type="tel"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                >
              </div>
            </div>
            
            <div class="border-t border-gray-200 pt-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">修改密码</h3>
              <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label class="block text-sm font-medium text-gray-700">当前密码</label>
                  <input 
                    v-model="profileForm.current_password" 
                    type="password"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  >
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">新密码</label>
                  <input 
                    v-model="profileForm.new_password" 
                    type="password"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  >
                </div>
              </div>
            </div>
            
            <div class="flex justify-end">
              <button 
                type="submit"
                class="btn-primary"
                :disabled="loading"
              >
                <i class="fas fa-save mr-2"></i>
                保存修改
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 银行卡管理 -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="bg-primary-600 text-white p-6 flex justify-between items-center">
          <h2 class="text-xl font-bold">银行卡管理</h2>
          <button 
            class="btn-white"
            @click="showAddCardModal = true"
          >
            <i class="fas fa-plus mr-2"></i>
            添加银行卡
          </button>
        </div>
        
        <div class="p-6">
          <div v-if="cards.length === 0" class="text-center py-8 text-gray-500">
            暂无银行卡信息
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="card in cards" 
              :key="card.id"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center">
                <i class="fas fa-credit-card text-2xl text-primary-600"></i>
                <div class="ml-4">
                  <h3 class="font-medium">{{ card.bank_name }}</h3>
                  <p class="text-sm text-gray-600">
                    **** **** **** {{ card.card_number.slice(-4) }}
                  </p>
                </div>
              </div>
              
              <button 
                class="text-red-600 hover:text-red-800"
                @click="deleteCard(card.id)"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加银行卡弹窗 -->
    <el-dialog
      v-model="showAddCardModal"
      title="添加银行卡"
      width="500px"
    >
      <form @submit.prevent="addCard" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">银行名称</label>
          <input 
            v-model="cardForm.bank_name" 
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            required
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">卡号</label>
          <input 
            v-model="cardForm.card_number" 
            type="text"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            required
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">卡片类型</label>
          <select 
            v-model="cardForm.card_type"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            required
          >
            <option value="信用卡">信用卡</option>
            <option value="储蓄卡">储蓄卡</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">有效期</label>
          <el-date-picker
            v-model="cardForm.expiry_date"
            type="date"
            placeholder="选择有效期"
            format="YYYY-MM"
            value-format="YYYY-MM-DD"
            class="w-full"
            required
          />
        </div>
      </form>
      
      <template #footer>
        <div class="flex justify-end space-x-4">
          <button 
            class="btn-secondary"
            @click="showAddCardModal = false"
          >
            取消
          </button>
          <button 
            class="btn-primary"
            @click="addCard"
            :disabled="loading"
          >
            确认添加
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import api from '../api'

const userStore = useUserStore()
const loading = ref(false)
const showAddCardModal = ref(false)

// 个人信息
const profile = ref({})
const profileForm = ref({
  username: '',
  email: '',
  full_name: '',
  phone: '',
  current_password: '',
  new_password: ''
})

// 银行卡信息
const cards = ref([])
const cardForm = ref({
  bank_name: '',
  card_number: '',
  card_type: '信用卡',
  expiry_date: ''
})

// 获取个人信息
const fetchProfile = async () => {
  try {
    const response = await api.get('/profile')
    profile.value = response.data
    // 填充表单
    profileForm.value.username = response.data.username
    profileForm.value.email = response.data.email
    profileForm.value.full_name = response.data.full_name
    profileForm.value.phone = response.data.phone
  } catch (error) {
    console.error('获取个人信息失败:', error)
    ElMessage.error('获取个人信息失败')
  }
}

// 获取银行卡列表
const fetchCards = async () => {
  try {
    const response = await api.get('/cards')
    cards.value = response.data
  } catch (error) {
    console.error('获取银行卡列表失败:', error)
    ElMessage.error('获取银行卡列表失败')
  }
}

// 更新个人信息
const updateProfile = async () => {
  try {
    loading.value = true
    await api.put('/profile', profileForm.value)
    ElMessage.success('个人信息更新成功')
    // 清空密码字段
    profileForm.value.current_password = ''
    profileForm.value.new_password = ''
    // 重新获取个人信息
    await fetchProfile()
  } catch (error) {
    console.error('更新个人信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新个人信息失败')
  } finally {
    loading.value = false
  }
}

// 上传头像
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('file', file)
    
    await api.post('/profile/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    ElMessage.success('头像上传成功')
    await fetchProfile()
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('上传头像失败')
  } finally {
    loading.value = false
  }
}

// 添加银行卡
const addCard = async () => {
  try {
    loading.value = true
    await api.post('/cards', cardForm.value)
    ElMessage.success('银行卡添加成功')
    showAddCardModal.value = false
    // 重置表单
    cardForm.value = {
      bank_name: '',
      card_number: '',
      card_type: '信用卡',
      expiry_date: ''
    }
    // 重新获取银行卡列表
    await fetchCards()
  } catch (error) {
    console.error('添加银行卡失败:', error)
    ElMessage.error('添加银行卡失败')
  } finally {
    loading.value = false
  }
}

// 删除银行卡
const deleteCard = async (cardId) => {
  try {
    loading.value = true
    await api.delete(`/cards/${cardId}`)
    ElMessage.success('银行卡删除成功')
    // 重新获取银行卡列表
    await fetchCards()
  } catch (error) {
    console.error('删除银行卡失败:', error)
    ElMessage.error('删除银行卡失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!userStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  await Promise.all([
    fetchProfile(),
    fetchCards()
  ])
})
</script>

<style scoped>
.btn-primary {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-white {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-primary-700 bg-white hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white;
}
</style> 