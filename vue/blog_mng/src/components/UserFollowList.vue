<template>
  <div class="user-list-container">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h2 class="list-title">用户 {{ userInfo || '未知用户' }} (ID: {{ userId }})的{{ isFollowers ? '粉丝列表' : '关注列表' }}</h2>
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
            <td>
              <a @click="showUserInfo(user.id)" class="clickable">{{ user.id }}</a>
            </td>
            <td>
              <a @click="showUserInfo(user.id)" class="clickable">{{ user.username }}</a>
            </td>
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
    ownerUsername: { // 这个 prop 在你的 template 和 script 中未使用，可以考虑移除或根据需求使用
      type: String,
      required: true
    },
    ownerId: { // 这个 prop 在你的 template 和 script 中未使用，可以考虑移除或根据需求使用
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
      userInfo: { nickname: '未知用户' }, // 初始值，确保在获取到数据前有默认显示
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
        // 注意：布尔值与字符串 'true'/'false' 的比较
        const onlineMatch = this.onlineFilter === '' || user.is_online.toString() === this.onlineFilter;
        const relationMatch = this.relationFilter === '' || this.relationMap[user.id] === this.relationFilter;

        return searchMatch && statusMatch && genderMatch && onlineMatch && relationMatch;
      });
    }
  },
  // 在 `created` 钩子中只做初始化操作，数据加载由 `watch` 控制
  created() {
    this.fetchUserInfo(); // 用户信息在组件创建时获取一次即可
  },
  watch: {
    // 监听 isFollowers 变化，决定加载粉丝还是关注列表
    isFollowers: {
      handler() {
        this.resetAndFetchData();
      },
      immediate: true, // 立即执行一次，确保组件首次渲染时根据 isFollowers 的初始值加载数据
    },
    // 监听 userId 变化，如果用户 ID 改变，也需要重新加载数据和用户信息
    userId: {
      handler() {
        this.fetchUserInfo(); // 用户 ID 改变时重新获取用户信息
        this.resetAndFetchData();
      },
      immediate: true, // 立即执行一次，确保组件首次渲染时根据 userId 的初始值加载数据
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    // 封装重置数据并获取列表和关系的逻辑
    async resetAndFetchData() {
      this.userList = []; // 清空当前列表数据
      this.relationMap = {}; // 清空关系映射
      // 重置筛选条件，可选，看你的业务需求是否每次切换列表都重置筛选
      this.searchKeyword = '';
      this.statusFilter = '';
      this.genderFilter = '';
      this.onlineFilter = '';
      this.relationFilter = '';

      await this.fetchUserList();
      await this.fetchRelations();
    },
    async fetchUserInfo() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.userInfo = response.data.user;
        } else {
          console.error('获取用户信息失败:', response.data.message);
          this.userInfo = { nickname: '未知用户' };
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.userInfo = { nickname: '未知用户' };
      }
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
          // 根据 isFollowers 属性来正确赋值 userList
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
        // 遍历当前 userList 中的用户，获取他们的关系
        for (const user of this.userList) {
          const response = await axios.get(
            `http://localhost:5000/friends/${user.id}`, // 这里应该是当前登录用户与列表中用户的关系，如果 API 是这样设计的
            {
              headers: {
                'Authorization': 'Bearer ' + token
              }
            }
          );
          // 根据 API 返回判断关系，假设 is_mutual 和 is_following 是从当前登录用户视角判断的
          relations[user.id] = response.data.is_mutual ? '互相关注' : (response.data.is_following ? '已关注' : '未关注');
        }
        this.relationMap = relations;
      } catch (error) {
        console.error('获取用户关系失败:', error);
        alert('获取用户关系失败，请稍后再试');
      }
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    backToList() {
      this.$emit('back-to-list');
    },
  }
}
</script>

<style scoped>
.user-list-container {
  padding: 24px;
  background-color: #fff; /* 容器背景色改为白色 */
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.list-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
  text-align: center;
  flex-grow: 1;
}

.back-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  margin-bottom: 20px;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.back-button:hover {
  background-color: #4a90c2;
}

.filter-container {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

/* 移除 .search-filter-container 样式，因为它在 template 中不存在 */
/* .search-filter-container {
  display: flex;
  gap: 2px;
  align-items: center;
  position: absolute;
  top: 140px;
  right: 24px;
} */

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px 12px;
  background-color: #fff;
}

.search-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  color: #888;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
  flex-grow: 1;
}

.search-box select {
  border: none;
  outline: none;
  font-size: 14px;
  color: #333;
  margin-left: 10px;
  background-color: transparent;
}

.filter-select {
  display: flex;
  align-items: center;
}

.filter-select label {
  font-size: 14px;
  color: #555;
  margin-right: 8px;
}

.filter-select select {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg fill='none' viewBox='0 0 24 24' stroke='currentColor'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7' /%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position-x: 100%;
  background-position-y: 50%;
  padding-right: 24px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.user-table thead {
  background-color: #f2f2f2; /* 表头浅灰色 */
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.user-table th {
  font-weight: 600;
  color: #555;
}

.user-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #eee;
}

.user-table tbody tr {
  background-color: #fff; /* 奇数行或没有指定时的背景色 */
}

.user-table tbody tr:nth-child(even) {
  background-color: #f9f9f9; /* 偶数行背景设置为更浅的灰色 */
}

.user-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.avatar-container {
  width: 32px;
  height: 32px;
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
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.online {
  background-color: #5cb85c;
}

.offline {
  background-color: #d9534f;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.normal {
  background-color: #dff0d8;
  color: #3c763d;
}

.blocked {
  background-color: #fdecea;
  color: #d9534f;
}

.relation-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #555;
  background-color: #f8f8f8;
  border: 1px solid #eee;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

.user-table td a {
  color: #5ea8da; /* 浅蓝色 */
  text-decoration: none;
}

</style>