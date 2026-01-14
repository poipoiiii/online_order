<template>
  <div class="home-container">
    <!-- 顶部搜索与定位栏 -->
    <div class="search-bar-wrapper">
      <div class="location-picker" @click="chooseLocation">
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { Shop, StarFilled, Search, Location, LocationInformation } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const shops = ref([])
const searchQuery = ref('')
const loading = ref(false)
const currentLocation = ref('')
const coords = ref(null)

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

const chooseLocation = () => {
  const input = prompt("请输入经纬度 (格式: lat,lng) 或输入城市名模拟定位:", "")
  if (input) {
    if (input.includes(',')) {
      const [lat, lng] = input.split(',')
      saveLocation(parseFloat(lat), parseFloat(lng), '自定义位置')
    } else {
      // 简单模拟城市坐标
      const cityMap = {
        '北京': { lat: 39.9042, lng: 116.4074 },
        '上海': { lat: 31.2304, lng: 121.4737 },
        '广州': { lat: 23.1291, lng: 113.2644 },
        '深圳': { lat: 22.5431, lng: 114.0579 },
        '成都': { lat: 30.5728, lng: 104.0668 },
        '杭州': { lat: 30.2741, lng: 120.1551 }
      }
      const cityCoords = cityMap[input]
      if (cityCoords) {
        saveLocation(cityCoords.lat, cityCoords.lng, input)
      } else {
        ElMessage.error('未知城市，请输入经纬度')
      }
    }
  }
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
  color: #333;
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
  background: #fff;
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
}

.campaign-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.campaign-card h3 { margin: 0 0 4px 0; font-size: 18px; color: #333; }
.campaign-card p { margin: 0 0 8px 0; font-size: 12px; color: #999; }

.daily-deal { background: linear-gradient(135deg, #ffe6e6 0%, #fff 100%); }
.flash-sale { background: linear-gradient(135deg, #fff7e6 0%, #fff 100%); }
.big-brand { background: linear-gradient(135deg, #e6f7ff 0%, #fff 100%); }

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  color: #303133;
  font-size: 20px;
}

.shop-card {
  margin-bottom: 24px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: none;
  overflow: hidden;
}

.shop-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1) !important;
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
  color: #303133;
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
  color: #909399;
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
</style>
