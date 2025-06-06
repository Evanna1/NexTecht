import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import FollowView from '@/views/FollowView.vue'
import ProfileView from '@/views/ProfileView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import CreatePostView from '@/views/CreatePostView.vue' 
import OtherUserProfile from '../views/OtherUserProfile.vue'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/follow', component: FollowView, meta: { requiresAuth: true } },
  { path: '/profile', component: ProfileView},
  { path: '/create', component: CreatePostView}, 
  { path: '/post/:id', component: () => import('@/views/PostDetail.vue'),},
  { path: '/my-profile', name: 'MyProfile', component: ProfileView, },
  { path: '/user/:userId', name: 'OtherUserProfile', component: OtherUserProfile,}
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
