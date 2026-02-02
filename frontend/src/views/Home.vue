<template>
  <div class="home-container">
    <!-- 顶部搜索与定位栏 -->
    <div class="search-bar-wrapper">
      <div class="location-picker" @click="showLocationDialog">
        <el-icon><Location /></el-icon>
        <span class="location-text">{{ currentLocation || '点击定位' }}</span>
        <el-tag size="small" type="info" style="margin-left: 5px">切换</el-tag>
      </div>
      <el-input
        v-model="searchQuery"
        placeholder="搜索商家或美食..."
        prefix-icon="Search"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 地址选择弹窗 -->
    <el-dialog v-model="locationDialogVisible" title="选择收货地址" width="500px">
      <div class="location-options">
        <div class="current-location-option" @click="handleAutoLocate">
          <el-icon><Aim /></el-icon>
          <span>定位到当前位置</span>
        </div>
        
        <!-- 手动输入位置搜索 -->
        <div style="margin-top: 10px; padding: 0 10px;">
          <el-input 
            v-model="manualLocationInput" 
            placeholder="输入城市或地址（如：北京）" 
            clearable
            @keyup.enter="handleManualLocationSearch"
          >
            <template #append>
              <el-button @click="handleManualLocationSearch">确认</el-button>
            </template>
          </el-input>
        </div>

        <el-divider content-position="left">我的收货地址</el-divider>
        
        <div v-if="!isLoggedIn" class="login-tip">
          <el-button type="primary" link @click="$router.push('/login')">登录后可选择收货地址</el-button>
        </div>
        
        <el-empty v-else-if="userAddresses.length === 0" description="暂无收货地址">
          <el-button type="primary" size="small" @click="$router.push('/profile')">去添加</el-button>
        </el-empty>

        <div v-else class="address-list">
          <div 
            v-for="addr in userAddresses" 
            :key="addr.id" 
            class="address-item"
            @click="selectAddress(addr)"
          >
            <div class="addr-info">
              <div class="addr-text">{{ addr.address }}</div>
              <div class="addr-contact">{{ addr.name }} {{ addr.phone }}</div>
            </div>
            <el-icon v-if="isAddressSelected(addr)" color="#409EFF"><Select /></el-icon>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 营销活动区 -->
    <div class="campaign-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="campaign-card daily-deal" @click="filterByTag('daily_deal')">
            <h3>每日优惠</h3>
            <p>超值美食天天享</p>
            <el-tag type="danger" effect="dark">HOT</el-tag>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="campaign-card flash-sale" @click="filterByTag('flash_sale')">
            <h3>限时秒杀</h3>
            <p>手慢无 抢好货</p>
            <el-tag type="warning" effect="dark">限时</el-tag>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="campaign-card big-brand" @click="filterByTag('big_brand')">
            <h3>大牌一口价</h3>
            <p>知名大牌 品质保障</p>
            <el-tag effect="dark">优选</el-tag>
          </div>
        </el-col>
      </el-row>
    </div>

    <h2 class="section-title">
      <el-icon><Shop /></el-icon> 附近好店
    </h2>
    
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <el-empty v-else-if="shops.length === 0" description="附近暂无商家"></el-empty>
    
    <el-row v-else :gutter="24">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="shop in shops" :key="shop.id">
        <el-card shadow="hover" class="shop-card" :body-style="{ padding: '0px' }" @click="$router.push(`/shop/${shop.id}`)">
          <div class="image-wrapper">
            <img 
              :src="getShopImage(shop)" 
              class="shop-image" 
              loading="lazy"
              decoding="async"
              :alt="shop.name"
            >
            <div class="shop-status" v-if="!shop.is_open">休息中</div>
            <div class="distance-badge" v-if="shop.distance">
              <el-icon><LocationInformation /></el-icon>
              {{ formatDistance(shop.distance) }}
            </div>
          </div>
          <div class="card-content">
            <div class="shop-header">
              <h3 class="shop-name">{{ shop.name }}</h3>
              <span class="rating">
                <el-icon color="#FF9900"><StarFilled /></el-icon>
                {{ shop.rating }}
              </span>
            </div>
            <p class="shop-desc">{{ shop.description || '暂无描述' }}</p>
            <div class="shop-tags">
              <el-tag size="small" type="info" effect="plain">30分钟送达</el-tag>
              <el-tag size="small" type="success" effect="plain">免配送费</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { Shop, StarFilled, Search, Location, LocationInformation, Aim, Select } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const shops = ref([])
const searchQuery = ref('')
const loading = ref(false)
const currentLocation = ref('')
const coords = ref(null)

// Location Dialog
const locationDialogVisible = ref(false)
const userAddresses = ref([])
const isLoggedIn = computed(() => !!authStore.token)
const manualLocationInput = ref('')

onMounted(() => {
  // 1. 尝试从 LocalStorage 读取已保存的定位信息
  const savedLoc = localStorage.getItem('user_location')
  if (savedLoc) {
    try {
      const locData = JSON.parse(savedLoc)
      // 简单的有效期检查（例如 1 小时内有效）
      if (Date.now() - locData.timestamp < 3600 * 1000) {
        coords.value = locData.coords
        currentLocation.value = locData.name
        fetchShops()
        return
      }
    } catch (e) {
      localStorage.removeItem('user_location')
    }
  }
  
  // 2. 如果没有保存的位置，则尝试自动定位
  getLocation()
})

const saveLocation = (lat, lng, name) => {
  coords.value = { lat, lng }
  currentLocation.value = name
  localStorage.setItem('user_location', JSON.stringify({
    coords: { lat, lng },
    name: name,
    timestamp: Date.now()
  }))
  fetchShops()
}

const getLocation = () => {
  if (coords.value) return // 已有位置不再重复定位
  ElMessage.info('正在定位中...')
  
  // 优先使用百度地图定位，并增加异常捕获
  try {
    if (window.BMap && window.BMap.Geolocation) {
      const geolocation = new window.BMap.Geolocation()
      geolocation.getCurrentPosition(function(r) {
        if (this.getStatus() === window.BMAP_STATUS_SUCCESS) {
          const lat = r.point.lat
          const lng = r.point.lng
          let addrName = '当前位置'
          if (r.address) {
             addrName = `${r.address.city || ''}${r.address.district || ''}${r.address.street || ''}`
          }
          ElMessage.success('定位成功')
          saveLocation(lat, lng, addrName)
        } else {
          console.warn('百度定位失败状态码:', this.getStatus())
          useNativeLocation()
        }
      }, {enableHighAccuracy: true})
    } else {
      console.warn('百度地图脚本未加载或初始化失败')
      useNativeLocation()
    }
  } catch (e) {
    console.error('调用百度地图API出错:', e)
    useNativeLocation()
  }
}

const useNativeLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords
        ElMessage.success('定位成功')
        saveLocation(latitude, longitude, `Lat:${latitude.toFixed(2)}, Lng:${longitude.toFixed(2)}`)
      },
      (error) => {
        console.error(error)
        ElMessage.warning('定位失败，请手动搜索或选择位置')
        currentLocation.value = '定位失败'
      }
    )
  } else {
    ElMessage.warning('您的浏览器不支持地理定位')
  }
}

// 添加缓存机制
const shopsCache = ref({})

const fetchShops = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value
    }
    if (coords.value) {
      params.lat = coords.value.lat
      params.lng = coords.value.lng
    }
    
    // 生成缓存键
    const cacheKey = JSON.stringify(params)
    
    // 检查缓存
    if (shopsCache.value[cacheKey]) {
      console.log('使用缓存的商家数据')
      shops.value = shopsCache.value[cacheKey]
      loading.value = false
      return
    }
    
    // 发起请求
    const res = await axios.get('/api/shops/', { params })
    shops.value = res.data
    
    // 缓存结果
    shopsCache.value[cacheKey] = res.data
  } catch (e) {
    console.error(e)
    // 尝试使用缓存数据
    const cacheKey = JSON.stringify({
      search: searchQuery.value,
      lat: coords.value?.lat,
      lng: coords.value?.lng
    })
    if (shopsCache.value[cacheKey]) {
      shops.value = shopsCache.value[cacheKey]
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchShops()
}

const filterByTag = (tag) => {
  router.push(`/search?tag=${tag}`)
}

const formatDistance = (val) => {
  if (val === undefined || val === null) return ''
  if (val < 1) return '< 1km'
  return `${val.toFixed(1)}km`
}

const showLocationDialog = async () => {
  locationDialogVisible.value = true
  if (isLoggedIn.value) {
    try {
      const res = await axios.get('/api/addresses/')
      userAddresses.value = res.data
    } catch (e) {
      console.error('获取地址失败', e)
    }
  }
}

const handleAutoLocate = () => {
  getLocation()
  locationDialogVisible.value = false
}

const handleManualLocationSearch = () => {
  const input = manualLocationInput.value.trim()
  if (!input) return
  
  // 简单模拟城市坐标映射（实际应调用地理编码 API）
  // 为了支持"北京"，我们手动添加常用城市
  const cityMap = {
    '北京': { lat: 39.9042, lng: 116.4074 },
    '北京市': { lat: 39.9042, lng: 116.4074 },
    '上海': { lat: 31.2304, lng: 121.4737 },
    '上海市': { lat: 31.2304, lng: 121.4737 },
    '广州': { lat: 23.1291, lng: 113.2644 },
    '广州市': { lat: 23.1291, lng: 113.2644 },
    '深圳': { lat: 22.5431, lng: 114.0579 },
    '深圳市': { lat: 22.5431, lng: 114.0579 },
    '宁波': { lat: 29.8683, lng: 121.5440 },
    '宁波市': { lat: 29.8683, lng: 121.5440 },
    '镇海': { lat: 29.9550, lng: 121.7150 },
    '镇海区': { lat: 29.9550, lng: 121.7150 }
  }

  const cityCoords = cityMap[input]
  if (cityCoords) {
    saveLocation(cityCoords.lat, cityCoords.lng, input)
    locationDialogVisible.value = false
    ElMessage.success(`已切换至: ${input}`)
  } else {
    // 尝试调用百度地图 API 进行解析
    if (window.BMap && window.BMap.Geocoder) {
      const myGeo = new window.BMap.Geocoder()
      myGeo.getPoint(input, function(point) {
        if (point) {
           saveLocation(point.lat, point.lng, input)
           locationDialogVisible.value = false
           ElMessage.success(`已切换至: ${input}`)
        } else {
           ElMessage.warning('无法解析该地址，请尝试输入更详细的城市名')
        }
      })
    } else {
      ElMessage.warning('未知位置且地图服务未加载，请尝试输入主要城市名')
    }
  }
}

const selectAddress = (addr) => {
  // Address 模型包含 latitude 和 longitude
  if (addr.latitude && addr.longitude) {
    saveLocation(addr.latitude, addr.longitude, addr.address)
    locationDialogVisible.value = false
  } else {
    // 如果没有经纬度（旧数据），可能需要地理编码，或者提示用户
    // 简单起见，这里假设都有，或者调用后端 geocode (但目前后端 save 时已处理)
    if (addr.latitude === 0 && addr.longitude === 0) {
       ElMessage.warning('该地址暂无坐标信息，请编辑后重试')
       return
    }
    // 兼容逻辑
    saveLocation(addr.latitude || 0, addr.longitude || 0, addr.address)
    locationDialogVisible.value = false
  }
}

const isAddressSelected = (addr) => {
  if (!coords.value) return false
  // 简单比较坐标
  const EPSILON = 0.00001
  return Math.abs(addr.latitude - coords.value.lat) < EPSILON && 
         Math.abs(addr.longitude - coords.value.lng) < EPSILON
}

const chooseLocation = () => {
  // Deprecated in favor of dialog, but keeping logic for fallback if needed or debug
  showLocationDialog()
}

const getShopImage = (shop) => {
  if (shop.image_url) return shop.image_url
  if (shop.image) return shop.image
  return 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=500&auto=format&fit=crop'
}
</script>

<style scoped>
.home-container {
  padding-bottom: 40px;
}

/* 搜索栏和定位优化 */
.search-bar-wrapper {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.location-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-color);
  font-weight: bold;
  white-space: nowrap;
  padding: 10px 16px;
  border-radius: 20px;
  background: var(--glass-bg);
  border: var(--glass-border);
  box-shadow: 0 2px 8px var(--shadow-color);
  transition: all 0.2s;
}

.location-picker:hover {
  background: var(--bg-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.search-input {
  flex: 1;
  max-width: 500px;
  min-width: 200px;
}

.search-input .el-input__wrapper {
  border-radius: 25px !important;
  box-shadow: 0 2px 8px var(--shadow-color);
  transition: all 0.2s;
}

.search-input .el-input__wrapper:hover {
  box-shadow: 0 4px 12px var(--shadow-color);
}

.search-input .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px var(--primary-color) !important;
}

/* 营销活动区优化 */
.campaign-section {
  margin-bottom: 32px;
}

.campaign-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: var(--glass-border);
  box-shadow: 0 4px 16px var(--shadow-color);
  backdrop-filter: blur(8px);
}

.campaign-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 24px var(--shadow-color);
}

.campaign-card h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: var(--text-color);
  font-weight: 700;
  animation: fadeInUp 0.3s ease;
}

.campaign-card p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--text-secondary);
  animation: fadeInUp 0.4s ease 0.1s both;
}

.campaign-card .el-tag {
  animation: fadeInUp 0.5s ease 0.2s both;
}

.daily-deal {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 255, 255, 0.8) 100%);
  border-left: 4px solid #f56c6c;
}

.flash-sale {
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.1) 0%, rgba(255, 255, 255, 0.8) 100%);
  border-left: 4px solid #e6a23c;
}

.big-brand {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(255, 255, 255, 0.8) 100%);
  border-left: 4px solid #409EFF;
}

/* 商家列表优化 */
.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  color: var(--text-color);
  font-size: 22px;
  font-weight: 700;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--primary-color);
  animation: slideInLeft 0.5s ease;
}

.shop-card {
  margin-bottom: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  overflow: hidden;
  background: var(--card-bg) !important;
  backdrop-filter: blur(12px);
  border: var(--glass-border) !important;
  box-shadow: 0 4px 16px var(--shadow-color) !important;
  border-radius: 16px !important;
}

.shop-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px var(--shadow-color) !important;
}

.image-wrapper {
  height: 180px;
  overflow: hidden;
  position: relative;
  border-radius: 16px 16px 0 0;
}

.shop-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.shop-card:hover .shop-image {
  transform: scale(1.1);
}

.shop-status {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.distance-badge {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(4px);
  animation: fadeInUp 0.4s ease 0.1s both;
}

.card-content {
  padding: 20px;
}

.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.shop-name {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  animation: fadeInUp 0.3s ease;
}

.rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #ff9900;
  font-weight: bold;
  font-size: 14px;
  background: rgba(255, 153, 0, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  animation: fadeInUp 0.4s ease 0.1s both;
}

.shop-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 16px 0;
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  animation: fadeInUp 0.4s ease 0.2s both;
}

.shop-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  animation: fadeInUp 0.4s ease 0.3s both;
}

.shop-tags .el-tag {
  border-radius: 12px;
  font-size: 12px;
  padding: 2px 8px;
  transition: all 0.2s;
}

.shop-tags .el-tag:hover {
  transform: scale(1.05);
}

/* 加载状态优化 */
.loading-state {
  padding: 40px 20px;
  text-align: center;
}

.loading-state .el-skeleton {
  background: var(--glass-bg);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px var(--shadow-color);
}

/* 空状态优化 */
:deep(.el-empty) {
  padding: 60px 20px !important;
}

:deep(.el-empty__image) {
  width: 120px !important;
  height: 120px !important;
}

:deep(.el-empty__description) {
  font-size: 16px !important;
  color: var(--text-secondary) !important;
  margin-top: 20px !important;
}

:deep(.el-empty__action) {
  margin-top: 30px !important;
}

:deep(.el-empty__action .el-button) {
  border-radius: 20px;
  padding: 8px 20px;
  box-shadow: 0 2px 8px var(--shadow-color);
  transition: all 0.2s;
}

:deep(.el-empty__action .el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

/* 地址选择弹窗优化 */
.location-options {
  padding: 20px 0;
}

.current-location-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.2s;
  background: var(--glass-bg);
  border: var(--glass-border);
  box-shadow: 0 2px 8px var(--shadow-color);
  margin-bottom: 16px;
}

.current-location-option:hover {
  background: var(--bg-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.login-tip {
  text-align: center;
  padding: 30px;
  background: var(--glass-bg);
  border-radius: 12px;
  margin: 20px 0;
}

.login-tip .el-button {
  border-radius: 20px;
  padding: 8px 24px;
  font-weight: 600;
}

.address-list {
  max-height: 350px;
  overflow-y: auto;
  margin-top: 16px;
}

.address-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 8px;
  margin-bottom: 8px;
}

.address-item:hover {
  background: var(--glass-bg);
  transform: translateX(4px);
}

.addr-text {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 6px;
  color: var(--text-color);
}

.addr-contact {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计优化 */
@media (max-width: 768px) {
  .search-bar-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .location-picker {
    justify-content: center;
  }
  
  .search-input {
    max-width: none;
  }
  
  .campaign-card {
    height: 100px;
    padding: 16px;
  }
  
  .campaign-card h3 {
    font-size: 18px;
  }
  
  .campaign-card p {
    font-size: 12px;
  }
  
  .section-title {
    font-size: 18px;
    margin-bottom: 20px;
  }
  
  .image-wrapper {
    height: 150px;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .shop-name {
    font-size: 16px;
  }
  
  .location-options {
    padding: 10px 0;
  }
  
  .current-location-option {
    padding: 12px;
  }
  
  .address-item {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .campaign-card {
    height: 90px;
    padding: 12px;
  }
  
  .campaign-card h3 {
    font-size: 16px;
  }
  
  .image-wrapper {
    height: 120px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 16px;
  }
  
  .card-content {
    padding: 12px;
  }
  
  .shop-name {
    font-size: 14px;
  }
}
</style>
