<template>
  <div class="search-result-page">
    <div class="page-header">
      <el-button icon="ArrowLeft" circle @click="$router.go(-1)"></el-button>
      <h2>{{ pageTitle }}</h2>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <el-empty v-else-if="dishes.length === 0" description="暂无相关活动商品"></el-empty>

    <div v-else class="dish-grid">
      <div v-for="dish in dishes" :key="dish.id" class="dish-card" @click="goToShop(dish.shop)">
        <div class="dish-img-box">
          <img :src="getDishImage(dish)" class="dish-img" loading="lazy">
          <div class="tag-badge" v-if="dish.tag">{{ getTagName(dish.tag) }}</div>
        </div>
        <div class="dish-info">
          <h3 class="dish-name">{{ dish.name }}</h3>
          <div class="shop-name"><el-icon><Shop /></el-icon> {{ dish.shop_name || '店铺' }}</div>
          <div class="price-row">
            <span class="price">￥{{ dish.price }}</span>
            <span class="original-price" v-if="dish.original_price">￥{{ dish.original_price }}</span>
          </div>
          <el-button type="primary" size="small" round>去抢购</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ArrowLeft, Shop } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const dishes = ref([])
const loading = ref(false)
const tag = route.query.tag

const pageTitle = computed(() => {
  const map = {
    'daily_deal': '每日优惠',
    'flash_sale': '限时秒杀',
    'big_brand': '大牌一口价'
  }
  return map[tag] || '活动商品'
})

onMounted(async () => {
  if (!tag) return
  loading.value = true
  try {
    // 假设后端 DishViewSet 支持 ?tag=xxx 过滤
    // 我们需要在 DishSerializer 中增加 shop_name 字段以便展示
    const res = await axios.get(`/api/dishes/?tag=${tag}`)
    dishes.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

const getTagName = (t) => {
  const map = { 'daily_deal': '特惠', 'flash_sale': '秒杀', 'big_brand': '大牌' }
  return map[t] || ''
}

const goToShop = (shopId) => {
  router.push(`/shop/${shopId}`)
}

const getDishImage = (dish) => {
  if (dish.image_url) return dish.image_url
  if (dish.image) return dish.image
  return 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&auto=format&fit=crop'
}
</script>

<style scoped>
.search-result-page {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.dish-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.dish-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.dish-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.dish-img-box {
  position: relative;
  height: 160px;
}

.dish-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tag-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #ff4d4f;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.dish-info {
  padding: 12px;
}

.dish-name {
  margin: 0 0 4px 0;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.shop-name {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 8px;
}

.price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}

.original-price {
  color: #ccc;
  font-size: 12px;
  text-decoration: line-through;
}
</style>
