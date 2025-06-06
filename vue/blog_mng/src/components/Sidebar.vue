<template>
  <div class="sidebar">
    <h2 class="title">后台系统</h2>
    <ul class="menu">
      <li @click="$emit('show-profile')">个人信息</li>
      <li @click="$emit('show-managers')">管理员管理</li>
      <li @click="$emit('show-users')">用户管理</li>
      <li @click="$emit('show-articles')">文章管理</li>
      <li @click="$emit('show-comments')">评论管理</li> 
    </ul>
  </div>
</template>

<style scoped>
.title {
  font-size: 22px;
  margin-bottom: 30px;
  font-weight: bold;
}

.menu {
  list-style: none;
  padding: 0;
}

.menu li {
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.menu li:hover {
  background-color: #34495e;
}
</style>
