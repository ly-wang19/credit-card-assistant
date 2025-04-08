<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-8 text-center">信用卡对比</h1>
      
      <!-- 选择要对比的信用卡 -->
      <div class="bg-white rounded-lg shadow-lg p-8 mb-8 transform hover:shadow-xl transition-shadow duration-300">
        <h2 class="text-2xl font-semibold mb-6 text-center">选择要对比的信用卡</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">第一张信用卡</label>
            <el-select 
              v-model="selectedCards[0]" 
              class="w-full" 
              placeholder="请选择信用卡"
              :popper-class="'select-dropdown'"
            >
              <el-option
                v-for="card in cardsList"
                :key="`${card.bank}-${card.name}`"
                :label="`${card.bank} - ${card.name}`"
                :value="`${card.bank}-${card.name}`"
              >
                <div class="flex items-center">
                  <span class="text-primary-600 font-medium">{{ card.bank }}</span>
                  <span class="ml-2 text-gray-600">{{ card.name }}</span>
                </div>
              </el-option>
            </el-select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">第二张信用卡</label>
            <el-select 
              v-model="selectedCards[1]" 
              class="w-full" 
              placeholder="请选择信用卡"
              :popper-class="'select-dropdown'"
            >
              <el-option
                v-for="card in cardsList"
                :key="`${card.bank}-${card.name}`"
                :label="`${card.bank} - ${card.name}`"
                :value="`${card.bank}-${card.name}`"
              >
                <div class="flex items-center">
                  <span class="text-primary-600 font-medium">{{ card.bank }}</span>
                  <span class="ml-2 text-gray-600">{{ card.name }}</span>
                </div>
              </el-option>
            </el-select>
          </div>
        </div>
      </div>

      <!-- 对比结果 -->
      <div v-if="showComparison" class="bg-white rounded-lg shadow-lg overflow-hidden transform hover:shadow-xl transition-shadow duration-300">
        <div class="grid grid-cols-3 gap-4 p-8 bg-gray-50">
          <div class="text-center">
            <h3 class="text-xl font-semibold mb-2 text-primary-600">{{ getCardInfo(selectedCards[0]).bank }}</h3>
            <p class="text-gray-600">{{ getCardInfo(selectedCards[0]).name }}</p>
          </div>
          <div class="text-center text-gray-500 font-medium">对比项</div>
          <div class="text-center">
            <h3 class="text-xl font-semibold mb-2 text-primary-600">{{ getCardInfo(selectedCards[1]).bank }}</h3>
            <p class="text-gray-600">{{ getCardInfo(selectedCards[1]).name }}</p>
          </div>
        </div>

        <div class="divide-y divide-gray-200">
          <div v-for="(item, index) in comparisonItems" :key="index" 
               class="grid grid-cols-3 gap-4 p-6 hover:bg-gray-50 transition-colors duration-200">
            <div class="text-right font-medium">{{ item.value1 }}</div>
            <div class="text-center text-gray-500 font-medium">{{ item.label }}</div>
            <div class="text-left font-medium">{{ item.value2 }}</div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="bg-white rounded-lg shadow-lg p-12 text-center transform hover:shadow-xl transition-shadow duration-300">
        <el-empty description="请选择两张信用卡进行对比">
          <template #image>
            <i class="fas fa-balance-scale text-6xl text-gray-300"></i>
          </template>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { cards as cardsApi } from '../api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const cardsList = ref([])
const selectedCards = ref([null, null])
const loading = ref(false)
const router = useRouter()

// 获取所有信用卡列表
const fetchCards = async () => {
  loading.value = true
  try {
    console.log('开始获取信用卡列表')
    // 创建一个数组存储所有的Promise
    const promises = []
    // 根据数据库中的卡片数量，遍历获取每张卡片
    for (let i = 1; i <= 8; i++) {
      promises.push(
        cardsApi.getDetail(i).catch(error => {
          console.log(`获取卡片${i}失败:`, error)
          return { data: null } // 返回空数据而不是抛出错误
        })
      )
    }
    
    // 并行获取所有卡片信息
    const responses = await Promise.all(promises)
    // 过滤掉失败的请求，只保留成功的数据
    cardsList.value = responses
      .filter(response => response.data)
      .map(response => response.data)
    
    console.log('成功获取信用卡列表:', cardsList.value)
  } catch (error) {
    console.error('获取信用卡列表失败:', error)
    if (error.response?.status === 401) {
      ElMessage.error('请先登录')
      router.push('/login')
    } else {
      ElMessage.error('获取信用卡列表失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 获取卡片信息
const getCardInfo = (cardValue) => {
  if (!cardValue) return {}
  const [bank, name] = cardValue.split('-')
  const card = cardsList.value.find(card => card.bank === bank && card.name === name)
  return card || {}
}

// 对比项
const comparisonItems = computed(() => {
  if (!selectedCards.value[0] || !selectedCards.value[1]) return []

  const card1 = getCardInfo(selectedCards.value[0])
  const card2 = getCardInfo(selectedCards.value[1])

  if (!card1 || !card2) return []

  return [
    { label: '卡片等级', value1: card1.level || '暂无信息', value2: card2.level || '暂无信息' },
    { label: '年费', value1: card1.annual_fee || '暂无信息', value2: card2.annual_fee || '暂无信息' },
    { label: '信用额度', value1: card1.credit_limit || '暂无信息', value2: card2.credit_limit || '暂无信息' },
    { label: '积分规则', value1: card1.points_rule || '暂无信息', value2: card2.points_rule || '暂无信息' },
    { label: '主要权益', value1: formatBenefits(card1.benefits), value2: formatBenefits(card2.benefits) },
    { label: '申请条件', value1: formatRequirements(card1.requirements), value2: formatRequirements(card2.requirements) }
  ]
})

// 格式化权益信息
const formatBenefits = (benefits) => {
  if (!benefits) return '暂无信息'
  if (typeof benefits === 'string') return benefits
  if (typeof benefits === 'object') {
    return Object.entries(benefits)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ')
  }
  return '暂无信息'
}

// 格式化申请条件
const formatRequirements = (requirements) => {
  if (!requirements) return '暂无信息'
  if (typeof requirements === 'string') return requirements
  if (typeof requirements === 'object') {
    return Object.entries(requirements)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ')
  }
  return '暂无信息'
}

// 是否显示对比结果
const showComparison = computed(() => {
  return selectedCards.value[0] && selectedCards.value[1] && 
         getCardInfo(selectedCards.value[0]) && getCardInfo(selectedCards.value[1])
})

onMounted(() => {
  fetchCards()
})
</script>

<style>
.select-dropdown {
  @apply bg-white rounded-lg shadow-lg border-0;
}

.select-dropdown .el-select-dropdown__item {
  @apply py-2 px-4 hover:bg-primary-50;
}

.select-dropdown .el-select-dropdown__item.selected {
  @apply bg-primary-100 text-primary-600 font-medium;
}
</style> 