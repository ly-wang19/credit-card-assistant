<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="loading" class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
      <p class="mt-4 text-gray-600">加载中...</p>
    </div>
    
    <div v-else-if="error" class="text-center text-red-500">
      {{ error }}
    </div>
    
    <div v-else class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      <!-- 卡片头部 -->
      <div class="bg-gradient-to-r from-blue-500 to-blue-700 p-6 text-white">
        <h1 class="text-3xl font-bold">{{ card.name }}</h1>
        <p class="mt-2 text-lg">{{ card.bank }}</p>
        <p v-if="card.level" class="mt-1">等级：{{ card.level }}</p>
      </div>
      
      <!-- 卡片详情 -->
      <div class="p-6">
        <!-- 年费信息 -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-2">年费政策</h2>
          <p class="text-gray-600">{{ card.annual_fee || '暂无年费信息' }}</p>
        </div>
        
        <!-- 权益信息 -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-2">卡片权益</h2>
          <div v-if="Object.keys(card.benefits).length > 0" class="grid gap-4">
            <div v-for="(value, key) in card.benefits" :key="key" class="bg-gray-50 p-4 rounded">
              <h3 class="font-medium text-gray-800">{{ key }}</h3>
              <p class="mt-1 text-gray-600">{{ value }}</p>
            </div>
          </div>
          <p v-else class="text-gray-600">暂无权益信息</p>
        </div>
        
        <!-- 申请条件 -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-2">申请条件</h2>
          <div v-if="Object.keys(card.requirements).length > 0" class="grid gap-4">
            <div v-for="(value, key) in card.requirements" :key="key" class="bg-gray-50 p-4 rounded">
              <h3 class="font-medium text-gray-800">{{ key }}</h3>
              <p class="mt-1 text-gray-600">{{ value }}</p>
            </div>
          </div>
          <p v-else class="text-gray-600">暂无申请条件信息</p>
        </div>
        
        <!-- 积分规则 -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-2">积分规则</h2>
          <p class="text-gray-600">{{ card.points_rule || '暂无积分规则信息' }}</p>
        </div>
        
        <!-- 信用额度 -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-2">信用额度</h2>
          <p class="text-gray-600">{{ card.credit_limit || '暂无信用额度信息' }}</p>
        </div>
      </div>
      
      <!-- 底部按钮 -->
      <div class="px-6 py-4 bg-gray-50 border-t">
        <button @click="$router.push('/cards')" class="text-blue-500 hover:text-blue-700">
          返回信用卡列表
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { cards } from '../api'

const route = useRoute()
const card = ref(null)
const loading = ref(true)
const error = ref(null)

const fetchCardDetail = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await cards.getDetail(route.params.id)
    card.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || '获取信用卡详情失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCardDetail()
})
</script> 