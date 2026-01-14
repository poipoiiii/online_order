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
        </div>
      </div>
    </el-header>
    
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
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { Food, ShoppingCart, CaretBottom, Shop, Bicycle, List, SwitchButton, User } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()
const cartCount = ref(0)

// 简单的轮询检查购物车数量（实际项目中应使用 Pinia 状态管理购物车）
const updateCartCount = () => {
  const cart = JSON.parse(localStorage.getItem('cart')) || { items: [] }
  cartCount.value = cart.items.reduce((sum, item) => sum + item.quantity, 0)
}

onMounted(() => {
  updateCartCount()
  window.addEventListener('storage', updateCartCount)
  setInterval(updateCartCount, 1000)
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
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
}

.header {
  background: #ffffff;
  box-shadow: 0 4px 20px rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  height: 70px !important;
}

.header-content {
  max-width: 1400px; /* Wider to accommodate sidebars */
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
  color: #2c3e50;
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

.cart-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  background: #f0f2f5;
  color: #606266;
  transition: all 0.2s;
}

.cart-btn:hover {
  background: #e6e8eb;
  color: #409EFF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info:hover {
  background: rgba(0,0,0,0.03);
}

.username {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
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
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}
.ad-card:hover { transform: translateY(-2px); }
.ad-img { width: 100%; display: block; }

@media (min-width: 1200px) {
  .side-panel {
    display: block;
  }
}

.footer {
  background: #fff;
  border-top: 1px solid #eee;
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
</style>
