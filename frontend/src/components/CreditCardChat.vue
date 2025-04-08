<template>
  <div class="credit-card-chat">
    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-content">
            {{ message.content }}
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="请输入您的问题..."
          @keyup.enter.ctrl="sendMessage"
        />
        <el-button
          type="primary"
          :loading="loading"
          @click="sendMessage"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

export default {
  name: 'CreditCardChat',
  setup() {
    const messages = ref([])
    const inputMessage = ref('')
    const loading = ref(false)
    const messagesContainer = ref(null)
    
    const scrollToBottom = async () => {
      await nextTick()
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }
    
    const sendMessage = async () => {
      if (!inputMessage.value.trim() || loading.value) return
      
      const userMessage = inputMessage.value.trim()
      inputMessage.value = ''
      
      messages.value.push({
        role: 'user',
        content: userMessage
      })
      
      await scrollToBottom()
      
      loading.value = true
      try {
        const response = await axios.post('/api/chat', {
          message: userMessage
        })
        
        messages.value.push({
          role: 'assistant',
          content: response.data.response
        })
      } catch (error) {
        console.error('发送消息失败:', error)
        messages.value.push({
          role: 'assistant',
          content: '抱歉，发生了一些错误，请稍后再试。'
        })
      } finally {
        loading.value = false
        await scrollToBottom()
      }
    }
    
    onMounted(() => {
      messages.value.push({
        role: 'assistant',
        content: '您好！我是信用卡智能助手，请问有什么可以帮您？'
      })
    })
    
    return {
      messages,
      inputMessage,
      loading,
      messagesContainer,
      sendMessage
    }
  }
}
</script>

<style scoped>
.credit-card-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  margin-bottom: 20px;
  background-color: white;
  border-radius: 8px;
}

.message {
  margin-bottom: 20px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message-content {
  padding: 10px 15px;
  border-radius: 8px;
  background-color: #f0f0f0;
}

.message.user .message-content {
  background-color: #409eff;
  color: white;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area .el-input {
  flex: 1;
}

.input-area .el-button {
  width: 100px;
}
</style> 