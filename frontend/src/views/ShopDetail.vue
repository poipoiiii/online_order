<template>
  <div v-if="shop" class="shop-detail">
    <!-- 店铺头部信息 -->
    <div class="shop-header">
      <div class="shop-info">
        <img :src="getShopImage(shop)" class="header-image">
        <div class="header-text">
          <h1>{{ shop.name }}</h1>
          <div class="rating-row">
            <el-rate v-model="shop.rating" disabled show-score text-color="#fff" score-template="{value}分"></el-rate>
            <span class="divider">|</span>
            <span>配送约30分钟</span>
          </div>
          <p class="desc">{{ shop.description || '暂无店铺描述' }}</p>
        </div>
      </div>
    </div>

    <!-- 菜单区域 -->
    <div class="menu-container">
      <!-- 左侧分类导航 -->
      <div class="category-sidebar">
        <div 
          v-for="cat in categories" 
          :key="cat.id"
          class="category-item"
          :class="{ active: activeCategory === cat.id }"
          @click="scrollToCategory(cat.id)"
        >
          {{ cat.name }}
        </div>
      </div>

      <!-- 右侧菜品列表 -->
      <div class="dish-list-wrapper">
        <div v-for="cat in categories" :key="cat.id" :id="'cat-' + cat.id" class="category-section">
          <h3 class="category-title">{{ cat.name }}</h3>
          <div class="dish-grid">
            <div v-for="dish in getDishesByCategory(cat.id)" :key="dish.id" class="dish-item">
              <img :src="getDishImage(dish)" class="dish-img">
              <div class="dish-info">
                <h4 class="dish-name">{{ dish.name }}</h4>
                <p class="dish-desc">{{ dish.description || '暂无介绍' }}</p>
                <div class="dish-bottom">
                  <span class="price">￥{{ dish.price }}</span>
                  <el-button 
                    type="primary" 
                    circle 
                    size="small" 
                    :icon="Plus"
                    @click="addToCart(dish)"
                  ></el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const route = useRoute()
const shop = ref(null)
const dishes = ref([])
const categories = ref([])
const activeCategory = ref(null)

onMounted(async () => {
  const shopId = route.params.id
  try {
    const [shopRes, dishesRes, catRes] = await Promise.all([
      axios.get(`/api/shops/${shopId}/`),
      axios.get(`/api/dishes/?shop=${shopId}`),
      axios.get(`/api/categories/?shop=${shopId}`) // 注意：后端需支持此筛选，如果不支持前端自己筛
    ])
    shop.value = shopRes.data
    // 确保 rating 是数字，避免 ElementPlus 警告
    if (shop.value.rating) {
      shop.value.rating = Number(shop.value.rating)
    }
    dishes.value = dishesRes.data
    
    // 如果后端API没过滤 categories，我们这里先模拟一下分类数据
    // 假设后端返回了所有分类，我们这里手动提取或者使用后端数据
    // 这里的 demo 数据生成脚本生成了 Category，所以我们最好获取一下
    // 由于我们没有写 filterset_fields=['shop'] for CategoryViewSet, 可能获取的是全部
    // 简单起见，我们从 dishes 中提取分类
    const uniqueCats = new Map()
    dishes.value.forEach(d => {
      if (d.category_name) {
         // 这里有个小问题，dish serializer 只返回了 category_name，没返回 ID
         // 让我们修改一下 DishSerializer 返回 category_id 或者直接用 name 分组
         // 简单起见，这里按 category_name 分组，假设 name 唯一
         if (!uniqueCats.has(d.category)) {
           uniqueCats.set(d.category, d.category_name)
         }
      }
    })
    
    // 构造前端用的分类列表
    categories.value = Array.from(uniqueCats.entries()).map(([id, name]) => ({ id, name }))
    if (categories.value.length > 0) activeCategory.value = categories.value[0].id

  } catch (e) {
    console.error(e)
  }
})

const getDishesByCategory = (catId) => {
  return dishes.value.filter(d => d.category === catId)
}

const scrollToCategory = (catId) => {
  activeCategory.value = catId
  const el = document.getElementById('cat-' + catId)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

const addToCart = (dish) => {
  let cart = JSON.parse(localStorage.getItem('cart')) || { items: [], shopId: null }
  if (cart.shopId && cart.shopId !== shop.value.id) {
    if (!confirm('购物车中已有其他店铺商品，是否清空？')) return
    cart = { items: [], shopId: null }
  }
  cart.shopId = shop.value.id
  const existing = cart.items.find(i => i.dish_id === dish.id)
  if (existing) existing.quantity++
  else cart.items.push({ 
    dish_id: dish.id, 
    name: dish.name, 
    price: dish.price, 
    quantity: 1, 
    image: dish.image, 
    image_url: dish.image_url 
  })
  localStorage.setItem('cart', JSON.stringify(cart))
  ElMessage.success({ message: '已加入购物车', type: 'success', duration: 1000 })
}

// ---------------- 图片处理 ----------------
const getShopImage = (shop) => {
  if (shop.image_url) return shop.image_url
  if (shop.image) return shop.image
  return 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=500&auto=format&fit=crop'
}

const getDishImage = (dish) => {
  if (dish.image_url) return dish.image_url
  if (dish.image) return dish.image
  return 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&auto=format&fit=crop'
}
</script>

<style scoped>
.shop-detail {
  background: white;
  min-height: 80vh;
}

.shop-header {
  background: #333;
  color: white;
  padding: 30px 20px;
}

.shop-info {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
}

.header-image {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid rgba(255,255,255,0.2);
}

.header-text h1 { margin: 0 0 10px 0; font-size: 24px; }
.rating-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.divider { color: #666; }
.desc { color: #ccc; margin: 0; font-size: 13px; max-width: 600px; }

.menu-container {
  display: flex;
  max-width: 1000px;
  margin: 0 auto;
  height: calc(100vh - 250px); /* 视口高度减去头部 */
  overflow: hidden;
}

.category-sidebar {
  width: 120px;
  background: #f5f7fa;
  overflow-y: auto;
}

.category-item {
  padding: 16px 12px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  border-left: 3px solid transparent;
}

.category-item.active {
  background: white;
  color: #333;
  font-weight: bold;
  border-left-color: #409EFF;
}

.dish-list-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
}

.category-title {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.dish-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f9f9f9;
}

.dish-img {
  width: 90px;
  height: 90px;
  border-radius: 6px;
  object-fit: cover;
}

.dish-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.dish-name { margin: 0 0 4px 0; font-size: 16px; }
.dish-desc { margin: 0; font-size: 12px; color: #999; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.dish-bottom { display: flex; justify-content: space-between; align-items: center; }
.price { color: #f56c6c; font-weight: bold; font-size: 18px; }
</style>
