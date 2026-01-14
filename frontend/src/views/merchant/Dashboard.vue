<template>
  <div class="merchant-dashboard">
    <div class="header">
      <h2>商家后台管理系统</h2>
      <el-tag type="success" v-if="shop">{{ shop.name }}</el-tag>
    </div>
    
    <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
      <!-- 订单管理 -->
      <el-tab-pane label="订单管理" name="orders">
        <div class="filter-bar">
          <el-radio-group v-model="orderFilter" size="small" @change="fetchOrders">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="pending">待接单</el-radio-button>
            <el-radio-button value="accepted">制作中</el-radio-button>
            <el-radio-button value="delivering">配送中</el-radio-button>
            <el-radio-button value="completed">已完成</el-radio-button>
          </el-radio-group>
          <el-button icon="Refresh" circle @click="fetchOrders"></el-button>
        </div>

        <el-table :data="filteredOrders" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="订单号" width="80"></el-table-column>
          <el-table-column label="商品信息">
            <template #default="scope">
              <div v-for="item in scope.row.items" :key="item.id">
                {{ item.dish_name }} x {{ item.quantity }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="total_price" label="金额" width="100">
             <template #default="scope">￥{{ scope.row.total_price }}</template>
          </el-table-column>
          <el-table-column prop="status_display" label="状态" width="100">
             <template #default="scope">
               <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status_display }}</el-tag>
             </template>
          </el-table-column>
          <el-table-column label="时间" width="160">
             <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button v-if="scope.row.status === 'pending'" size="small" type="primary" @click="updateStatus(scope.row.id, 'accepted')">接单</el-button>
              <el-button v-if="scope.row.status === 'accepted'" size="small" type="warning" @click="updateStatus(scope.row.id, 'cooking')">开始制作</el-button>
              <el-button v-if="scope.row.status === 'cooking'" size="small" type="success" @click="updateStatus(scope.row.id, 'delivering')">出餐完成</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 菜品管理 -->
      <el-tab-pane label="菜品管理" name="dishes">
        <div class="action-bar">
          <el-button type="primary" icon="Plus" @click="openDishDialog()">新增菜品</el-button>
        </div>
        
        <el-table :data="dishes" style="width: 100%" v-loading="loading">
          <el-table-column label="图片" width="100">
            <template #default="scope">
              <img :src="scope.row.image_url || scope.row.image || 'https://via.placeholder.com/60'" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;">
            </template>
          </el-table-column>
          <el-table-column prop="name" label="名称"></el-table-column>
          <el-table-column prop="price" label="价格" width="100"></el-table-column>
          <el-table-column prop="stock" label="库存" width="100"></el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-switch v-model="scope.row.is_available" @change="toggleDishStatus(scope.row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="openDishDialog(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteDish(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 店铺设置 -->
      <el-tab-pane label="店铺设置" name="settings">
        <el-form :model="shopForm" label-width="100px" style="max-width: 500px">
          <el-form-item label="店铺名称">
            <el-input v-model="shopForm.name"></el-input>
          </el-form-item>
          <el-form-item label="店铺描述">
            <el-input type="textarea" v-model="shopForm.description"></el-input>
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="shopForm.phone"></el-input>
          </el-form-item>
          <el-form-item label="营业状态">
             <el-switch v-model="shopForm.is_open" active-text="营业中" inactive-text="休息中"></el-switch>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="updateShop">保存修改</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <!-- 菜品编辑弹窗 -->
    <el-dialog v-model="dishDialogVisible" :title="isEdit ? '编辑菜品' : '新增菜品'">
      <el-form :model="dishForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="dishForm.name"></el-input>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="dishForm.price" :min="0" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="dishForm.original_price" :min="0" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="库存">
          <el-input-number v-model="dishForm.stock" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="dishForm.description"></el-input>
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="dishForm.image_url" placeholder="请输入图片链接"></el-input>
        </el-form-item>
        <el-form-item label="活动标签">
           <el-select v-model="dishForm.tag" clearable>
             <el-option label="每日优惠" value="daily_deal"></el-option>
             <el-option label="限时秒杀" value="flash_sale"></el-option>
             <el-option label="大牌一口价" value="big_brand"></el-option>
           </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDish">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const activeTab = ref('orders')
const orders = ref([])
const dishes = ref([])
const shop = ref(null)
const loading = ref(false)
const orderFilter = ref('all')

// Shop Settings Form
const shopForm = ref({})

// Dish Form
const dishDialogVisible = ref(false)
const isEdit = ref(false)
const dishForm = ref({ name: '', price: 0, stock: 100, description: '', image_url: '', tag: '' })

onMounted(() => {
  fetchOrders()
  fetchShopInfo()
})

const handleTabChange = (tab) => {
  if (tab === 'orders') fetchOrders()
  if (tab === 'dishes') fetchDishes()
}

// ----------------- Orders -----------------
const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/orders/')
    orders.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const filteredOrders = computed(() => {
  if (orderFilter.value === 'all') return orders.value
  if (orderFilter.value === 'completed') return orders.value.filter(o => ['delivered', 'cancelled'].includes(o.status))
  return orders.value.filter(o => o.status === orderFilter.value)
})

const updateStatus = async (id, status) => {
  await axios.post(`/api/orders/${id}/update_status/`, { status })
  ElMessage.success('操作成功')
  fetchOrders()
}

// ----------------- Shop -----------------
const fetchShopInfo = async () => {
  // 假设当前用户只能获取自己的店铺，后端需配合或前端遍历
  // 简化：获取当前用户的店铺信息，这需要后端 API 支持 "get my shop"
  // 这里我们假设后端 /api/shops/ 列表里包含了当前商家的店铺，或者我们增加一个 /api/shops/my_shop/ 接口
  // 由于 ShopViewSet 是 ModelViewSet，我们可以尝试 filter?merchant=current_user_id
  // 但前端不知道 user_id，从 store 取
  if (authStore.user) {
    // 临时方案：遍历所有 shops 找到自己的 (不推荐用于生产，但用于演示)
    // 更好方案：后端增加 `me` 接口
    // 这里先尝试获取所有，找到自己的
    try {
      // 实际上后端 ShopViewSet 应该增加 @action(detail=False) def my_shop
      // 这里暂时用一个假设的接口或逻辑
      const res = await axios.get('/api/shops/')
      // 假设 authStore.user.username 是唯一的，且我们知道店铺 merchant 用户名
      // 后端 ShopSerializer 返回了 merchant_id 或者 merchant_username?
      // 查看 ShopSerializer: merchant 是 ReadOnlyField(source='merchant.username')
      const myShop = res.data.find(s => s.merchant === authStore.user.username)
      if (myShop) {
        shop.value = myShop
        shopForm.value = { ...myShop }
      }
    } catch (e) {}
  }
}

const updateShop = async () => {
  if (!shop.value) return
  try {
    await axios.patch(`/api/shops/${shop.value.id}/`, shopForm.value)
    ElMessage.success('店铺信息已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

// ----------------- Dishes -----------------
const fetchDishes = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/dishes/')
    dishes.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const openDishDialog = (dish = null) => {
  if (dish) {
    isEdit.value = true
    dishForm.value = { ...dish }
  } else {
    isEdit.value = false
    dishForm.value = { name: '', price: 0, stock: 100, description: '', image_url: '', tag: '', is_available: true }
  }
  dishDialogVisible.value = true
}

const saveDish = async () => {
  try {
    if (isEdit.value) {
      await axios.put(`/api/dishes/${dishForm.value.id}/`, dishForm.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/dishes/', dishForm.value)
      ElMessage.success('创建成功')
    }
    dishDialogVisible.value = false
    fetchDishes()
  } catch (e) {
    ElMessage.error('操作失败: ' + (e.response?.data?.detail || e.message))
  }
}

const toggleDishStatus = async (dish) => {
  try {
    await axios.patch(`/api/dishes/${dish.id}/`, { is_available: dish.is_available })
    ElMessage.success('状态已更新')
  } catch (e) {
    dish.is_available = !dish.is_available // revert
    ElMessage.error('更新失败')
  }
}

const deleteDish = (id) => {
  ElMessageBox.confirm('确定删除该菜品吗?', '提示', { type: 'warning' }).then(async () => {
    await axios.delete(`/api/dishes/${id}/`)
    ElMessage.success('已删除')
    fetchDishes()
  })
}

// Utils
const formatDate = (str) => new Date(str).toLocaleString()
const getStatusType = (status) => {
  const map = { pending: 'warning', accepted: 'primary', cooking: 'warning', delivering: 'primary', delivered: 'success', cancelled: 'info' }
  return map[status] || 'info'
}
</script>

<style scoped>
.merchant-dashboard { padding: 20px; }
.header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.filter-bar { margin-bottom: 20px; display: flex; justify-content: space-between; }
.action-bar { margin-bottom: 20px; }
</style>
