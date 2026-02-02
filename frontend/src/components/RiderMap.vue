<template>
  <div class="map-container">
    <div ref="mapRef" class="map-view"></div>
    <div class="map-status" v-if="status">
      <div class="status-item">
        <span class="label">状态:</span>
        <span class="value">{{ status }}</span>
      </div>
      <div class="status-item" v-if="distance">
        <span class="label">距离:</span>
        <span class="value">{{ distance }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  shopLocation: Object, // { lat, lng }
  userLocation: Object, // { lat, lng }
  riderLocation: Object, // { lat, lng } (optional, if provided)
  status: String
})

const mapRef = ref(null)
let map = null
let riderMarker = null
let drivingRoute = null

onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map) {
    // Clean up if needed
  }
})

// Watch for rider location updates
watch(() => props.riderLocation, (newVal) => {
  if (newVal && map) {
    updateRiderPosition(newVal)
  }
}, { deep: true })

const initMap = () => {
  if (!window.BMap) return
  
  map = new window.BMap.Map(mapRef.value)
  const point = new window.BMap.Point(props.shopLocation.lng, props.shopLocation.lat)
  map.centerAndZoom(point, 15)
  map.enableScrollWheelZoom(true)

  // Add Shop Marker
  const shopIcon = new window.BMap.Icon("https://api.map.baidu.com/images/marker_red_sprite.png", new window.BMap.Size(39, 25))
  const shopMarker = new window.BMap.Marker(point, { icon: shopIcon })
  map.addOverlay(shopMarker)
  
  // Add User Marker
  if (props.userLocation) {
    const userPoint = new window.BMap.Point(props.userLocation.lng, props.userLocation.lat)
    const userMarker = new window.BMap.Marker(userPoint)
    map.addOverlay(userMarker)
    
    // Draw Route
    drawRoute(point, userPoint)
  }

  // Init Rider Marker (if delivering)
  if (props.status === 'delivering' || props.status === 'cooking') {
    // Start rider at shop if no location yet
    const riderStart = props.riderLocation ? 
      new window.BMap.Point(props.riderLocation.lng, props.riderLocation.lat) : 
      point
      
    // Use a custom icon for rider (e.g., a bike or different color)
    // Using a simple blue marker for now, or simulate a bike icon URL
    // Here using a standard icon but we could use a custom one
    riderMarker = new window.BMap.Marker(riderStart)
    map.addOverlay(riderMarker)
    
    // If no real-time data, we can simulate movement along the route in a real app
    // For now, we just show the marker
  }
}

const distance = ref('')

const drawRoute = (p1, p2) => {
  const driving = new window.BMap.DrivingRoute(map, {
    renderOptions: { map: map, autoViewport: true },
    onSearchComplete: (results) => {
      if (driving.getStatus() === window.BMAP_STATUS_SUCCESS) {
        const plan = results.getPlan(0)
        distance.value = plan.getDistance(true) + ' / ' + plan.getDuration(true)
      }
    }
  })
  driving.search(p1, p2)
  drivingRoute = driving
}

const updateRiderPosition = (loc) => {
  if (!riderMarker) return
  const newPoint = new window.BMap.Point(loc.lng, loc.lat)
  riderMarker.setPosition(newPoint)
}

</script>

<style scoped>
.map-container {
  width: 100%;
  height: 300px;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 10px;
}
.map-view {
  width: 100%;
  height: 100%;
}
.map-status {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  font-size: 12px;
}
.status-item {
  margin-bottom: 4px;
}
.label {
  color: #666;
  margin-right: 4px;
}
.value {
  font-weight: bold;
  color: #333;
}
</style>