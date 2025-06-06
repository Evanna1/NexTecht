<template>
  <div class="user-list-container">
    <!-- 增加用户信息标题栏 -->
    <div class="user-info-header">
      <div class="user-avatar">
        <img :src="userInfo.avatar" alt="用户头像" class="user-avatar-img">
      </div>
      <div class="user-info-details">
        <h2 class="user-name">{{ ownerUsername }}</h2>
        <p class="user-id">ID: {{ ownerId }}</p>
      </div>
    </div>

    <div class="header-container">
      <h2 class="list-title">{{ isFollowers ? '粉丝列表' : '关注列表' }}</h2>
      <button class="back-button" @click="backToList">
        <svg viewBox="0 0 24 24" fill="currentColor" class="back-icon">
          <path fill-rule="evenodd" d="M15.79 6.70a1 1 0 010 1.41l-5.58 5.59a1 1 0 01-1.42 0L6.21 8.11a1 1 0 111.42-1.42l4.87 4.88 5.58-5.59a1 1 0 011.42 0z" clip-rule="evenodd" />
        </svg>
        返回
      </button>
    </div>

    <div class="filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" placeholder="搜索">
        <select v-model="searchField">
          <option value="username">用户名</option>
          <option value="id">ID</option>
          <option value="nickname">昵称</option>
          <option value="email">邮箱</option>
          <option value="phone">手机号</option>
          <option value="create_at">注册时间</option>
          <option value="last_login_at">最后登录</option>
        </select>
      </div>

      <div class="filter-select">
        <label for="status-filter">状态:</label>
        <select id="status-filter" v-model="statusFilter">
          <option value="">全部</option>
          <option value="0">正常</option>
          <option value="1">封禁</option>
        </select>
      </div>

      <div class="filter-select">
        <label for="gender-filter">性别:</label>
        <select id="gender-filter" v-model="genderFilter">
          <option value="">全部</option>
          <option value="男">男</option>
          <option value="女">女</option>
          <option value="保密">保密</option>
        </select>
      </div>

      <div class="filter-select">
        <label for="online-filter">在线:</label>
        <select id="online-filter" v-model="onlineFilter">
          <option value="">全部</option>
          <option value="true">在线</option>
          <option value="false">离线</option>
        </select>
      </div>

      <div class="filter-select">
        <label for="relation-filter">关系:</label>
        <select id="relation-filter" v-model="relationFilter">
          <option value="">全部</option>
          <option value="互相关注">互相关注</option>
          <option value="已关注">已关注</option>
          <option value="未关注">未关注</option>
        </select>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>头像</th>
            <th>性别</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>注册时间</th>
            <th>最后登录</th>
            <th>在线</th>
            <th>状态</th>
            <th>关系</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in filteredUserList" :key="user.id" :class="{ 'first-row': index === 0 }">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.nickname }}</td>
            <td>
              <div class="avatar-container">
                <img :src="user.avatar" alt="头像" class="avatar">
              </div>
            </td>
            <td>{{ user.gender }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone }}</td>
            <td>{{ formatDate(user.create_at) }}</td>
            <td>{{ formatDate(user.last_login_at) }}</td>
            <td>
              <span :class="['status-dot', user.is_online ? 'online' : 'offline']"></span>
              {{ user.is_online ? '在线' : '离线' }}
            </td>
            <td>
              <span :class="['status-badge', user.u_status === 0 ? 'normal' : 'blocked']">
                {{ user.u_status === 0 ? '正常' : '封禁' }}
              </span>
            </td>
            <td>
              <span class="relation-tag">{{ relationMap[user.id] }}</span>
            </td>
          </tr>
          <tr v-if="filteredUserList.length === 0">
            <td colspan="12" class="no-data">没有符合条件的用户</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    userId: {
      type: Number,
      required: true
    },
    isFollowers: {
      type: Boolean,
      required: true
    },
    ownerUsername: {
      type: String,
      required: true
    },
    ownerId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      userList: [],
      relationMap: {},
      searchKeyword: '',
      searchField: 'username',
      statusFilter: '',
      genderFilter: '',
      onlineFilter: '',
      relationFilter: '',
      userInfo: {
        avatar: 'https://via.placeholder.com/150', // 默认头像URL
      }
    };
  },
  computed: {
    filteredUserList() {
      return this.userList.filter(user => {
        // 搜索框的过滤
        let searchMatch = true;
        if (this.searchKeyword) {
          const keyword = this.searchKeyword.toLowerCase();
          const value = user[this.searchField] || '';
          searchMatch = value.toString().toLowerCase().includes(keyword);
        }

        // 下拉框的过滤
        const statusMatch = this.statusFilter === '' || user.u_status.toString() === this.statusFilter;
        const genderMatch = this.genderFilter === '' || user.gender === this.genderFilter;
        const onlineMatch = this.onlineFilter === '' || user.is_online.toString() === this.onlineFilter;
        const relationMatch = this.relationFilter === '' || this.relationMap[user.id] === this.relationFilter;

        return searchMatch && statusMatch && genderMatch && onlineMatch && relationMatch;
      });
    }
  },
  async created() {
    await this.fetchUserList();
    await this.fetchRelations();
    await this.fetchUserInfo(); // 新增获取用户信息的方法
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchUserList() {
      try {
        const token = localStorage.getItem('token');
        const endpoint = this.isFollowers
          ? `/manager/followers/${this.userId}`
          : `/manager/following/${this.userId}`;
        const response = await axios.get(`http://localhost:5000${endpoint}`, {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        if (response.data.state === 1) {
          this.userList = this.isFollowers ? response.data.followers : response.data.following;
        } else {
          alert('获取用户列表失败: ' + response.data.message);
        }
      } catch (error) {
        console.error('获取用户列表失败:', error);
        alert('获取用户列表失败，请稍后再试');
      }
    },
    async fetchRelations() {
      try {
        const token = localStorage.getItem('token');
        const relations = {};
        for (const user of this.userList) {
          const response = await axios.get(
            `http://localhost:5000/friends/${user.id}`,
            {
              headers: {
                'Authorization': 'Bearer ' + token
              }
            }
          );
          relations[user.id] = response.data.is_mutual ? '互相关注' : (response.data.is_following ? '已关注' : '未关注');
        }
        this.relationMap = relations;
      } catch (error) {
        console.error('获取用户关系失败:', error);
        alert('获取用户关系失败，请稍后再试');
      }
    },
    async fetchUserInfo() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/users/${this.ownerId}`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.userInfo = response.data.user;
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
      }
    },
    backToList() {
      this.$emit('back-to-list');
    },
  }
}
</script>

<style scoped>
/* 保持原有样式不变，只添加新的样式 */
.user-list-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.user-info-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 16px;
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.user-id {
  font-size: 14px;
  color: #718096;
  margin-top: 4px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-title {
  font-size: 22px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.back-button {
  background-color: #fff;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #4a5568;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
}

.back-button:hover {
  background-color: #f7fafc;
  border-color: #cbd5e0;
}

.back-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  color: #4a5568;
}

.filter-container {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
  flex-grow: 1;
  max-width: 300px;
  background-color: #fff;
}

.search-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  color: #a0aec0;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 14px;
  color: #2d3748;
  flex-grow: 1;
  background-color: transparent;
}

.search-box select {
  border: none;
  outline: none;
  font-size: 14px;
  color: #2d3748;
  margin-left: 8px;
  background-color: transparent;
  cursor: pointer;
}

.filter-select {
  display: flex;
  align-items: center;
  background-color: #f7fafc;
  border-radius: 8px;
  padding: 8px 12px;
}

.filter-select label {
  font-size: 14px;
  color: #718096;
  margin-right: 8px;
  white-space: nowrap;
}

.filter-select select {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  color: #2d3748;
  background-color: #fff;
  min-width: 120px;
  cursor: pointer;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #4a5568;
  white-space: nowrap;
}

.user-table thead {
  background-color: #f7fafc;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.user-table th {
  font-weight: 600;
  color: #4a5568;
  padding: 14px 16px;
  text-align: left;
}

.user-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #edf2f7;
}

.user-table tbody tr:nth-child(even) {
  background-color: #fafafa;
}

.user-table tbody tr:hover {
  background-color: #f0f7ff;
  transition: background-color 0.2s ease-in-out;
}

.avatar-container {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

.online {
  background-color: #48bb78;
}

.offline {
  background-color: #e53e3e;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.normal {
  background-color: #e6f7ee;
  color: #2d6a4f;
}

.blocked {
  background-color: #fef2f2;
  color: #c53030;
}

.relation-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #4a5568;
  background-color: #edf2f7;
  border: 1px solid #e2e8f0;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #a0aec0;
  font-size: 14px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-box {
    max-width: 100%;
    width: 100%;
    margin-bottom: 12px;
  }
  
  .filter-select {
    width: 100%;
    margin-bottom: 12px;
  }
  
  .user-table {
    font-size: 12px;
  }
  
  .user-table th,
  .user-table td {
    padding: 8px 12px;
  }
}
</style>