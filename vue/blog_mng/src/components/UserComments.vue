<template>
  <div class="comment-table-container">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h2 class="browsers-title">用户 {{ userInfo }} (ID: {{ userId }}) 的评论记录</h2>
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
            <option value="comment_id">评论ID</option>
            <option value="comment_create_time">创建时间</option>
            <option value="comment_status">状态</option>
            <option value="article_id">文章ID</option>
            <option value="parent_id">父评论ID</option>
            <option value="comment_content">评论内容</option>
            <option value="article_title">文章标题</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>

    <div v-else class="table-wrapper">
      <table class="comment-table">
        <thead>
          <tr>
            <th>评论ID</th>
            <th>创建时间</th>
            <th>状态</th>
            <th>文章ID</th>
            <th>文章标题</th>
            <th>父评论ID</th>
            <th>深度</th>
            <th>点赞数</th>
            <th>回复数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(comment, index) in filteredComments" :key="comment.comment_id" :class="{ 'even-row': index % 2 === 1 }">
            <td>
              <a @click="showCommentReview(comment.comment_id)" class="clickable">{{ comment.comment_id }}</a>
            </td>
            <td>{{ formatDate(comment.comment_create_time) }}</td>
            <td>
              <span :class="['status-badge', formatStatusClass(comment.comment_status)]">{{ formatStatus(comment.comment_status) }}</span>
            </td>
            <td>
              <a @click="showArticleDetail(comment.article_id)" class="clickable">{{ comment.article_id }}</a>
            </td>
            <td>
              <a @click="showArticleDetail(comment.article_id)" class="clickable">{{  comment.article_title }}</a>
            </td>
            <td>
              <a v-if="comment.parent_id" @click="showCommentParent(comment.parent_id)" class="clickable">
                {{ comment.parent_id }}
              </a>
              <span v-else>无</span>
            </td>
            <td>{{ comment.depth }}</td>
            <td>
              <a @click="showCommentLikeUsers(comment.comment_id)" class="clickable">{{ comment.comment_like_count }}</a>
            </td>
            <td>
              <a @click="showCommentReplies(comment.comment_id)" class="clickable">{{ comment.comment_reply_count }}</a>
            </td>
            <td>
              <button class="action-button" @click="showCommentReview(comment.comment_id)">详情</button>
              <button class="action-button delete-button" @click="deleteComment(comment.comment_id)">删除</button>
            </td>
          </tr>
          <tr v-if="filteredComments.length === 0">
            <td colspan="13" class="no-data">没有符合条件的评论</td>
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
      type: [String, Number],
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    initialComments: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      comments: [], // 存储从后端获取的所有评论
      filteredComments: [], // 存储过滤后的评论
      localIsLoading: false,
      userInfo: {},
      searchKeyword: '',
      searchField: '',
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  watch: {
    userId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchUserComments();
          this.fetchUserInfo();
        }
      }
    },
    // 当 comments 数据变化时，重新应用过滤，确保搜索/筛选功能即时生效
    comments: {
      handler(newVal) {
        this.filterComments();
      },
      deep: true, // 深度监听，以便内部属性变化也能触发
      immediate: true,
    },
    initialComments(newVal) {
      this.comments = newVal;
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
        case 1: return 'blocked';
        case 2: return 'blocked';
        case 3: return 'reported';
        default: return '';
      }
    },
    async fetchUserComments() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}/comments`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.comments = response.data.comments;
        } else {
          this.comments = [];
        }
      } catch (error) {
        console.error('获取用户评论记录失败:', error);
        alert('获取用户评论记录失败，请稍后再试');
        this.comments = [];
      } finally {
        this.localIsLoading = false;
      }
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
          this.userInfo = { nickname: '未知用户' };
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.userInfo = { nickname: '未知用户' };
      }
    },
    async deleteComment(commentId) {
      if (!confirm('确定要删除这条评论吗？')) {
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
        this.fetchUserComments(); // 删除后重新加载评论数据
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
    showCommentParent(parentId) {
      this.$emit('show-comment-parent', parentId);
    },
    showArticleDetail(articleId) {
      this.$emit('show-articleDetail', articleId);
    },
    backToList() {
      this.$emit('back-to-list');
    },
    filterComments() {
      if (!this.searchKeyword) {
        this.filteredComments = this.comments;
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredComments = this.comments.filter(comment => {
        if (!this.searchField) {
          // 如果没有选择特定字段，则搜索所有相关字段
          return (
            comment.comment_id.toString().includes(keyword) ||
            this.formatDate(comment.comment_create_time).includes(keyword) ||
            this.formatDate(comment.comment_update_time).includes(keyword) ||
            this.formatStatus(comment.comment_status).toLowerCase().includes(keyword) ||
            comment.article_id.toString().includes(keyword) ||
            (comment.article_title && comment.article_title.toLowerCase().includes(keyword)) ||
            (comment.parent_id && comment.parent_id.toString().includes(keyword))
          );
        } else {
          let value;
          switch (this.searchField) {
            case 'comment_id':
              value = comment.comment_id;
              break;
            case 'comment_create_time':
              value = this.formatDate(comment.comment_create_time);
              break;
            case 'comment_update_time':
              value = this.formatDate(comment.comment_update_time);
              break;
            case 'comment_status':
              value = this.formatStatus(comment.comment_status);
              break;
            case 'article_id':
              value = comment.article_id;
              break;
            case 'article_title':
              value = comment.article_title;
              break;
            case 'comment_content':
              value = comment.comment_content;
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
/* 样式完全复用自评论列表，确保一致性 */
.comment-table-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
}

.header-container {
  display: flex;
  justify-content: center; /* 标题居中 */
  align-items: center;
  margin-bottom: 15px; /* 缩小标题与搜索框的距离 */
  margin-top: 1px;
}

.browsers-title {
  font-size: 24px; /* 放大标题字体 */
  font-weight: 600;
  color: #333;
  margin-bottom: 20px; /* 增加标题与搜索框的距离 */
}

.search-filter-container {
  display: flex;
  gap: 2px;
  align-items: center;
  position: absolute; /* 相对于 .article-browsers 定位 */
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
}

.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 78px;
}

.comment-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.comment-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.comment-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.comment-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.comment-table tbody tr.even-row {
  background-color: #f9f9f9;
}

.comment-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
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
  background-color: #d9edf7;
  color: #31708f;
}

.action-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease-in-out;
  margin-right: 8px;
}

.action-button:hover {
  background-color: #4a90c2;
}

.action-button.delete-button {
  background-color: #dc3545;
}

.action-button.delete-button:hover {
  background-color: #c82333;
}

.clickable {
  cursor: pointer;
  color: #5ea8da;
  text-decoration: none;
}

.clickable:hover {
  text-decoration: underline;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

/* 加载层样式 */
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
</style>