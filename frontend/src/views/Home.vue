<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 主要内容 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- 轮播图 -->
      <div class="mb-12">
        <el-carousel height="500px" :interval="5000" arrow="always">
          <el-carousel-item v-for="banner in banners" :key="banner.id">
            <div class="h-full flex items-center justify-center bg-gradient-to-r from-primary-500 to-primary-700 text-white relative overflow-hidden">
              <div class="absolute inset-0 bg-black opacity-20"></div>
              <div class="relative z-10 text-center px-8">
                <h2 class="text-5xl font-bold mb-6 animate-fade-in">{{ banner.title }}</h2>
                <p class="text-xl mb-8 max-w-2xl mx-auto animate-fade-in-delay">{{ banner.description }}</p>
                <router-link 
                  :to="banner.link" 
                  class="btn-primary bg-white text-primary-600 hover:bg-gray-100 transform hover:scale-105 transition-transform duration-300 inline-block px-8 py-3 text-lg"
                >
                  {{ banner.buttonText }}
                </router-link>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>

      <!-- 功能卡片 -->
      <div class="mb-16">
        <h2 class="text-3xl font-bold text-center mb-12">我们的服务</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="feature in features" :key="feature.id" 
               class="card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
            <div class="text-center p-8">
              <div class="text-5xl mb-6 text-primary-500">
                <i :class="feature.icon"></i>
              </div>
              <h3 class="text-xl font-semibold mb-4">{{ feature.title }}</h3>
              <p class="text-gray-600 mb-6">{{ feature.description }}</p>
              <router-link 
                :to="feature.link" 
                class="btn-primary inline-block w-full text-center"
              >
                了解更多
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门信用卡 -->
      <div class="mb-16">
        <h2 class="text-3xl font-bold text-center mb-12">热门信用卡推荐</h2>
        <el-carousel :interval="4000" type="card" height="400px">
          <el-carousel-item v-for="card in hotCards" :key="card.id">
            <div class="card h-full transform hover:scale-105 transition-transform duration-300">
              <div class="p-6">
                <h3 class="text-xl font-semibold mb-2">{{ card.bank_name }} - {{ card.card_name }}</h3>
                <p class="text-gray-600 mb-4">{{ card.card_level }}</p>
                <div class="mb-6">
                  <span class="inline-block bg-primary-100 text-primary-800 text-sm px-3 py-1 rounded-full mr-2 mb-2"
                        v-for="(benefit, index) in card.benefits.split(',')"
                        :key="index">
                    {{ benefit }}
                  </span>
                </div>
                <router-link 
                  :to="'/cards/' + card.id" 
                  class="btn-primary w-full text-center block"
                >
                  查看详情
                </router-link>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-gray-800 text-white py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 class="text-lg font-semibold mb-4">关于我们</h3>
            <p class="text-gray-400">专业的信用卡推荐平台，为您提供最合适的信用卡选择建议。</p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">联系方式</h3>
            <p class="text-gray-400">邮箱：support@creditcard.com</p>
            <p class="text-gray-400">电话：400-123-4567</p>
          </div>
          <div>
            <h3 class="text-lg font-semibold mb-4">关注我们</h3>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-400 hover:text-white transition-colors duration-300">
                <i class="fab fa-weixin text-2xl"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors duration-300">
                <i class="fab fa-weibo text-2xl"></i>
              </a>
            </div>
          </div>
        </div>
        <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
          <p>© 2024 信用卡助手. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 轮播图数据
const banners = ref([
  {
    id: 1,
    title: '智能信用卡推荐',
    description: '基于AI技术，为您推荐最适合的信用卡，让您的消费更智能、更优惠',
    buttonText: '开始体验',
    link: '/chat'
  },
  {
    id: 2,
    title: '信用卡对比',
    description: '多维度对比不同信用卡的权益和费用，助您做出最佳选择',
    buttonText: '立即对比',
    link: '/compare'
  }
])

// 功能卡片数据
const features = ref([
  {
    id: 1,
    title: '信用卡列表',
    description: '浏览各大银行的信用卡产品，了解详细权益和申请条件',
    icon: 'fas fa-credit-card',
    link: '/cards'
  },
  {
    id: 2,
    title: 'AI助手',
    description: '智能对话，解答您的信用卡相关问题，提供个性化建议',
    icon: 'fas fa-robot',
    link: '/chat'
  },
  {
    id: 3,
    title: '信用卡对比',
    description: '多维度对比不同信用卡的权益和费用，助您做出最佳选择',
    icon: 'fas fa-balance-scale',
    link: '/compare'
  }
])

// 热门信用卡数据
const hotCards = ref([
  {
    id: 1,
    bank_name: '中国银行',
    card_name: '长城环球通信用卡',
    card_level: '白金卡',
    benefits: '机场贵宾厅,积分兑换,消费返现'
  },
  {
    id: 2,
    bank_name: '建设银行',
    card_name: '龙卡信用卡',
    card_level: '金卡',
    benefits: '消费返现,积分兑换,免费道路救援'
  },
  {
    id: 3,
    bank_name: '工商银行',
    card_name: '牡丹信用卡',
    card_level: '白金卡',
    benefits: '机场贵宾厅,积分兑换,消费返现'
  }
])
</script>

<style scoped>
.home-container {
  padding: 20px;
  margin-top: 20px;
}

.recommend-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #303133;
}

.card-carousel {
  margin: 0 auto;
  max-width: 1200px;
}

.card-item {
  height: 300px;
  margin: 0 20px;
}

.card-content {
  padding: 20px;
  text-align: center;
}
</style>

<style>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 1s ease-out;
}

.animate-fade-in-delay {
  animation: fadeIn 1s ease-out 0.3s forwards;
  opacity: 0;
}
</style> 