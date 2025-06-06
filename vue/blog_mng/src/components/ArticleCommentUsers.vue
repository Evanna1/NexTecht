<template>
  <div class="article-comment-users">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h2 class="comments-title">文章(ID:{{ this.articleId }})的评论用户</h2>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterComments" placeholder="输入关键词搜索...">
      </div>
      <div class="filter-select">
        <select v-model="searchField" id="search-field">
          <option value="">不限</option>
          <option value="user_info.id">用户ID</option>
          <option value="user_info.username">用户名</option>
          <option value="comment_content">评论内容</option>
          <option value="comment_create_time">评论时间</option>
        </select>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else class="comments-content">
      <div class="table-wrapper">
        <table class="comments-table">
          <thead>
            <tr>
              <th>用户ID</th>
              <th>用户名</th>
              <th>昵称</th>
              <th>头像</th>
              <th>评论ID</th>
              <th>评论内容</th>
              <th>评论时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="commentUser in filteredCommentUsers" :key="commentUser.comment_id">
              <td>
                <a @click="showUserInfo(commentUser.user_info.id)">{{ commentUser.user_info.id }}</a>
              </td>
              <td>
                <a @click="showUserInfo(commentUser.user_info.id)">{{ commentUser.user_info.username }}</a>
              </td>
              <td>{{ commentUser.user_info.nickname }}</td>
              <td>{{ commentUser.user_info.avatar }}</td>
              <td>
                <a @click="showCommentDeatail(commentUser.comment_id)">{{ commentUser.comment_id }}</a>
              </td>
              <td>{{ commentUser.comment_content }}</td>
              <td>{{ formatDate(commentUser.comment_create_time) }}</td>
            </tr>
            <tr v-if="filteredCommentUsers.length === 0">
              <td colspan="7" class="no-data">没有符合条件的评论记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    articleId: {
      type: [String, Number],
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    initialCommentUsers: { // 新增 prop 以支持初始数据
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      commentUsers: this.initialCommentUsers,
      localIsLoading: false,
      searchKeyword: '',
      searchField: '',
      filteredCommentUsers: [...this.initialCommentUsers] // 初始化为所有评论记录
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  watch: {
    articleId: {
      immediate: true,
      handler(newVal) {
        if (newVal && !this.initialCommentUsers.length) { // 仅当没有初始数据时才调用 API
          this.fetchArticleCommentUsers();
        }
      }
    },
    initialCommentUsers(newVal) { // 监听 initialCommentUsers 的变化
      this.commentUsers = newVal;
      this.filteredCommentUsers = [...newVal]; // 当 initialCommentUsers 更新时，重置 filteredCommentUsers
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchArticleCommentUsers() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/article/${this.articleId}/comment-users`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.commentUsers = response.data.comment_users;
          this.filteredCommentUsers = [...this.commentUsers]; // 获取数据后初始化 filteredCommentUsers
        }
      } catch (error) {
        console.error('获取文章评论用户列表失败:', error);
        alert('获取文章评论用户列表失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
    },
    filterComments() {
      if (!this.searchKeyword) {
        this.filteredCommentUsers = [...this.commentUsers];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredCommentUsers = this.commentUsers.filter(commentUser => {
        if (!this.searchField) {
          return (
            (commentUser.user_info.id && commentUser.user_info.id.toString().toLowerCase().includes(keyword)) ||
            (commentUser.user_info.username && commentUser.user_info.username.toLowerCase().includes(keyword)) ||
            (commentUser.comment_content && commentUser.comment_content.toLowerCase().includes(keyword)) ||
            (commentUser.comment_create_time && this.formatDate(commentUser.comment_create_time).toLowerCase().includes(keyword))
          );
        } else {
          let value = '';
          if (this.searchField.startsWith('user_info.')) {
            const nestedField = this.searchField.split('.')[1];
            value = commentUser.user_info[nestedField];
          } else {
            value = commentUser[this.searchField];
          }

          if (this.searchField === 'comment_create_time') {
            return value && this.formatDate(value).toLowerCase().includes(keyword);
          }

          return value && value.toString().toLowerCase().includes(keyword);
        }
      });
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    showCommentDeatail(commentId) {
      this.$emit('show-comment-detail', commentId);
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
.article-comment-users {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative; /* 使其内部元素可以使用 absolute 定位 */
  text-align: left; /* 内容默认左对齐 */
}

.header-container {
  display: flex;
  justify-content: center; /* 标题居中 */
  align-items: center;
  margin-bottom: 15px; /* 缩小标题与搜索框的距离 */
  margin-top: 10px;
}

.comments-title { /* 统一标题类名 */
  font-size: 24px; /* 放大标题字体 */
  font-weight: 600;
  color: #333;
  margin-bottom: 20px; /* 增加标题与搜索框的距离 */
}

.search-filter-container {
  display: flex;
  gap: 2px;
  align-items: center;
  position: absolute; /* 相对于 .article-comment-users 定位 */
  top: 140px; /* 调整搜索框与白色卡片顶部的距离 (标题高度 + margin-bottom) */
  right: 24px; /* 靠近白色卡片的右侧 */
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
}

.filter-select {
  display: flex;
  align-items: center;
  margin-left: 10px;
}
.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
}

.comments-content { /* 统一内容区域类名 */
  padding-top: 20px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 30px; /* 缩小搜索框与列表的间距 */
}

.comments-table { /* 统一表格类名 */
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.comments-table thead { /* 统一表格头部类名 */
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.comments-table th { /* 统一表格 th 类名 */
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.comments-table td { /* 统一表格 td 类名 */
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.comments-table tbody tr:nth-child(even) { /* 统一表格偶数行类名 */
  background-color: #f9f9f9;
}

.comments-table tbody tr:hover { /* 统一表格 hover 类名 */
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.comments-table td a { /* 统一表格链接类名 */
  color: #5ea8da; /* 浅蓝色 */
  text-decoration: none;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 16px;
  color: #666;
}

button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  margin-top: 1px;
}

button:hover {
  background-color: #4a90c2;
}
</style>