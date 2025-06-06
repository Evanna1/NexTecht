<template>
  <div class="comment-table-container">
    <div class="header-container">
      <h2 class="list-title">评论管理</h2>
      <div class="search-filter-container">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
          <input type="text" v-model="searchKeyword" @input="filterComments" placeholder="输入关键词搜索评论...">
        </div>
        <div class="filter-select">
          <select v-model="searchField" id="search-field">
            <option value="">不限</option>
            <option value="id">评论ID</option>
            <option value="author">作者</option>
            <option value="create_time">创建时间</option>
            <option value="status">状态</option>
            <option value="article_id">文章ID</option>
            <option value="parent_id">父评论ID</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>

    <div class="table-wrapper">
      <table class="comment-table">
        <thead>
          <tr>
            <th>评论ID</th>
            <th>作者</th>
            <th>创建时间</th>
            <th>状态</th>
            <th>文章ID</th>
            <th>父评论ID</th>
            <th>深度</th>
            <th>点赞数</th>
            <th>回复数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(comment, index) in filteredComments" :key="comment.id" :class="{ 'even-row': index % 2 === 1 }">
            <td>{{ comment.id }}</td>
            <td>
              <a @click="showUserInfo(comment.user.id)" class="clickable">{{ comment.user.username }}</a>
            </td>
            <td>{{ formatDate(comment.create_time) }}</td>
            <td>
              <span :class="['status-badge', formatStatusClass(comment.status)]">{{ formatStatus(comment.status) }}</span>
            </td>
            <td>
              <a @click="showArticleDetail(comment.article_id)" class="clickable">{{ comment.article_id }}</a>
            </td>
            <td>
              <a v-if="comment.parent_id" @click="showCommentDeatail(comment.parent_id)">
                {{ comment.parent_id }}
              </a>
              <span v-else>无</span>
            </td>
            <td>{{ comment.depth }}</td>
            <td>
              <a @click="showCommentLikeUsers(comment.id)" class="clickable">{{ comment.like_count }}</a>
            </td>
            <td>
              <a @click="showCommentReplies(comment.id)" class="clickable">{{ comment.reply_count }}</a>
            </td>
            <td>
              <button class="action-button" @click="showCommentReview(comment.id)">详情</button>
              <button class="action-button delete-button" @click="deleteComment(comment.id)">删除</button>
            </td>
          </tr>
          <tr v-if="filteredComments.length === 0">
            <td colspan="12" class="no-data">没有符合条件的评论</td>
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
    comments: {
      type: Array,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      searchKeyword: '',
      searchField: '',
      filteredComments: this.comments, // 初始化过滤后的评论列表
    };
  },
  watch: {
    comments: {
      handler(newVal) {
        this.filteredComments = newVal;
      },
      immediate: true
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    formatStatus(status) {
      const statusMap = {
        0: '正常',
        1: '已删除',
        2: '屏蔽',
        3: '举报'
      };
      return statusMap[status] || '未知状态';
    },
    formatStatusClass(status) {
      switch (status) {
        case 0: return 'normal';
        case 1: return 'blocked'; // 已删除使用 'blocked'
        case 2: return 'blocked'; // 屏蔽使用 'blocked'
        case 3: return 'reported'; // 举报使用 'reported'
        default: return '';
      }
    },
    async approveComment(commentId) {
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `http://localhost:5000/manager/comment/${commentId}/review`,
          { approved: true },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        alert('审核成功');
        this.$emit('load-comments'); // 重新加载评论数据
      } catch (error) {
        console.error('审核评论失败:', error);
        alert('审核失败，请稍后再试');
      }
    },
    async deleteComment(commentId) {
      if (!confirm('确定要删除这条回复吗？此操作不可逆。')) {
        return;
      }
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `http://localhost:5000/manager/comment/${commentId}/delete`,
          {},
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        alert('删除成功');
        this.$emit('load-comments'); // 重新加载评论数据
      } catch (error) {
        console.error('删除评论失败:', error);
        alert('删除失败，请稍后再试');
      }
    },
    showCommentReview(commentId) {
      this.$emit('show-comment-review', commentId);
    },
    showCommentLikeUsers(commentId) {
      this.$emit('show-comment-like-users', commentId);
    },
    showCommentReplies(commentId) {
      this.$emit('show-comment-replies', commentId);
    },
    showCommentDeatail(commentId) {
      this.$emit('show-comment-detail', commentId);
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    showArticleDetail(articleId) {
      this.$emit('show-articleDetail', articleId);
    },
    filterComments() {
      if (!this.searchKeyword) {
        this.filteredComments = this.comments;
        return;
      }
      this.filteredComments = this.comments.filter(comment => {
        const keyword = this.searchKeyword.toLowerCase();
        if (!this.searchField) {
          // 如果没有选择特定字段，则搜索所有相关字段
          return (
            comment.id.toString().includes(keyword) ||
            (comment.user.username && comment.user.username.toLowerCase().includes(keyword)) ||
            this.formatDate(comment.create_time).includes(keyword) ||
            this.formatStatus(comment.status).toLowerCase().includes(keyword) ||
            comment.article_id.toString().includes(keyword) ||
            (comment.parent_id && comment.parent_id.toString().includes(keyword))
          );
        } else {
          let value;
          switch (this.searchField) {
            case 'id':
              value = comment.id;
              break;
            case 'author':
              value = comment.user.username;
              break;
            case 'create_time':
              value = this.formatDate(comment.create_time);
              break;
            case 'update_time':
              value = this.formatDate(comment.update_time);
              break;
            case 'status':
              value = this.formatStatus(comment.status);
              break;
            case 'article_id':
              value = comment.article_id;
              break;
            case 'parent_id':
              value = comment.parent_id;
              break;
            default:
              value = '';
              break;
          }
          return value && value.toString().toLowerCase().includes(keyword);
        }
      });
    }
  }
};
</script>

<style scoped>
.comment-table-container {
  padding: 24px; /* 与用户/文章列表容器一致 */
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06); /* 与用户/文章列表阴影一致 */
  position: relative; /* 保持加载层定位 */
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px; /* 与用户/文章列表头部间隔一致 */
}

.list-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.search-filter-container {
  display: flex;
  gap: 16px; /* 与用户/文章列表搜索/筛选间距一致 */
  align-items: center;
  margin-left: auto; /* 搜索和筛选靠右对齐 */
}

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 6px; /* 与用户/文章列表搜索框圆角一致 */
  padding: 6px 12px; /* 与用户/文章列表搜索框内边距一致 */
  background-color: #fff;
}

.search-icon {
  width: 18px; /* 与用户/文章列表搜索图标大小一致 */
  height: 18px;
  margin-right: 8px; /* 与用户/文章列表搜索图标右边距一致 */
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
}

.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px; /* 与用户/文章列表筛选下拉框圆角一致 */
  padding: 5px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); /* 与用户/文章列表表格容器阴影一致 */
  margin-top: 20px;
}

.comment-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap; /* 防止内容换行，保持表格紧凑 */
}

.comment-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02); /* 与用户/文章列表表头阴影一致 */
}

.comment-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px; /* 与用户/文章列表表头内边距一致 */
  text-align: left;
}

.comment-table td {
  padding: 10px 16px; /* 与用户/文章列表表格单元格内边距一致 */
  border-bottom: 1px solid #eee;
}

.comment-table tbody tr.even-row {
  background-color: #f9f9f9; /* 与用户/文章列表偶数行背景一致 */
}

.comment-table tbody tr:hover {
  background-color: #f5f5f5; /* 与用户/文章列表鼠标悬停背景一致 */
  transition: background-color 0.2s ease-in-out; /* 与用户/文章列表过渡效果一致 */
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* 评论状态徽章颜色 */
.normal { /* 正常 / 已通过 */
  background-color: #dff0d8;
  color: #3c763d;
}

.blocked { /* 已删除 / 屏蔽 / 未通过 */
  background-color: #fdecea;
  color: #d9534f;
}

.reported { /* 举报 */
  background-color: #fdf5e6;
  color: #b8860b;
}

.pending { /* 待审核 */
  background-color: #d9edf7; /* 浅蓝色 */
  color: #31708f; /* 深蓝色 */
}

.action-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px; /* 与用户/文章列表按钮内边距一致 */
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease-in-out;
  margin-right: 8px; /* 与用户/文章列表按钮右边距一致 */
}

.action-button:hover {
  background-color: #4a90c2; /* 悬停颜色 */
}

.action-button.delete-button { /* 删除按钮的特定样式 */
    background-color: #dc3545; /* 红色 */
}

.action-button.delete-button:hover {
    background-color: #c82333; /* 红色悬停 */
}

.clickable {
  cursor: pointer;
  color: #5ea8da; /* 与用户/文章列表可点击链接颜色一致 */
  text-decoration: none; /* 默认无下划线 */
}

.clickable:hover {
  text-decoration: underline; /* 鼠标悬停显示下划线 */
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

/* 加载层样式 - 与用户/文章列表一致 */
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
  z-index: 10;
  border-radius: 12px; /* 确保与容器圆角一致 */
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

.comment-table td a {
  color: #5ea8da; /* 浅蓝色 */
  text-decoration: none;
}

</style>