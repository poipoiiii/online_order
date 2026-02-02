<template>
  <el-container class="app-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <div class="logo-box">
            <el-icon class="logo-icon"><Food /></el-icon>
          </div>
          <span class="logo-text">xx外卖</span>
        </div>
        
        <div class="nav-right">
          <!-- 移动端菜单按钮 -->
          <el-button 
            v-if="isMobile" 
            class="mobile-menu-btn" 
            @click="mobileMenuVisible = !mobileMenuVisible"
            circle
            plain
          >
            <el-icon><Menu /></el-icon>
          </el-button>
          
          <!-- 桌面端导航 -->
          <template v-else>
            <template v-if="authStore.isAuthenticated">
              <!-- 商家入口 -->
              <el-button 
                v-if="authStore.user?.role === 'merchant'" 
                type="success" 
                plain 
                round
                class="role-btn"
                @click="$router.push('/merchant')"
              >
                <el-icon><Shop /></el-icon> 商家中心
              </el-button>
              
              <!-- 骑手入口 -->
              <el-button 
                v-if="authStore.user?.role === 'rider'" 
                type="warning" 
                plain 
                round
                class="role-btn"
                @click="$router.push('/rider')"
              >
                <el-icon><Bicycle /></el-icon> 骑手中心
              </el-button>

              <!-- Theme Switcher -->
              <el-dropdown @command="handleTheme" trigger="click" class="theme-dropdown">
                <span class="theme-btn">
                  <el-icon><MagicStick /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="light">⚪ 简约白</el-dropdown-item>
                    <el-dropdown-item command="dark">⚫ 暗夜黑</el-dropdown-item>
                    <el-dropdown-item command="pink">🌸 樱花粉</el-dropdown-item>
                    <el-dropdown-item command="blue">🌊 海洋蓝</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>

              <el-badge :value="cartCount" :hidden="cartCount === 0" class="cart-badge" v-if="authStore.user?.role === 'customer'">
                <div class="cart-btn" @click="$router.push('/cart')">
                  <el-icon><ShoppingCart /></el-icon>
                  <span>购物车</span>
                </div>
              </el-badge>
              
              <el-dropdown @command="handleCommand" trigger="click" class="user-dropdown">
                <span class="user-info">
                  <el-avatar :size="36" :src="authStore.user?.avatar || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'"></el-avatar>
                  <span class="username">{{ authStore.user?.username }}</span>
                  <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu class="custom-dropdown">
                    <el-dropdown-item command="profile" icon="User">个人中心</el-dropdown-item>
                    <el-dropdown-item command="orders" icon="List">我的订单</el-dropdown-item>
                    <el-dropdown-item command="logout" divided icon="SwitchButton">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <div class="auth-buttons">
                <el-button type="primary" link @click="$router.push('/login')">登录</el-button>
                <el-button type="primary" round @click="$router.push('/register')">注册</el-button>
              </div>
            </template>
          </template>
        </div>
      </div>
    </el-header>
    
    <!-- 移动端菜单 -->
    <el-drawer 
      v-model="mobileMenuVisible" 
      direction="rtl" 
      size="80%"
      title="菜单"
      class="mobile-menu"
    >
      <div class="mobile-menu-content">
        <template v-if="authStore.isAuthenticated">
          <!-- 商家入口 -->
          <el-button 
            v-if="authStore.user?.role === 'merchant'" 
            type="success" 
            plain 
            class="mobile-role-btn"
            @click="$router.push('/merchant'); mobileMenuVisible = false"
          >
            <el-icon><Shop /></el-icon> 商家中心
          </el-button>
          
          <!-- 骑手入口 -->
          <el-button 
            v-if="authStore.user?.role === 'rider'" 
            type="warning" 
            plain 
            class="mobile-role-btn"
            @click="$router.push('/rider'); mobileMenuVisible = false"
          >
            <el-icon><Bicycle /></el-icon> 骑手中心
          </el-button>

          <!-- Theme Switcher -->
          <div class="mobile-theme-section">
            <h4 class="mobile-section-title">主题设置</h4>
            <div class="mobile-theme-options">
              <div 
                v-for="theme in themes" 
                :key="theme.value"
                class="mobile-theme-option"
                :class="{ active: currentTheme === theme.value }"
                @click="handleTheme(theme.value); mobileMenuVisible = false"
              >
                {{ theme.label }}
              </div>
            </div>
          </div>

          <el-badge :value="cartCount" :hidden="cartCount === 0" class="mobile-cart-badge" v-if="authStore.user?.role === 'customer'">
            <div class="mobile-cart-btn" @click="$router.push('/cart'); mobileMenuVisible = false">
              <el-icon><ShoppingCart /></el-icon>
              <span>购物车</span>
            </div>
          </el-badge>
          
          <div class="mobile-user-menu">
            <h4 class="mobile-section-title">个人中心</h4>
            <el-menu>
              <el-menu-item @click="$router.push('/profile'); mobileMenuVisible = false">
                <el-icon><User /></el-icon>
                <span>个人信息</span>
              </el-menu-item>
              <el-menu-item @click="$router.push('/orders'); mobileMenuVisible = false">
                <el-icon><List /></el-icon>
                <span>我的订单</span>
              </el-menu-item>
              <el-menu-item @click="authStore.logout(); $router.push('/login'); mobileMenuVisible = false">
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </el-menu-item>
            </el-menu>
          </div>
        </template>
        <template v-else>
          <div class="mobile-auth-buttons">
            <el-button type="primary" @click="$router.push('/login'); mobileMenuVisible = false">登录</el-button>
            <el-button type="success" @click="$router.push('/register'); mobileMenuVisible = false">注册</el-button>
          </div>
        </template>
      </div>
    </el-drawer>
    
    <el-main class="main-body">
      <div class="main-container-wrapper">
        <!-- 左侧边栏 (PC Only) -->
        <div class="side-panel left-panel">
          <el-card class="ad-card" :body-style="{ padding: '0px' }">
            <img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&auto=format&fit=crop" class="ad-img">
            <div style="padding: 10px; font-size: 12px; color: #666; text-align: center;">新人专享大礼包</div>
          </el-card>
          <el-card class="ad-card" :body-style="{ padding: '0px' }">
             <div style="padding: 15px; background: #fff7e6; text-align: center;">
               <h4 style="margin:0 0 5px; color:#fa8c16">会员特权</h4>
               <p style="margin:0; font-size:12px; color:#666">免配送费 · 专属红包</p>
             </div>
          </el-card>
        </div>

        <!-- 主内容区 -->
        <div class="main-content">
          <router-view></router-view>
        </div>

        <!-- 右侧边栏 (PC Only) -->
        <div class="side-panel right-panel">
          <el-card class="ad-card" :body-style="{ padding: '0px' }">
             <img src="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&auto=format&fit=crop" class="ad-img">
             <div style="padding: 10px; font-size: 12px; color: #666; text-align: center;">当季新品推荐</div>
          </el-card>
          <el-card class="ad-card">
            <template #header><span style="font-size:14px; font-weight:bold">热门活动</span></template>
            <div style="font-size:12px; line-height: 2;">
              <div style="color: #f56c6c">🔥 周五半价日</div>
              <div style="color: #409EFF">💎 积分兑换商城</div>
              <div style="color: #67c23a">🌱 环保无需餐具</div>
            </div>
          </el-card>
        </div>
      </div>
    </el-main>

    <el-footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 xx外卖 - 让美食触手可及</p>
        <div class="footer-links">
          <a href="#" class="footer-link">关于我们</a>
          <a href="#" class="footer-link">联系我们</a>
          <a href="#" class="footer-link">用户协议</a>
          <a href="#" class="footer-link">隐私政策</a>
        </div>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Food, ShoppingCart, CaretBottom, Shop, Bicycle, List, SwitchButton, User, MagicStick, Menu } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()
const cartCount = ref(0)
const mobileMenuVisible = ref(false)

// 移动端检测
const isMobile = ref(window.innerWidth < 768)

const updateMobileStatus = () => {
  isMobile.value = window.innerWidth < 768
}

// Theme Management
const currentTheme = ref(localStorage.getItem('theme') || 'light')
const themes = [
  { value: 'light', label: '⚪ 简约白' },
  { value: 'dark', label: '⚫ 暗夜黑' },
  { value: 'pink', label: '🌸 樱花粉' },
  { value: 'blue', label: '🌊 海洋蓝' }
]

const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
  currentTheme.value = theme
}

const handleTheme = (theme) => {
  applyTheme(theme)
}

// 优化购物车数量检查逻辑
const updateCartCount = () => {
  try {
    const cart = JSON.parse(localStorage.getItem('cart')) || { items: [] }
    cartCount.value = cart.items.reduce((sum, item) => sum + item.quantity, 0)
  } catch (error) {
    console.error('解析购物车数据失败:', error)
    cartCount.value = 0
  }
}

onMounted(() => {
  updateCartCount()
  // 只在存储变化时更新，减少性能消耗
  window.addEventListener('storage', (e) => {
    if (e.key === 'cart') {
      updateCartCount()
    }
  })
  // 降低轮询频率到 5 秒
  const cartInterval = setInterval(updateCartCount, 5000)
  applyTheme(currentTheme.value) // Apply saved theme
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateMobileStatus)
  
  // 清理函数
  onUnmounted(() => {
    clearInterval(cartInterval)
    window.removeEventListener('storage', updateCartCount)
    window.removeEventListener('resize', updateMobileStatus)
  })
})

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (cmd === 'orders') {
    router.push('/orders')
  } else if (cmd === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: var(--bg-color);
  background-image: var(--bg-image);
  background-attachment: fixed;
  background-size: cover;
  display: flex;
  flex-direction: column;
  transition: background 0.3s;
}

.header {
  background: var(--header-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px var(--shadow-color);
  border-bottom: var(--glass-border);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  height: 70px !important;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.2s;
}

.logo:hover {
  transform: scale(1.02);
}

.logo-box {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #409EFF, #007bff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.3);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-color);
  letter-spacing: 0.5px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.role-btn {
  font-weight: 600;
}

.theme-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--glass-bg);
  border: var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.3s;
  box-shadow: 0 2px 8px var(--shadow-color);
}
.theme-btn:hover { transform: rotate(15deg) scale(1.1); }

.cart-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  background: var(--glass-bg);
  border: var(--glass-border);
  color: var(--text-color);
  transition: all 0.2s;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.cart-btn:hover {
  background: var(--bg-color);
  color: var(--primary-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  background: var(--glass-bg);
  border: var(--glass-border);
  transition: background 0.2s;
}

.username {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color);
}

.dropdown-icon {
  font-size: 12px;
  color: #909399;
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

.main-container-wrapper {
  display: flex;
  justify-content: center;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.side-panel {
  width: 200px;
  display: none; /* Hidden on mobile by default */
}

.main-content {
  flex: 1;
  max-width: 1000px; /* Limit main content width */
  padding: 0;
}

.ad-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
  background: var(--card-bg);
  border: var(--glass-border);
  box-shadow: 0 4px 12px var(--shadow-color);
}
.ad-card:hover { transform: translateY(-2px); }
.ad-img { width: 100%; display: block; }

@media (min-width: 1200px) {
  .side-panel {
    display: block;
  }
}

.footer {
  background: var(--header-bg);
  backdrop-filter: blur(10px);
  border-top: var(--glass-border);
  padding: 20px 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.footer-links {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.footer-link {
  color: #909399;
  text-decoration: none;
  font-size: 12px;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--primary-color);
}

/* 移动端菜单样式 */
.mobile-menu-btn {
  display: none;
}

.mobile-menu-content {
  padding: 20px;
}

.mobile-role-btn {
  width: 100%;
  margin-bottom: 15px;
  font-size: 16px;
  padding: 12px;
}

.mobile-theme-section {
  margin: 20px 0;
}

.mobile-section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: var(--text-color);
}

.mobile-theme-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.mobile-theme-option {
  padding: 12px;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--glass-bg);
}

.mobile-theme-option:hover {
  background: var(--bg-color);
  transform: translateY(-2px);
}

.mobile-theme-option.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.mobile-cart-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: var(--glass-bg);
  border: var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 20px;
}

.mobile-cart-btn:hover {
  background: var(--bg-color);
  color: var(--primary-color);
}

.mobile-user-menu {
  margin-top: 20px;
}

.mobile-auth-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.mobile-auth-buttons .el-button {
  padding: 12px;
  font-size: 16px;
}

/* 响应式设计调整 */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: block;
  }
  
  .nav-right {
    gap: 10px;
  }
  
  .logo-text {
    font-size: 18px;
  }
  
  .logo-box {
    width: 36px;
    height: 36px;
  }
  
  .logo-icon {
    font-size: 20px;
  }
  
  .header-content {
    padding: 0 16px;
  }
  
  .main-container-wrapper {
    padding: 10px;
    gap: 10px;
  }
  
  .footer-links {
    gap: 15px;
  }
  
  .footer-link {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .header {
    height: 60px !important;
  }
  
  .logo {
    gap: 8px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .logo-box {
    width: 32px;
    height: 32px;
  }
  
  .logo-icon {
    font-size: 18px;
  }
  
  .header-content {
    padding: 0 12px;
  }
  
  .main-container-wrapper {
    padding: 8px;
  }
  
  .footer-content p {
    font-size: 12px;
  }
  
  .footer-links {
    gap: 10px;
  }
}

/* 平板设备调整 */
@media (min-width: 769px) and (max-width: 1024px) {
  .side-panel {
    width: 180px;
  }
  
  .main-content {
    max-width: 800px;
  }
  
  .nav-right {
    gap: 20px;
  }
}

/* 大屏幕设备优化 */
@media (min-width: 1400px) {
  .main-container-wrapper {
    max-width: 1600px;
  }
  
  .side-panel {
    width: 250px;
  }
  
  .main-content {
    max-width: 1200px;
  }
}
</style>
