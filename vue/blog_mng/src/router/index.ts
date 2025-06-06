import { createRouter, createWebHistory } from 'vue-router'
import AdminLogin from '../views/AdminLogin.vue'
import Dashboard from '../views/Dashboard.vue'
import ArticleDetail from '../components/ArticleDetail.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: AdminLogin },
  { path: '/bashbord', component:Dashboard }, // ✅ 管理员后台页面
  { path: '/article-detail/:articleId',component: ArticleDetail }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
