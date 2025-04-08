import { defineStore } from 'pinia'
import axios from 'axios'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    sessionId: null,
    isLoading: false,
    error: null
  }),
  
  actions: {
    async sendMessage(message) {
      this.isLoading = true
      this.error = null
      
      try {
        // 如果没有sessionId，生成一个新的
        if (!this.sessionId) {
          this.sessionId = Date.now().toString()
        }
        
        // 添加用户消息到历史记录
        this.messages.push({
          role: 'user',
          content: message,
          timestamp: new Date()
        })
        
        // 发送消息到后端
        const response = await axios.post('/api/v1/chat', {
          message,
          session_id: this.sessionId
        })
        
        // 添加助手回复到历史记录
        this.messages.push({
          role: 'assistant',
          content: response.data.message,
          timestamp: new Date()
        })
        
      } catch (error) {
        this.error = error.message
        console.error('发送消息失败:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    clearChat() {
      this.messages = []
      this.sessionId = null
      this.error = null
    }
  }
}) 