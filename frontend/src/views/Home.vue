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
            <img :src="getShopImage(shop)" class="shop-image" loading="lazy">
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
    const res = await axios.get('/api/shops/', { params })
    shops.value = res.data
  } catch (e) {
    console.error(e)
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

.search-bar-wrapper {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.location-picker {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--text-color);
  font-weight: bold;
  white-space: nowrap;
}

.search-input {
  flex: 1;
  max-width: 500px;
}

.campaign-section {
  margin-bottom: 32px;
}

.campaign-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: transform 0.2s;
  height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border: var(--glass-border);
  box-shadow: 0 4px 12px var(--shadow-color);
  backdrop-filter: blur(5px);
}

.campaign-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px var(--shadow-color);
}

.campaign-card h3 { margin: 0 0 4px 0; font-size: 18px; color: var(--text-color); }
.campaign-card p { margin: 0 0 8px 0; font-size: 12px; color: var(--text-secondary); }

.daily-deal { background: linear-gradient(135deg, rgba(255, 230, 230, 0.8) 0%, rgba(255, 255, 255, 0.8) 100%); }
.flash-sale { background: linear-gradient(135deg, rgba(255, 247, 230, 0.8) 0%, rgba(255, 255, 255, 0.8) 100%); }
.big-brand { background: linear-gradient(135deg, rgba(230, 247, 255, 0.8) 0%, rgba(255, 255, 255, 0.8) 100%); }

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  color: var(--text-color);
  font-size: 20px;
}

.shop-card {
  margin-bottom: 24px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: none;
  overflow: hidden;
  background: var(--card-bg) !important;
  backdrop-filter: blur(10px);
  border: var(--glass-border) !important;
  box-shadow: 0 4px 12px var(--shadow-color) !important;
}

.shop-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px var(--shadow-color) !important;
}

.image-wrapper {
  height: 160px;
  overflow: hidden;
  position: relative;
}

.shop-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.shop-card:hover .shop-image {
  transform: scale(1.05);
}

.shop-status {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.6);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.distance-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255,255,255,0.9);
  color: #333;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: bold;
}

.card-content {
  padding: 16px;
}

.shop-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.shop-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.rating {
  display: flex;
  align-items: center;
  gap: 2px;
  color: #ff9900;
  font-weight: bold;
  font-size: 14px;
}

.shop-desc {
  color: var(--text-secondary);
  font-size: 13px;
  margin: 0 0 12px 0;
  height: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shop-tags {
  display: flex;
  gap: 6px;
}

/* Location Dialog Styles */
.location-options {
  padding: 10px 0;
}
.current-location-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.2s;
}
.current-location-option:hover {
  background: #f5f7fa;
}
.login-tip {
  text-align: center;
  padding: 20px;
}
.address-list {
  max-height: 300px;
  overflow-y: auto;
}
.address-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}
.address-item:hover {
  background: #f5f7fa;
}
.addr-text {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 4px;
}
.addr-contact {
  font-size: 12px;
  color: #999;
}
</style>
