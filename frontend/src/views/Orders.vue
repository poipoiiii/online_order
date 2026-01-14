<template>
  <div class="orders-page">
    <h2>我的订单</h2>
    <el-empty v-if="orders.length === 0" description="暂无订单"></el-empty>
    
    <div v-else class="order-list">
      <el-card v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="shop-name" @click="$router.push(`/shop/${order.shop}`)">{{ order.shop_name }} <el-icon><ArrowRight /></el-icon></span>
          <span class="status-tag" :class="order.status">{{ order.status_display }}</span>
        </div>
        
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item-row">
            <span class="item-name">{{ item.dish_name }}</span>
            <span class="item-qty">x{{ item.quantity }}</span>
            <span class="item-price">￥{{ item.price }}</span>
          </div>
        </div>
        
        <div class="order-footer">
          <span class="time">{{ formatDate(order.created_at) }}</span>
          <div class="total">
            共 {{ order.items.length }} 件，实付 <span class="price">￥{{ order.total_price }}</span>
          </div>
        </div>
        
        <div class="actions">
          <el-button v-if="order.status === 'unpaid'" size="small" type="danger" @click="$router.push(`/payment/${order.id}`)">去支付</el-button>
          <el-button v-if="order.status === 'delivered'" size="small" @click="openReviewDialog(order)">评价</el-button>
          <el-button v-if="order.status === 'delivered'" size="small" type="primary" plain>再来一单</el-button>
        </div>
      </el-card>
    </div>
    <!-- 评价弹窗 -->
    <el-dialog v-model="reviewDialogVisible" title="评价订单" width="400px">
      <el-form :model="reviewForm">
        <el-form-item label="评分">
          <el-rate v-model="reviewForm.rating" show-text></el-rate>
        </el-form-item>
        <el-form-item label="评论">
          <el-input type="textarea" v-model="reviewForm.comment" placeholder="说说味道怎么样..."></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">提交评价</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'

const orders = ref([])
const loading = ref(false)

// Review
const reviewDialogVisible = ref(false)
const reviewForm = ref({ order: null, shop: null, rating: 5, comment: '' })

onMounted(() => {
  fetchOrders()
})

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/orders/')
    orders.value = res.data
  } catch (e) {
    ElMessage.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

const openReviewDialog = (order) => {
  reviewForm.value = { order: order.id, shop: order.shop, rating: 5, comment: '' }
  reviewDialogVisible.value = true
}

const submitReview = async () => {
  try {
    await axios.post('/api/reviews/', reviewForm.value)
    ElMessage.success('评价成功')
    reviewDialogVisible.value = false
  } catch (e) {
    ElMessage.error('评价失败')
  }
}

const formatDate = (str) => {
  return new Date(str).toLocaleString()
}
</script>

<style scoped>
.orders-page { max-width: 800px; margin: 0 auto; }
.order-card { margin-bottom: 20px; }
.order-header { display: flex; justify-content: space-between; border-bottom: 1px solid #f0f0f0; padding-bottom: 12px; margin-bottom: 12px; }
.shop-name { font-weight: bold; cursor: pointer; display: flex; align-items: center; }
.status-tag { font-size: 13px; }
.status-tag.unpaid { color: #f56c6c; }
.status-tag.pending { color: #e6a23c; }
.status-tag.cooking { color: #409eff; }
.status-tag.delivering { color: #409eff; }
.status-tag.delivered { color: #67c23a; }

.order-items { margin-bottom: 12px; }
.order-item-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; color: #606266; }
.item-name { flex: 1; }
.item-qty { width: 50px; text-align: center; }
.item-price { width: 80px; text-align: right; }

.order-footer { display: flex; justify-content: space-between; align-items: center; color: #909399; font-size: 12px; }
.price { color: #303133; font-weight: bold; font-size: 16px; margin-left: 4px; }
.actions { margin-top: 12px; text-align: right; border-top: 1px solid #f0f0f0; padding-top: 12px; }
</style>
