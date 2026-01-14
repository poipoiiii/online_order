<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <template #header>
        <div class="header">
          <h2>个人中心</h2>
          <el-button type="primary" size="small" @click="isEditing = !isEditing">{{ isEditing ? '取消' : '编辑资料' }}</el-button>
        </div>
      </template>

      <div class="user-info-section">
        <div class="avatar-box">
          <el-avatar :size="80" :src="form.avatar_url || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'"></el-avatar>
          <div v-if="isEditing" style="margin-top: 10px;">
            <el-input v-model="form.avatar_url" placeholder="输入头像URL" size="small"></el-input>
          </div>
        </div>
        
        <el-form :model="form" label-width="80px" class="user-form" :disabled="!isEditing">
          <el-form-item label="用户名">
            <el-input v-model="form.username"></el-input>
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" disabled></el-input>
          </el-form-item>
          <el-form-item label="电话">
            <el-input v-model="form.phone"></el-input>
          </el-form-item>
          <el-form-item v-if="isEditing">
            <el-button type="primary" @click="updateProfile">保存修改</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :md="12" :xs="24">
        <el-card class="section-card">
          <template #header>
            <div class="header">
              <span>收货地址</span>
              <el-button link type="primary" @click="openAddressDialog()">新增地址</el-button>
            </div>
          </template>
          <el-table :data="addresses" style="width: 100%" size="small">
            <el-table-column prop="name" label="联系人" width="80"></el-table-column>
            <el-table-column prop="phone" label="电话" width="110"></el-table-column>
            <el-table-column prop="address" label="地址"></el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button link type="primary" size="small" @click="openAddressDialog(scope.row)">编辑</el-button>
                <el-button link type="danger" size="small" @click="deleteAddress(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :md="12" :xs="24">
        <el-card class="section-card">
          <template #header>
            <div class="header">
              <span>我的优惠券</span>
            </div>
          </template>
          <el-empty v-if="coupons.length === 0" description="暂无优惠券"></el-empty>
          <div v-else class="coupon-list">
            <div v-for="c in coupons" :key="c.id" class="coupon-item">
              <div class="amount">￥{{ c.coupon.discount }}</div>
              <div class="info">
                <div class="code">{{ c.coupon.code }}</div>
                <div class="date">有效期至 {{ formatDate(c.coupon.valid_to) }}</div>
              </div>
              <el-tag size="small" :type="c.is_used ? 'info' : 'success'">{{ c.is_used ? '已使用' : '未使用' }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 地址弹窗 -->
    <el-dialog v-model="addressDialogVisible" :title="isEditAddress ? '编辑地址' : '新增地址'" width="90%" style="max-width: 500px">
      <el-form :model="addressForm" label-width="80px">
        <el-form-item label="联系人">
          <el-input v-model="addressForm.name"></el-input>
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="addressForm.phone"></el-input>
        </el-form-item>
        <el-form-item label="详细地址">
          <el-input v-model="addressForm.address" placeholder="请输入详细地址">
            <template #append>
              <el-button @click="autoLocate">
                <el-icon><Location /></el-icon> 定位
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="addressForm.is_default"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addressDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAddress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Location } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { getCurrentLocation } from '../utils/location'

const authStore = useAuthStore()
const isEditing = ref(false)
const form = ref({})
const addresses = ref([])
const coupons = ref([])

// Address Form
const addressDialogVisible = ref(false)
const isEditAddress = ref(false)
const addressForm = ref({})

onMounted(() => {
  fetchProfile()
  fetchAddresses()
  fetchCoupons()
})

const fetchProfile = async () => {
  // 假设后端支持 /api/users/me/
  try {
    const res = await axios.get('/api/users/me/')
    form.value = { ...res.data, avatar_url: res.data.avatar } // 简化处理
  } catch (e) {
    // fallback
    form.value = { ...authStore.user }
  }
}

const updateProfile = async () => {
  try {
    await axios.patch('/api/users/me/', {
      username: form.value.username,
      phone: form.value.phone,
      // avatar: form.value.avatar_url // 实际需要处理文件上传或URL
    })
    ElMessage.success('资料已更新')
    isEditing.value = false
    authStore.user.username = form.value.username // 简单同步 store
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const fetchAddresses = async () => {
  try {
    const res = await axios.get('/api/addresses/')
    addresses.value = res.data
  } catch (e) {}
}

const openAddressDialog = (addr = null) => {
  if (addr) {
    isEditAddress.value = true
    addressForm.value = { ...addr }
  } else {
    isEditAddress.value = false
    addressForm.value = { name: '', phone: '', address: '', is_default: false }
  }
  addressDialogVisible.value = true
}

const autoLocate = async () => {
  try {
    ElMessage.info('正在定位...')
    const loc = await getCurrentLocation()
    addressForm.value.address = loc.address
    ElMessage.success('定位成功')
  } catch (e) {
    ElMessage.error('定位失败: ' + e.message)
  }
}

const saveAddress = async () => {
  try {
    if (isEditAddress.value) {
      await axios.put(`/api/addresses/${addressForm.value.id}/`, addressForm.value)
    } else {
      await axios.post('/api/addresses/', addressForm.value)
    }
    addressDialogVisible.value = false
    ElMessage.success('保存成功')
    fetchAddresses()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteAddress = (id) => {
  ElMessageBox.confirm('确定删除吗?', '提示').then(async () => {
    await axios.delete(`/api/addresses/${id}/`)
    fetchAddresses()
  })
}

const fetchCoupons = async () => {
  try {
    const res = await axios.get('/api/user_coupons/')
    coupons.value = res.data
  } catch (e) {}
}

const formatDate = (str) => new Date(str).toLocaleDateString()
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header h2 { margin: 0; font-size: 18px; }
.user-info-section {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}
.avatar-box {
  text-align: center;
}
.user-form {
  flex: 1;
  max-width: 400px;
}
.section-card {
  margin-bottom: 20px;
}
.coupon-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #f0f0f0;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
  background: #fdfdfd;
}
.coupon-item .amount {
  color: #f56c6c;
  font-weight: bold;
  font-size: 18px;
}
.coupon-item .info {
  flex: 1;
  margin-left: 10px;
}
.coupon-item .code { font-weight: bold; font-size: 14px; }
.coupon-item .date { font-size: 12px; color: #999; }

@media (max-width: 768px) {
  .user-info-section {
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  .user-form {
    width: 100%;
  }
}
</style>
