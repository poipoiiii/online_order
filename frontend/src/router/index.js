import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Layout from '../views/Layout.vue'
import Home from '../views/Home.vue'
import ShopDetail from '../views/ShopDetail.vue'
import Cart from '../views/Cart.vue'
import Orders from '../views/Orders.vue'
import Payment from '../views/Payment.vue'
import SearchResult from '../views/SearchResult.vue'
import Profile from '../views/Profile.vue'
import MerchantDashboard from '../views/merchant/Dashboard.vue'
import RiderDashboard from '../views/rider/Dashboard.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { 
    path: '/', 
    component: Layout,
    children: [
      { path: '', component: Home }, 
      { path: 'search', component: SearchResult },
      { path: 'shop/:id', component: ShopDetail },
      { path: 'cart', component: Cart },
      { path: 'orders', component: Orders },
      { path: 'payment/:id', component: Payment },
      { path: 'profile', component: Profile },
      { path: 'merchant', component: MerchantDashboard },
      { path: 'rider', component: RiderDashboard },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
