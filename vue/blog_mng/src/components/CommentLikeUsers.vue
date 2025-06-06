<template>
  <div class="comment-like-users-container">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h2 class="list-title">点赞评论(ID: {{ this.commentId }})的用户列表</h2>
    </div>

    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterLikeUsers" placeholder="输入关键词搜索用户...">
      </div>
      <div class="filter-select">
        <select v-model="searchField" id="search-field" @change="filterLikeUsers">
          <option value="">不限</option>
          <option value="user_id">用户ID</option>
          <option value="username">用户名</option>
          <option value="nickname">昵称</option>
          <option value="like_time">点赞时间</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>
    <div v-else class="content-wrapper">
      <div class="comment-info-card">
        <h3>评论内容：</h3>
        <h3><span class="comment-content-text">{{ commentContent }}</span></h3>
        <p>点赞数：<span class="like-count-number">{{ likeCount }}</span></p>
      </div>

      <div class="table-wrapper">
        <table class="like-users-table">
          <thead>
            <tr>
              <th>用户ID</th>
              <th>用户名</th>
              <th>昵称</th>
              <th>头像</th>
              <th>点赞时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredLikeUsers" :key="user.user_id">
              <td>
                <a @click="showUserInfo(user.user_id)" class="table-link">{{ user.user_id }}</a>
              </td>
              <td>
                <a @click="showUserInfo(user.user_id)" class="table-link">{{ user.username }}</a>
              </td>
              <td>{{ user.nickname }}</td>
              <td>
                <div class="avatar-container">
                  <img :src="user.avatar || 'default_avatar.png'" :alt="user.nickname" class="avatar">
                </div>
              </td>
              <td>{{ formatDate(user.like_time) }}</td>
            </tr>
            <tr v-if="filteredLikeUsers.length === 0">
              <td colspan="5" class="no-data">{{ searchKeyword || searchField ? '没有符合条件的用户' : '暂无用户点赞此评论' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
// ... (script 和 style 部分保持不变) ...
import axios from 'axios';

export default {
  props: {
    commentId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      commentContent: '',
      likeCount: 0,
      likeUsers: [], // 原始数据
      isLoading: false,
      searchKeyword: '', // 搜索关键词
      searchField: '',   // 搜索字段
      filteredLikeUsers: [] // 过滤后的数据
    };
  },
  created() {
    this.loadCommentLikeUsers();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async loadCommentLikeUsers() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.commentId}/likes`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.commentContent = data.comment_content;
          this.likeCount = data.like_count;
          this.likeUsers = data.like_users; // 存储原始数据
          this.filteredLikeUsers = [...this.likeUsers]; // 初始化过滤数据
        } else {
          console.error('获取评论点赞用户失败:', data.message);
        }
      } catch (error) {
        console.error('请求评论点赞用户接口失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    // 过滤用户列表的逻辑
    filterLikeUsers() {
      const keyword = this.searchKeyword.toLowerCase();

      if (!keyword && !this.searchField) {
        this.filteredLikeUsers = [...this.likeUsers]; // 如果没有关键词和搜索字段，显示所有数据
        return;
      }

      this.filteredLikeUsers = this.likeUsers.filter(user => {
        // 如果指定了搜索字段
        if (this.searchField) {
          let value;
          if (this.searchField === 'user_id') {
            value = String(user.user_id);
          } else if (this.searchField === 'username') {
            value = user.username;
          } else if (this.searchField === 'nickname') {
            value = user.nickname;
          } else if (this.searchField === 'like_time') {
            value = this.formatDate(user.like_time);
          }
          return value && value.toLowerCase().includes(keyword);
        } else {
          // 如果没有指定搜索字段（不限），则搜索所有相关字段
          return (
            String(user.user_id).toLowerCase().includes(keyword) ||
            user.username.toLowerCase().includes(keyword) ||
            (user.nickname && user.nickname.toLowerCase().includes(keyword)) || // 昵称可能为空
            this.formatDate(user.like_time).toLowerCase().includes(keyword)
          );
        }
      });
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
/* ... (样式部分保持不变) ... */
.comment-like-users-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
  text-align: left;
}

.back-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 10;
}

.back-button:hover {
  background-color: #4a90c2;
}

.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  margin-top: 10px; /* 调整标题与顶部距离 */
}

.list-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

/* 搜索和筛选样式 */
.search-filter-container {
  display: flex;
  gap: 10px; /* 增加搜索框和下拉菜单之间的距离 */
  align-items: center;
  position: absolute;
  top: 285px; /* 根据实际标题高度调整 */
  right: 24px;
}

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
  width: 200px; /* 调整输入框宽度 */
}

.filter-select {
  display: flex;
  align-items: center;
}

.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 7px 10px; /* 调整下拉菜单内边距 */
  font-size: 14px;
  color: #333;
  background-color: #fff;
  appearance: none; /* 移除默认的下拉箭头 */
  background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2020%2020%22%3E%3Cpath%20fill%3D%22%23666%22%20d%3D%22M5.293%207.293L10%2012l4.707-4.707a1%201%200%20011.414%201.414l-5.414%205.414a1%201%200%2001-1.414%200L3.879%208.707a1%201%200%20011.414-1.414z%22%2F%3E%3C%2Fsvg%3E');
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 12px;
  padding-right: 25px; /* 为箭头留出空间 */
}


.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 12px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #5ea8da;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.content-wrapper {
  margin-top: 50px; /* 调整内容与顶部搜索框的间距 */
}

.comment-info-card {
  background-color: #f8fafd;
  border: 1px solid #e0e9f1;
  border-radius: 8px;
  padding: 15px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.comment-info-card h3 {
  font-size: 18px;
  color: #333;
  margin-top: 0;
  margin-bottom: 10px;
  font-weight: 500;
}

.comment-info-card p {
  font-size: 16px;
  color: #555;
  margin-bottom: 0;
}

.comment-content-text {
  font-weight: 600;
  color: #000;
}

.like-count-number {
  font-weight: 600;
  color: #000;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 80px;
}

.like-users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.like-users-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.like-users-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.like-users-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.like-users-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.like-users-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.table-link {
  color: #5ea8da;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease-in-out;
}

.table-link:hover {
  color: #4a90c2;
  text-decoration: underline;
}

.avatar-container {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style>