<template>
  <div class="min-h-[calc(100vh-4rem)] bg-gray-50 py-4 sm:py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
      <div class="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col h-[calc(100vh-8rem)]">
        <!-- 聊天头部 -->
        <div class="bg-primary-600 text-white p-4 sm:p-6">
          <div class="flex justify-between items-center">
            <h1 class="text-xl sm:text-2xl font-bold flex items-center">
              <i class="fas fa-robot mr-3"></i>
              AI信用卡助手
            </h1>
            <div class="flex items-center space-x-3">
              <button @click="newChat" class="btn-white-outline">
                <i class="fas fa-plus mr-2"></i>新对话
              </button>
              <el-dropdown trigger="click">
                <button class="btn-white-outline">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="clearHistory">
                      <i class="fas fa-trash mr-2"></i>清空历史
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          <p class="mt-2 text-primary-100 text-sm sm:text-base">我可以帮您推荐最适合的信用卡，解答相关问题</p>
        </div>

        <!-- 聊天记录 -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" 
               :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start']">
            <div :class="[
              'max-w-[85%] rounded-2xl p-3 sm:p-4 group relative',
              message.role === 'user' 
                ? 'bg-primary-600 text-white ml-4' 
                : 'bg-gray-100 text-gray-800 mr-4'
            ]">
              <div class="flex items-start space-x-3">
                <div v-if="message.role === 'assistant'" class="flex-shrink-0 mt-1">
                  <i class="fas fa-robot text-lg sm:text-xl text-primary-600"></i>
                </div>
                <div class="flex-1">
                  <p class="whitespace-pre-wrap text-sm sm:text-base leading-relaxed">{{ message.content }}</p>
                </div>
                <div v-if="message.role === 'user'" class="flex-shrink-0 mt-1">
                  <i class="fas fa-user text-lg sm:text-xl text-white"></i>
                </div>
              </div>
              <!-- 消息操作按钮 -->
              <div class="absolute top-2 right-2 hidden group-hover:flex space-x-2">
                <button @click="copyMessage(message.content)" 
                        class="p-1 rounded-full hover:bg-gray-200 text-gray-600">
                  <i class="fas fa-copy"></i>
                </button>
                <button @click="deleteMessage(index)"
                        class="p-1 rounded-full hover:bg-gray-200 text-gray-600">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loading" class="flex justify-start">
            <div class="bg-gray-100 rounded-2xl p-4 max-w-[85%] mr-4">
              <div class="flex items-center space-x-3">
                <i class="fas fa-robot text-xl text-primary-600"></i>
                <div class="flex space-x-2">
                  <div class="w-2.5 h-2.5 bg-primary-600 rounded-full animate-bounce"></div>
                  <div class="w-2.5 h-2.5 bg-primary-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-2.5 h-2.5 bg-primary-600 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="border-t border-gray-200 p-4">
          <form @submit.prevent="sendMessage" class="flex space-x-3">
            <div class="flex-1">
              <el-input
                v-model="userInput"
                type="textarea"
                :rows="2"
                :maxlength="500"
                show-word-limit
                resize="none"
                placeholder="请输入您的问题..."
                @keydown.enter.exact.prevent="sendMessage"
                class="custom-textarea"
              />
            </div>
            <button
              type="submit"
              class="btn-primary self-end px-6 h-10 transition-all duration-200"
              :class="{'opacity-50 cursor-not-allowed': loading || !userInput.trim()}"
              :disabled="loading || !userInput.trim()"
            >
              <i class="fas fa-paper-plane mr-2"></i>
              发送
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../stores/user'
import { chat } from '../api'

const router = useRouter()
const userStore = useUserStore()
const messages = ref([])
const userInput = ref('')
const loading = ref(false)
const chatContainer = ref(null)

// 检查登录状态
onMounted(() => {
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  // 添加欢迎消息
  messages.value.push({
    role: 'assistant',
    content: '您好！我是AI信用卡助手，我可以帮您：\n1. 推荐最适合您的信用卡\n2. 解答信用卡相关问题\n3. 对比不同信用卡的权益\n请告诉我您的需求。'
  })

  // 尝试加载历史消息
  loadChatHistory()
})

// 加载历史消息
const loadChatHistory = async () => {
  try {
    const response = await chat.getHistory()
    if (response.data && response.data.length > 0) {
      messages.value = [...messages.value, ...response.data]
      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载历史消息失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  if (!userInput.value.trim() || loading.value) return

  const userMessage = userInput.value.trim()
  messages.value.push({ role: 'user', content: userMessage })
  userInput.value = ''
  loading.value = true

  try {
    const response = await chat.sendMessage(userMessage)
    if (response.data && response.data.response) {
      messages.value.push({ 
        role: 'assistant', 
        content: response.data.response 
      })
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error(error.response?.data?.message || '发送消息失败，请稍后重试')
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 新建对话
const newChat = async () => {
  try {
    await ElMessageBox.confirm('是否开始新的对话？当前对话将被保存。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    messages.value = [{
      role: 'assistant',
      content: '您好！我是AI信用卡助手，我可以帮您：\n1. 推荐最适合您的信用卡\n2. 解答信用卡相关问题\n3. 对比不同信用卡的权益\n请告诉我您的需求。'
    }]
    await chat.newConversation()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('创建新对话失败')
    }
  }
}

// 清空历史
const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有聊天记录吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await chat.clearHistory()
    messages.value = [{
      role: 'assistant',
      content: '您好！我是AI信用卡助手，我可以帮您：\n1. 推荐最适合您的信用卡\n2. 解答信用卡相关问题\n3. 对比不同信用卡的权益\n请告诉我您的需求。'
    }]
    ElMessage.success('历史记录已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空历史记录失败')
    }
  }
}

// 复制消息内容
const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 删除单条消息
const deleteMessage = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const messageId = messages.value[index].id
    if (messageId) {
      await chat.deleteMessage(messageId)
    }
    messages.value.splice(index, 1)
    ElMessage.success('消息已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除消息失败')
    }
  }
}
</script>

<style scoped>
.custom-textarea :deep(.el-textarea__inner) {
  @apply rounded-lg border-gray-300 focus:border-primary-500 focus:ring-primary-500;
  resize: none;
}

.btn-primary {
  @apply inline-flex items-center justify-center rounded-lg bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.animate-bounce {
  animation: bounce 1s infinite;
}

.btn-white-outline {
  @apply px-3 py-1.5 rounded-lg border border-white text-white hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50 transition-colors duration-200 text-sm flex items-center;
}
</style> 