<template>
  <div class="cards-container">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="银行">
          <el-select v-model="filterForm.bank" placeholder="选择银行" clearable>
            <el-option
              v-for="bank in banks"
              :key="bank.value"
              :label="bank.label"
              :value="bank.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="卡片等级">
          <el-select v-model="filterForm.level" placeholder="选择等级" clearable>
            <el-option
              v-for="level in levels"
              :key="level.value"
              :label="level.label"
              :value="level.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年费">
          <el-select v-model="filterForm.annualFee" placeholder="选择年费" clearable>
            <el-option
              v-for="fee in annualFees"
              :key="fee.value"
              :label="fee.label"
              :value="fee.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleFilter">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 信用卡列表 -->
    <div class="cards-list">
      <el-carousel :interval="4000" type="card" height="400px" v-if="showCarousel">
        <el-carousel-item v-for="card in filteredCards" :key="card.id">
          <el-card class="card-item" shadow="hover">
            <div class="card-content">
              <h3>{{ card.bank_name }} - {{ card.card_name }}</h3>
              <div class="card-info">
                <p><strong>卡片等级：</strong>{{ card.card_level }}</p>
                <p><strong>年费政策：</strong>{{ card.annual_fee }}</p>
                <p><strong>信用额度：</strong>{{ card.credit_limit }}</p>
                <div class="benefits">
                  <el-tag
                    v-for="(value, key) in (card.benefits || {})"
                    :key="key"
                    size="small"
                    class="benefit-tag"
                  >
                    {{ key }}: {{ value }}
                  </el-tag>
                </div>
              </div>
              <div class="card-actions">
                <el-button type="primary" @click="viewCardDetail(card.id)">
                  查看详情
                </el-button>
              </div>
            </div>
          </el-card>
        </el-carousel-item>
      </el-carousel>

      <!-- 列表视图 -->
      <el-row :gutter="20" v-else>
        <el-col :span="8" v-for="card in filteredCards" :key="card.id">
          <el-card class="card-item" shadow="hover">
            <div class="card-content">
              <h3>{{ card.bank_name }} - {{ card.card_name }}</h3>
              <div class="card-info">
                <p><strong>卡片等级：</strong>{{ card.card_level }}</p>
                <p><strong>年费政策：</strong>{{ card.annual_fee }}</p>
                <p><strong>信用额度：</strong>{{ card.credit_limit }}</p>
                <div class="benefits">
                  <el-tag
                    v-for="(value, key) in (card.benefits || {})"
                    :key="key"
                    size="small"
                    class="benefit-tag"
                  >
                    {{ key }}: {{ value }}
                  </el-tag>
                </div>
              </div>
              <div class="card-actions">
                <el-button type="primary" @click="viewCardDetail(card.id)">
                  查看详情
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 视图切换按钮 -->
    <div class="view-toggle">
      <el-button-group>
        <el-button
          :type="showCarousel ? 'primary' : 'default'"
          @click="showCarousel = true"
        >
          轮播视图
        </el-button>
        <el-button
          :type="!showCarousel ? 'primary' : 'default'"
          @click="showCarousel = false"
        >
          列表视图
        </el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { cards as cardsApi } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const cardsList = ref([])
const showCarousel = ref(true)

// 筛选表单
const filterForm = ref({
  bank: '',
  level: '',
  annualFee: ''
})

// 银行选项
const banks = ref([
  { value: '工商银行', label: '工商银行' },
  { value: '建设银行', label: '建设银行' },
  { value: '中国银行', label: '中国银行' },
  { value: '农业银行', label: '农业银行' }
])

// 卡片等级选项
const levels = ref([
  { value: '普卡', label: '普卡' },
  { value: '金卡', label: '金卡' },
  { value: '白金卡', label: '白金卡' },
  { value: '钻石卡', label: '钻石卡' }
])

// 年费选项
const annualFees = ref([
  { value: '免年费', label: '免年费' },
  { value: '刷免', label: '刷免' },
  { value: '刚性年费', label: '刚性年费' }
])

// 获取信用卡列表
const fetchCards = async () => {
  try {
    const response = await cardsApi.getAll()
    cardsList.value = response.data
  } catch (error) {
    console.error('获取信用卡列表失败:', error)
    ElMessage.error('获取信用卡列表失败')
  }
}

// 筛选后的信用卡列表
const filteredCards = computed(() => {
  return cardsList.value.filter(card => {
    const matchBank = !filterForm.value.bank || card.bank_name === filterForm.value.bank
    const matchLevel = !filterForm.value.level || card.card_level === filterForm.value.level
    const matchAnnualFee = !filterForm.value.annualFee || card.annual_fee.includes(filterForm.value.annualFee)
    return matchBank && matchLevel && matchAnnualFee
  })
})

// 处理筛选
const handleFilter = () => {
  // 筛选逻辑已经在 computed 中实现
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    bank: '',
    level: '',
    annualFee: ''
  }
}

// 查看卡片详情
const viewCardDetail = (cardId) => {
  router.push(`/cards/${cardId}`)
}

onMounted(() => {
  fetchCards()
})
</script>

<style scoped>
.cards-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 0;
}

.filter-form :deep(.el-select) {
  width: 200px;
}

.filter-form :deep(.el-input__inner) {
  font-size: 14px;
}

.cards-list {
  margin: 20px 0;
}

.card-item {
  height: 100%;
}

.card-content {
  padding: 20px;
  text-align: center;
}

.card-content h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.card-info {
  margin: 15px 0;
}

.card-info p {
  margin: 5px 0;
  color: #606266;
}

.benefits {
  margin: 15px 0;
}

.benefit-tag {
  margin: 0 5px 5px 0;
}

.card-actions {
  margin-top: 20px;
}

.view-toggle {
  text-align: center;
  margin-top: 20px;
}
</style> 