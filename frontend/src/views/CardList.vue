<template>
  <div class="card-list">
    <div class="search-bar">
      <input 
        v-model="searchKeyword"
        type="text"
        placeholder="搜索信用卡..."
        @input="handleSearch"
      >
      <div class="filters">
        <select v-model="selectedBank" @change="handleFilter">
          <option value="">全部银行</option>
          <option v-for="bank in banks" :key="bank" :value="bank">{{ bank }}</option>
        </select>
        <select v-model="selectedLevel" @change="handleFilter">
          <option value="">全部等级</option>
          <option v-for="level in levels" :key="level" :value="level">{{ level }}</option>
        </select>
      </div>
    </div>

    <div class="cards-grid">
      <div v-for="card in filteredCards" :key="card.id" class="card-item">
        <h3>{{ card.card_name }}</h3>
        <div class="card-info">
          <p><strong>发卡行：</strong>{{ card.bank_name }}</p>
          <p><strong>卡片等级：</strong>{{ card.card_level }}</p>
          <p><strong>年费：</strong>{{ card.annual_fee }}</p>
          <p><strong>额度：</strong>{{ card.credit_limit }}</p>
        </div>
        <button @click="showDetails(card)" class="view-details">查看详情</button>
      </div>
    </div>

    <div v-if="selectedCard" class="card-details-modal">
      <div class="modal-content">
        <h2>{{ selectedCard.card_name }}</h2>
        <div class="details-content">
          <p><strong>发卡行：</strong>{{ selectedCard.bank_name }}</p>
          <p><strong>卡片等级：</strong>{{ selectedCard.card_level }}</p>
          <p><strong>年费政策：</strong>{{ selectedCard.annual_fee }}</p>
          <p><strong>额度范围：</strong>{{ selectedCard.credit_limit }}</p>
          <p><strong>积分规则：</strong>{{ selectedCard.points_rule }}</p>
          <h3>权益详情</h3>
          <pre>{{ formatJSON(selectedCard.benefits) }}</pre>
          <h3>申请条件</h3>
          <pre>{{ formatJSON(selectedCard.requirements) }}</pre>
        </div>
        <button @click="closeDetails" class="close-modal">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CardList',
  data() {
    return {
      cards: [],
      searchKeyword: '',
      selectedBank: '',
      selectedLevel: '',
      selectedCard: null,
      banks: [],
      levels: []
    }
  },
  computed: {
    filteredCards() {
      let result = this.cards;
      
      if (this.searchKeyword) {
        const keyword = this.searchKeyword.toLowerCase();
        result = result.filter(card => 
          card.card_name.toLowerCase().includes(keyword) ||
          card.bank_name.toLowerCase().includes(keyword)
        );
      }
      
      if (this.selectedBank) {
        result = result.filter(card => card.bank_name === this.selectedBank);
      }
      
      if (this.selectedLevel) {
        result = result.filter(card => card.card_level === this.selectedLevel);
      }
      
      return result;
    }
  },
  methods: {
    async fetchCards() {
      try {
        const response = await axios.get('http://localhost:8000/api/cards');
        this.cards = response.data.data;
        this.extractFilters();
      } catch (error) {
        console.error('获取信用卡数据失败:', error);
      }
    },
    extractFilters() {
      this.banks = [...new Set(this.cards.map(card => card.bank_name))];
      this.levels = [...new Set(this.cards.map(card => card.card_level))];
    },
    handleSearch() {
      // 搜索逻辑已通过计算属性实现
    },
    handleFilter() {
      // 筛选逻辑已通过计算属性实现
    },
    showDetails(card) {
      this.selectedCard = card;
    },
    closeDetails() {
      this.selectedCard = null;
    },
    formatJSON(jsonString) {
      try {
        const obj = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
        return JSON.stringify(obj, null, 2);
      } catch (e) {
        return jsonString;
      }
    }
  },
  mounted() {
    this.fetchCards();
  }
}
</script>

<style scoped>
.card-list {
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filters {
  display: flex;
  gap: 10px;
}

.filters select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.card-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-item h3 {
  margin: 0 0 10px 0;
  color: #1890ff;
}

.card-info p {
  margin: 5px 0;
}

.view-details {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.view-details:hover {
  background-color: #40a9ff;
}

.card-details-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.details-content {
  margin: 20px 0;
}

.close-modal {
  padding: 8px 16px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-modal:hover {
  background-color: #ff7875;
}

pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
}
</style> 