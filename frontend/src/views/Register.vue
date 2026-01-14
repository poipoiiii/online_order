<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>注册</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email"></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="顾客" value="customer"></el-option>
            <el-option label="商家" value="merchant"></el-option>
            <el-option label="骑手" value="rider"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="店铺地址" v-if="form.role === 'merchant'">
          <el-input v-model="form.address" placeholder="请选择或输入店铺地址">
            <template #append>
              <el-button @click="handleLocate">
                <el-icon><Location /></el-icon> 定位
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister">注册</el-button>
          <el-button @click="$router.push('/login')">返回登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location } from '@element-plus/icons-vue'
import { getCurrentLocation } from '../utils/location'

const form = ref({ username: '', password: '', email: '', role: 'customer', address: '', lat: null, lng: null })
const authStore = useAuthStore()
const router = useRouter()

const handleLocate = async () => {
  try {
    ElMessage.info('正在定位...')
    const loc = await getCurrentLocation()
    form.value.address = loc.address
    form.value.lat = loc.lat
    form.value.lng = loc.lng
    ElMessage.success('定位成功')
  } catch (e) {
    ElMessage.error('定位失败: ' + e.message)
  }
}

const handleRegister = async () => {
  try {
    await authStore.register(form.value)
    ElMessage.success('注册成功')
    const role = authStore.role
    if (role === 'merchant') router.push('/merchant')
    else if (role === 'rider') router.push('/rider')
    else router.push('/')
  } catch (error) {
    ElMessage.error('注册失败')
  }
}
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; }
.login-card { width: 400px; }
</style>
