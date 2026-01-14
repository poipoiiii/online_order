<template>
  <div class="payment-container">
    <el-card class="payment-card">
      <template #header>
        <div class="header">
          <h2>收银台</h2>
          <span class="order-id">订单号: {{ orderId }}</span>
        </div>
      </template>

      <div class="amount-section">
        <p>支付金额</p>
        <div class="price">￥{{ order.total_price }}</div>
      </div>

      <div class="payment-methods">
        <h3>选择支付方式</h3>
        <el-radio-group v-model="paymentMethod" class="method-group">
          <el-radio border value="wechat" class="method-item">
            <div class="method-content">
              <el-icon class="wechat-icon" size="24" color="#09BB07"><ChatDotRound /></el-icon>
              <span>微信支付</span>
            </div>
          </el-radio>
          <el-radio border value="alipay" class="method-item">
            <div class="method-content">
              <el-icon class="alipay-icon" size="24" color="#1677FF"><Wallet /></el-icon>
              <span>支付宝</span>
            </div>
          </el-radio>
        </el-radio-group>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" :loading="paying" @click="handlePay" class="pay-btn">
          立即支付 ￥{{ order.total_price }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { ChatDotRound, Wallet } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const orderId = route.params.id
const order = ref({})
const paymentMethod = ref('wechat')
const paying = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get(`/api/orders/${orderId}/`)
    order.value = res.data
    if (order.value.status !== 'unpaid') {
      ElMessage.warning('该订单已支付或状态异常')
      router.replace('/orders')
    }
  } catch (e) {
    ElMessage.error('获取订单信息失败')
  }
})

const handlePay = async () => {
  paying.value = true
  
  // 模拟支付过程的延迟
  const loading = ElLoading.service({
    lock: true,
    text: '正在跳转支付...',
    background: 'rgba(0, 0, 0, 0.7)',
  })

  setTimeout(async () => {
    try {
      await axios.post(`/api/orders/${orderId}/pay/`, {
        payment_method: paymentMethod.value
      })
      loading.close()
      ElMessage.success('支付成功！')
      router.push('/orders')
    } catch (e) {
      loading.close()
      ElMessage.error('支付失败: ' + (e.response?.data?.error || e.message))
    } finally {
      paying.value = false
    }
  }, 1500)
}
</script>

<style scoped>
.payment-container {
  max-width: 600px;
  margin: 40px auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h2 { margin: 0; font-size: 18px; }
.order-id { color: #999; font-size: 14px; }

.amount-section {
  text-align: center;
  padding: 30px 0;
  border-bottom: 1px solid #f0f0f0;
}

.amount-section p { color: #666; margin: 0 0 10px 0; }
.price { font-size: 36px; font-weight: bold; color: #333; }

.payment-methods {
  padding: 30px 0;
}

.method-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.method-item {
  margin-right: 0 !important;
  width: 100%;
  height: auto;
  padding: 15px;
}

.method-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.actions {
  margin-top: 20px;
}

.pay-btn {
  width: 100%;
}
</style>
