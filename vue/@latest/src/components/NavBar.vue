<template>
  <nav class="navbar">
    <router-link to="/">推荐</router-link>
    <router-link :to="isLoggedIn ? '/follow' : '/login'">关注</router-link>
    <router-link :to="isLoggedIn ? '/profile' : '/login'">个人主页</router-link>
  </nav>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
const { isLoggedIn } = useUserStore()
</script>

<style scoped>
.navbar {
  display: flex;
  gap: 20px;
  padding: 10px;
  background-color: #f5f5f5;
}
</style>
