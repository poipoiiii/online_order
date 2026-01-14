
import { ElMessage } from 'element-plus'

/**
 * 获取当前位置
 * @returns {Promise<{lat: number, lng: number, address: string}>}
 */
export const getCurrentLocation = () => {
  return new Promise((resolve, reject) => {
    if (!window.BMap || !window.BMap.Geolocation) {
      const error = new Error('百度地图脚本未加载或初始化失败')
      console.warn(error.message)
      // Fallback to native geolocation
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords
            resolve({
              lat: latitude,
              lng: longitude,
              address: `Lat:${latitude.toFixed(6)}, Lng:${longitude.toFixed(6)}`
            })
          },
          (err) => {
            reject(err)
          }
        )
      } else {
        reject(error)
      }
      return
    }

    const geolocation = new window.BMap.Geolocation()
    geolocation.getCurrentPosition(function(r) {
      if (this.getStatus() === window.BMAP_STATUS_SUCCESS) {
        const lat = r.point.lat
        const lng = r.point.lng
        let address = '当前位置'
        if (r.address) {
          // 拼接详细地址
          const { province, city, district, street, street_number } = r.address
          address = `${province || ''}${city || ''}${district || ''}${street || ''}${street_number || ''}`
        }
        resolve({ lat, lng, address })
      } else {
        reject(new Error('定位失败，状态码: ' + this.getStatus()))
      }
    }, { enableHighAccuracy: true })
  })
}
