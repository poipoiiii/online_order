<template>
  <div class="cart-page">
    <el-card class="cart-card">
      <template #header>
        <div class="card-header">
          <span>购物车</span>
          <el-button link type="primary" @click="clearCart" :disabled="cart.items.length === 0">清空购物车</el-button>
        </div>
      </template>
      
      <el-table :data="cart.items" style="width: 100%" empty-text="购物车是空的，快去选购美食吧">
        <el-table-column width="100" label="图片">
          <template #default="scope">
            <img :src="scope.row.image || scope.row.image_url || 'https://via.placeholder.com/80'" class="cart-img">
          </template>
        </el-table-column>
        <el-table-column prop="name" label="菜品"></el-table-column>
        <el-table-column prop="price" label="单价" width="100">
          <template #default="scope">￥{{ scope.row.price }}</template>
        </el-table-column>
        <el-table-column label="数量" width="160">
          <template #default="scope">
            <el-input-number v-model="scope.row.quantity" :min="1" size="small" @change="saveCart" />
          </template>
        </el-table-column>
        <el-table-column label="小计" width="100">
          <template #default="scope">
            <span class="subtotal">￥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="scope">
            <el-button type="danger" link icon="Delete" @click="removeItem(scope.$index)"></el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="cart-footer" v-if="cart.items.length > 0">
        <div class="total-info">
          总计: <span class="total-price">￥{{ totalPrice }}</span>
        </div>
        <el-button type="primary" size="large" @click="placeOrder" class="checkout-btn">去结算</el-button>
      </div>
    </el-card>

    <!-- 下单弹窗 -->
    <el-dialog v-model="dialogVisible" title="确认订单" width="500px">
       <el-form label-position="top">
         <el-form-item label="选择收货地址">
           <el-select v-model="selectedAddress" placeholder="请选择地址" style="width: 100%">
             <el-option v-for="addr in addresses" :key="addr.id" :label="formatAddress(addr)" :value="addr.id"></el-option>
           </el-select>
           <div class="address-tip" v-if="addresses.length === 0">
             暂无地址，<el-button type="primary" link @click="addMockAddress">添加测试地址</el-button>
           </div>
         </el-form-item>
         <el-form-item label="支付方式">
            <el-radio-group v-model="paymentMethod">
              <el-radio value="wechat">微信支付</el-radio>
              <el-radio value="alipay">支付宝</el-radio>
            </el-radio-group>
         </el-form-item>
       </el-form>
       <template #footer>
         <el-button @click="dialogVisible = false">取消</el-button>
         <el-button type="primary" @click="confirmOrder" :loading="submitting">确认支付</el-button>
       </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Delete } from '@element-plus/icons-vue'

const cart = ref({ items: [] })
const dialogVisible = ref(false)
const addresses = ref([])
const selectedAddress = ref(null)
const paymentMethod = ref('wechat')
const submitting = ref(false)
const router = useRouter()

const totalPrice = computed(() => {
  return cart.value.items.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2)
})

onMounted(async () => {
  cart.value = JSON.parse(localStorage.getItem('cart')) || { items: [] }
  loadAddresses()
})

const loadAddresses = async () => {
  try {
    const res = await axios.get('/api/addresses/')
    addresses.value = res.data
    if (addresses.value.length > 0) {
      selectedAddress.value = addresses.value[0].id
    }
  } catch (e) {
    // maybe not logged in
  }
}

const formatAddress = (addr) => {
  return `${addr.address} (${addr.name} 收) ${addr.phone}`
}

const addMockAddress = async () => {
  try {
    await axios.post('/api/addresses/', {
      name: '测试用户',
      phone: '13800138000',
      address: '测试地址 ' + Math.floor(Math.random() * 1000) + ' 号',
      is_default: true
    })
    ElMessage.success('地址添加成功')
    loadAddresses()
  } catch (e) {
    ElMessage.error('添加失败: ' + e.message)
  }
}

const saveCart = () => {
  localStorage.setItem('cart', JSON.stringify(cart.value))
  // 触发 storage 事件以便 Layout 更新 badge (在同一页面需要手动触发自定义事件或使用 store)
  window.dispatchEvent(new Event('storage'))
}

const removeItem = (index) => {
  cart.value.items.splice(index, 1)
  saveCart()
}

const clearCart = () => {
  cart.value = { items: [], shopId: null }
  localStorage.removeItem('cart')
  window.dispatchEvent(new Event('storage'))
}

const placeOrder = () => {
  if (cart.value.items.length === 0) return ElMessage.warning('购物车为空')
  // 检查登录
  if (!localStorage.getItem('token')) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  dialogVisible.value = true
}

const confirmOrder = async () => {
  if (!selectedAddress.value) return ElMessage.warning('请选择地址')
  submitting.value = true
  try {
    const res = await axios.post('/api/orders/place_order/', {
      shop_id: cart.value.shopId,
      address_id: selectedAddress.value,
      items: cart.value.items
    })
    ElMessage.success('下单成功，请支付')
    clearCart()
    dialogVisible.value = false
    // 跳转到支付页面
    router.push(`/payment/${res.data.id}`)
  } catch (error) {
    ElMessage.error('下单失败: ' + (error.response?.data?.error || error.message))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.cart-page {
  max-width: 1000px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.cart-img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}
.subtotal {
  color: #f56c6c;
  font-weight: bold;
}
.cart-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}
.total-info {
  font-size: 16px;
}
.total-price {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
}
.checkout-btn {
  width: 120px;
}
.address-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
