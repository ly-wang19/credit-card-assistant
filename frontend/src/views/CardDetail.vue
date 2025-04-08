<template>
  <div class="card-detail-container">
    <el-card class="card-detail-card">
      <template #header>
        <div class="card-header">
          <h2>{{ card.bank_name }} - {{ card.card_name }}</h2>
        </div>
      </template>
      
      <div class="card-detail-content" v-if="card.id">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="卡片等级">
            {{ card.card_level }}
          </el-descriptions-item>
          <el-descriptions-item label="年费政策">
            {{ card.annual_fee || '暂无信息' }}
          </el-descriptions-item>
          <el-descriptions-item label="信用额度">
            {{ card.credit_limit || '暂无信息' }}
          </el-descriptions-item>
          <el-descriptions-item label="主要权益">
            {{ card.benefits || '暂无信息' }}
          </el-descriptions-item>
          <el-descriptions-item label="申请条件">
            {{ card.requirements || '暂无信息' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="card-actions">
          <el-button @click="goBack">返回列表</el-button>
        </div>
      </div>
      
      <el-empty v-else description="加载中..." />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cards as cardsApi } from '../api'

const route = useRoute()
const router = useRouter()
const card = ref({})

const fetchCardDetail = async () => {
  try {
    const response = await cardsApi.getDetail(route.params.id)
    card.value = response.data
  } catch (error) {
    console.error('获取信用卡详情失败:', error)
  }
}

const goBack = () => {
  router.push('/cards')
}

onMounted(() => {
  fetchCardDetail()
})
</script>

<style scoped>
.card-detail-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.card-detail-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  text-align: center;
}

.card-detail-content {
  padding: 20px;
}

.card-actions {
  margin-top: 20px;
  text-align: center;
}
</style> 