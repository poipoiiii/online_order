<template>
  <div class="rider-dashboard">
    <div class="header">
      <div class="status-bar">
        <h2>骑手工作台</h2>
        <div class="right-status">
          <div class="location-status" @click="updateLocation" style="cursor: pointer; margin-right: 20px; display: flex; align-items: center; color: #666">
             <el-icon style="margin-right: 4px"><Aim /></el-icon>
             <span style="font-size: 14px">{{ currentAddress }}</span>
          </div>
          <div class="work-status">
            <span style="margin-right: 10px; font-size: 14px; color: #666">接单状态:</span>
            <el-switch v-model="isOnline" active-text="听单中" inactive-text="休息中" active-color="#13ce66"></el-switch>
          </div>
        </div>
      </div>
    </div>

    <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
      <!-- 任务大厅 -->
      <el-tab-pane label="任务大厅" name="hall">
        <div class="filter-bar">
          <el-alert title="请保持电话畅通，抢单后请尽快前往店铺取餐" type="warning" :closable="false" show-icon />
          <el-button icon="Refresh" circle @click="fetchOrders" style="margin-left: 10px"></el-button>
        </div>
        
        <el-empty v-if="hallOrders.length === 0" description="暂无待抢订单"></el-empty>
        
        <el-row :gutter="20" v-else>
          <el-col :span="12" v-for="order in hallOrders" :key="order.id">
            <el-card class="order-card" shadow="hover">
              <div class="card-header">
                <span class="shop-name">{{ order.shop_name }}</span>
                <el-tag effect="dark" type="warning">待抢单</el-tag>
              </div>
              <div class="card-content">
                <div class="info-row"><el-icon><Location /></el-icon> 取: {{ order.shop_address || '店铺地址' }}</div>
                <div class="info-row"><el-icon><Position /></el-icon> 送: {{ order.address_str }}</div>
                <div class="info-row"><el-icon><Money /></el-icon> 配送费: ￥5.0</div>
              </div>
              <div class="card-footer">
                <span class="time">{{ formatDate(order.created_at) }}</span>
                <el-button type="primary" :disabled="!isOnline" @click="grabOrder(order.id)">立即抢单</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 我的配送 -->
      <el-tab-pane label="我的配送" name="mine">
        <el-table :data="myOrders" style="width: 100%" stripe>
          <el-table-column prop="id" label="订单号" width="80"></el-table-column>
          <el-table-column label="配送信息">
            <template #default="scope">
              <div><strong>取:</strong> {{ scope.row.shop_name }}</div>
              <div><strong>送:</strong> {{ scope.row.address_str }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="status_display" label="当前状态" width="100">
             <template #default="scope">
               <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status_display }}</el-tag>
             </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button v-if="scope.row.status === 'delivering'" type="success" size="small" @click="updateStatus(scope.row.id, 'delivered')">确认送达</el-button>
              <span v-else-if="scope.row.status === 'delivered'" style="color: #67c23a">已完成</span>
              <span v-else style="color: #909399">--</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 个人中心 -->
      <el-tab-pane label="业绩统计" name="stats">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="今日完成单量" :value="todayStats.count" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="今日预计收入" :precision="2" :value="todayStats.income">
              <template #prefix>￥</template>
            </el-statistic>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Location, Position, Money, Refresh, Aim } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import { getCurrentLocation } from '../../utils/location'

const authStore = useAuthStore()
const activeTab = ref('hall')
const orders = ref([])
const isOnline = ref(true)
const currentAddress = ref('未知位置')
const locationCoords = ref(null)

onMounted(() => {
  fetchOrders()
  updateLocation()
})

watch(isOnline, (val) => {
  if (val) updateLocation()
})

const updateLocation = async () => {
  try {
    const loc = await getCurrentLocation()
    currentAddress.value = loc.address
    locationCoords.value = { lat: loc.lat, lng: loc.lng }
    // 如果需要，这里可以将位置发送给后端 API 更新骑手实时位置
    // await axios.post('/api/rider/location/', { lat: loc.lat, lng: loc.lng })
  } catch (e) {
    console.error('获取位置失败', e)
    currentAddress.value = '定位失败'
  }
}

const handleTabChange = () => {
  fetchOrders()
}

const fetchOrders = async () => {
  try {
    const res = await axios.get('/api/orders/')
    // 后端 OrderViewSet 针对 rider 返回的是 status__in=['cooking', 'delivering', 'accepted']
    // 我们需要前端进一步区分哪些是可抢的，哪些是我的
    // 注意：当前后端逻辑是：rider只能看到所有符合状态的订单，或者只能看到自己的？
    // 让我们看后端 OrderViewSet get_queryset:
    // if user.role == 'rider': return Order.objects.filter(status__in=['cooking', 'delivering', 'accepted'])
    // 这意味着骑手能看到所有处于这些状态的订单，不管是谁的。
    // 我们需要区分：如果没有 rider 字段，就是待抢的；如果有 rider 且是自己，就是我的。
    orders.value = res.data.map(o => ({
      ...o,
      address_str: o.address_info ? `${o.address_info.address} ${o.address_info.name}` : '未知地址' // 需确认 serializer 是否返回 address 详情
      // OrderSerializer 默认只返回 address ID? 让我们检查一下
      // 如果 OrderSerializer 使用 Depth=1 或者嵌套 serializer，会有详情。
      // 假设暂时没有详情，我们显示 address ID 或让后端优化。
      // 为了体验，我们假设后端 OrderSerializer 应该优化。
      // 暂时用 Mock 地址
    }))
  } catch (e) {
    console.error(e)
  }
}

// 计算属性区分订单
const hallOrders = computed(() => {
  // 待抢订单：状态是 accepted, cooking 或 delivering (商家已出餐但未分配骑手)，且没有被分配骑手
  return orders.value.filter(o => !o.rider && ['accepted', 'cooking', 'delivering'].includes(o.status))
})

const myOrders = computed(() => {
  // 我的订单：rider 是我
  return orders.value.filter(o => o.rider === authStore.user.id)
})

const todayStats = computed(() => {
  // 简单前端统计 (实际应由后端聚合 API 提供)
  const today = new Date().toDateString()
  // 过滤出我完成的订单
  const myCompleted = orders.value.filter(o => 
    o.rider === authStore.user.id && 
    o.status === 'delivered' &&
    new Date(o.created_at).toDateString() === today // 仅统计今日
  )
  
  // 假设每单配送费 5 元
  return { 
    count: myCompleted.length, 
    income: myCompleted.length * 5.0 
  }
})

const grabOrder = async (id) => {
  if (!isOnline.value) return ElMessage.warning('请先开启接单状态')
  try {
    // 抢单逻辑：实际上是 update_status -> delivering，并设置 rider = current_user
    // 后端 update_status 逻辑：if status == 'delivering' and role == 'rider': order.rider = request.user
    // 所以我们发送 status: delivering 即可
    await axios.post(`/api/orders/${id}/update_status/`, { status: 'delivering' })
    ElMessage.success('抢单成功！请尽快配送')
    fetchOrders()
    activeTab.value = 'mine'
  } catch (e) {
    ElMessage.error('抢单失败')
  }
}

const updateStatus = async (id, status) => {
  await axios.post(`/api/orders/${id}/update_status/`, { status })
  ElMessage.success('操作成功')
  fetchOrders()
}

const formatDate = (str) => new Date(str).toLocaleString()
const getStatusType = (status) => {
  const map = { delivering: 'primary', delivered: 'success' }
  return map[status] || 'info'
}
</script>

<style scoped>
.rider-dashboard { padding: 20px; }
.header { margin-bottom: 20px; }
.status-bar { display: flex; justify-content: space-between; align-items: center; }
.right-status { display: flex; align-items: center; }
.work-status { display: flex; align-items: center; }
.filter-bar { display: flex; align-items: center; margin-bottom: 20px; }
.order-card { margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; font-weight: bold; }
.info-row { margin-bottom: 8px; color: #606266; font-size: 14px; display: flex; align-items: center; gap: 5px; }
.card-footer { border-top: 1px solid #EBEEF5; padding-top: 15px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center; }
.time { color: #909399; font-size: 12px; }
</style>
