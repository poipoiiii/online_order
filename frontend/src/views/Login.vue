<template>
  <div class="login-container">
    <!-- Theme Switcher -->
    <div class="theme-switcher">
      <el-dropdown @command="handleTheme" trigger="click">
        <el-button circle size="large" class="theme-btn">
          <el-icon><MagicStick /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="light">⚪ 简约白</el-dropdown-item>
            <el-dropdown-item command="dark">⚫ 暗夜黑</el-dropdown-item>
            <el-dropdown-item command="pink">🌸 樱花粉</el-dropdown-item>
            <el-dropdown-item command="blue">🌊 海洋蓝</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <el-card class="login-card glass-effect">
      <div class="login-header">
        <el-icon class="logo-icon"><Food /></el-icon>
        <h2>欢迎登录</h2>
      </div>
      <el-form :model="form" label-width="0" size="large">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="用户名" 
            prefix-icon="User"
            class="custom-input"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="Lock" 
            show-password
            class="custom-input"
            @keyup.enter="handleLogin"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" class="submit-btn" :loading="loading">登录</el-button>
        </el-form-item>
        <div class="form-footer">
          <span>还没有账号？</span>
          <el-button type="primary" link @click="$router.push('/register')">立即注册</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Food, MagicStick } from '@element-plus/icons-vue'

const form = ref({ username: '', password: '' })
const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    const role = authStore.role
    if (role === 'merchant') router.push('/merchant')
    else if (role === 'rider') router.push('/rider')
    else router.push('/')
  } catch (error) {
    ElMessage.error('登录失败: ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// Theme Management
const handleTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'light'
  document.documentElement.setAttribute('data-theme', savedTheme)
})
</script>

<style scoped>
.login-container { 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  height: 100vh;
  background-color: var(--bg-color);
  background-image: var(--bg-image);
  background-size: cover;
  transition: background 0.3s;
}

.theme-switcher {
  position: absolute;
  top: 20px;
  right: 20px;
}

.theme-btn {
  background: var(--glass-bg) !important;
  border: var(--glass-border) !important;
  color: var(--text-color) !important;
}

.login-card { 
  width: 400px;
  padding: 20px;
  border-radius: 16px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border: var(--glass-border);
  box-shadow: 0 8px 32px var(--shadow-color);
  color: var(--text-color);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 48px;
  color: var(--primary-color);
  margin-bottom: 10px;
}

.login-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  background: var(--logo-bg);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.custom-input :deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.5);
  box-shadow: none;
  border: 1px solid transparent;
  transition: all 0.3s;
}

[data-theme='dark'] .custom-input :deep(.el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.3);
}

.custom-input :deep(.el-input__wrapper:hover),
.custom-input :deep(.el-input__wrapper.is-focus) {
  background-color: var(--bg-color);
  box-shadow: 0 0 0 1px var(--primary-color) inset;
}

.submit-btn {
  width: 100%;
  border-radius: 20px;
  font-weight: bold;
  height: 44px;
  font-size: 16px;
  background: var(--logo-bg);
  border: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.form-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}
</style>
