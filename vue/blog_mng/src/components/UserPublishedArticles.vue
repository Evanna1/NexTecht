<template>
  <div class="user-published-articles">
    <button @click="backToList" class="button">返回</button>
    <div class="header-container">
      <h3 class="page-title">用户 {{ userInfo }}(ID: {{ userId }}) 发布过的文章</h3>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterArticles" placeholder="输入关键词搜索文章...">
      </div>
      <div class="filter-select">
        <select v-model="searchField">
          <option value="">不限</option>
          <option value="id">ID</option>
          <option value="title">标题</option>
          <option value="status">状态</option>
          <option value="permission">权限</option>
          <option value="create_time">创建时间</option>
          <option value="update_time">更新时间</option>
        </select>
      </div>
    </div>
    <div v-if="mergedIsLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>
    <div v-else class="articles-content">
      <div class="table-wrapper">
        <table class="articles-table">
          <thead>
            <tr>
              <th>文章ID</th>
              <th>标题</th>
              <th>创建时间</th>
              <th>更新时间</th>
              <th>标签</th>
              <th>状态</th>
              <th>权限</th>
              <th>阅读量</th>
              <th>评论数</th>
              <th>点赞数</th>
              <th>收藏数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(article, index) in filteredArticles" :key="article.id" :class="{ 'even-row': index % 2 === 1 }">
              <td>
                <a @click="showArticleDetail(article.id)" class="clickable">{{ article.id }}</a>
              </td>
              <td>{{ article.title }}</td>
              <td>{{ formatDate(article.create_time) }}</td>
              <td>{{ formatDate(article.update_time) }}</td>
              <td>{{ article.tag }}</td>
              <td>
                <span :class="['status-badge', formatStatusClass(article.status)]">
                  {{ formatStatus(article.status) }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', article.permission === 0 ? 'normal' : 'blocked']">
                  {{ article.permission === 0 ? '公开' : '屏蔽' }}
                </span>
              </td>
              <td @click="showArticleBrowsers(article.id)" class="clickable">{{ article.read_count }}</td>
              <td @click="showArticleCommentUsers(article.id)" class="clickable">{{ article.comments_count }}</td>
              <td @click="showArticleLikeUsers(article.id)" class="clickable">{{ article.likes_count }}</td>
              <td @click="showArticleFavorites(article.id)" class="clickable">{{ article.favorites_count }}</td>
              <td>
                <button class="action-button" @click="showArticleDetail(article.id)">详情</button>
                <button class="action-button" @click="openPermissionModal(article)">修改权限</button>
              </td>
            </tr>
            <tr v-if="filteredArticles.length === 0">
              <td colspan="12" class="no-data">没有符合条件的文章</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="isPermissionModalOpen" class="modal">
        <div class="modal-content">
          <span class="close" @click="closePermissionModal">&times;</span>
          <h2>修改文章权限</h2>
          <form @submit.prevent="submitPermissionChange">
            <div class="form-group">
              <label for="article_id_perm">文章ID</label>
              <input type="text" id="article_id_perm" v-model="permissionForm.article_id" readonly>
            </div>
            <div class="form-group">
              <label for="new_permission">新权限</label>
              <select id="new_permission" v-model="permissionForm.new_permission">
                <option value="0">公开</option>
                <option value="1">屏蔽</option>
              </select>
            </div>
            <button type="submit" class="submit-button">提交</button>
            <button type="button" @click="closePermissionModal" class="cancel-button">取消</button>
          </form>
        </div>
      </div>
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
    initialArticles: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      publishedArticles: this.initialArticles,
      localIsLoading: false,
      userInfo: { nickname: '未知用户' },
      isPermissionModalOpen: false,
      permissionForm: {
        article_id: '',
        new_permission: '0'
      },
      currentArticle: null,
      searchKeyword: '',
      searchField: '',
      filteredArticles: [...this.initialArticles]
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
          this.fetchUserPublishedArticles();
          this.fetchUserInfo();
        }
      }
    },
    initialArticles(newVal) {
      this.publishedArticles = newVal;
      this.filteredArticles = [...newVal];
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
        0: '已发布',
        1: '已删除',
        2: '被举报'
      };
      return statusMap[status] || '未知状态';
    },
    formatStatusClass(status) {
      switch (status) {
        case 0: return 'normal'; // Assuming 'normal' for published
        case 1: return 'blocked'; // Assuming 'blocked' for deleted
        case 2: return 'reported'; // Custom class for reported
        default: return '';
      }
    },
    async fetchUserPublishedArticles() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}/published-articles`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.publishedArticles = response.data.articles;
          this.filteredArticles = [...this.publishedArticles];
        }
      } catch (error) {
        console.error('获取用户发布文章失败:', error);
        alert('获取用户发布文章失败，请稍后再试');
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
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.userInfo = { nickname: '未知用户' };
      }
    },
    backToList() {
      this.$emit('back-to-list');
    },
    openPermissionModal(article) {
      this.permissionForm.article_id = article.id;
      this.permissionForm.new_permission = article.permission;
      this.currentArticle = article;
      this.isPermissionModalOpen = true;
    },
    closePermissionModal() {
      this.isPermissionModalOpen = false;
    },
    async submitPermissionChange() {
      try {
        const token = localStorage.getItem('token');
        await axios.patch(
          `http://localhost:5000/article/manager/update/${this.permissionForm.article_id}/permission`,
          {
            permission: parseInt(this.permissionForm.new_permission)
          },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        this.currentArticle.permission = parseInt(this.permissionForm.new_permission);
        this.filterArticles(); // Re-filter to update the display if needed
        this.closePermissionModal();
        alert('文章权限更新成功');
      } catch (error) {
        console.error('更新文章权限失败:', error);
        alert('更新权限失败，请稍后再试');
      }
    },
    showArticleDetail(articleId) {
      this.$emit('show-article-detail', articleId);
    },
    showArticleFavorites(articleId) {
      this.$emit('show-article-favorites', articleId);
    },
    showArticleCommentUsers(articleId) {
      this.$emit('show-article-comment-users', articleId);
    },
    showArticleLikeUsers(articleId) {
      this.$emit('show-article-like-users', articleId);
    },
    showArticleBrowsers(articleId) {
      this.$emit('show-article-browsers', articleId);
    },
    filterArticles() {
      if (!this.searchKeyword) {
        this.filteredArticles = [...this.publishedArticles];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredArticles = this.publishedArticles.filter(article => {
        let value = '';
        switch (this.searchField) {
          case 'id':
            value = article.id.toString();
            break;
          case 'title':
            value = article.title;
            break;
          case 'status':
            value = this.formatStatus(article.status);
            break;
          case 'permission':
            value = article.permission === 0 ? '公开' : '屏蔽';
            break;
          case 'create_time':
            value = this.formatDate(article.create_time);
            break;
          case 'update_time':
            value = this.formatDate(article.update_time);
            break;
          case 'tag': // Added tag filtering
            value = article.tag;
            break;
          default:
            // Search all fields if no specific field is selected
            value = `${article.id} ${article.title} ${this.formatStatus(article.status)} ${article.permission === 0 ? '公开' : '屏蔽'} ${this.formatDate(article.create_time)} ${this.formatDate(article.update_time)} ${article.tag || ''}`;
        }
        return value.toLowerCase().includes(keyword);
      });
    }
  }
};
</script>

<style scoped>
.user-published-articles {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  text-align: left;
  position: relative;
}

.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  margin-top: 10px;
  margin-bottom: 20px; /* 增加标题与搜索框的距离 */
}

.page-title {
  font-size: 20px; /* Adjusted to match article list title */
  font-weight: 600;
  color: #333;
  margin: 0; /* Remove default margin */
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

.articles-content {
  padding-top: 20px; /* Space for search/filter and title */
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 50px; /* 缩小搜索框与列表的间距 */
}

.articles-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.articles-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.articles-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.articles-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.articles-table tbody tr.even-row {
  background-color: #f9f9f9; /* Matches article list even row background */
}

.articles-table tbody tr:hover {
  background-color: #f5f5f5; /* Matches article list hover background */
  transition: background-color 0.2s ease-in-out;
}

/* Status Badges - Directly copied from article list */
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

.reported {
  background-color: #fdf5e6;
  color: #b8860b;
}

/* Clickable links/cells */
.clickable {
  cursor: pointer;
  color: #5ea8da;
}

.clickable:hover {
  text-decoration: underline;
}

/* Action Buttons */
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

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

/* Loading Overlay - Directly copied from article list */
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

.loading-overlay p {
  color: #666;
  font-size: 16px;
}

/* Modal styles - updated to match article list modal */
.modal {
  position: fixed;
  z-index: 10; /* Higher z-index for modals */
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: #fff; /* White background */
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 400px;
  max-width: 90%;
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
  margin-bottom: 15px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}

.close:hover {
  color: black;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}

.submit-button,
.cancel-button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s ease-in-out;
}

.submit-button {
  background-color: #28a745; /* Green submit button */
  color: white;
  margin-right: 10px;
}

.submit-button:hover {
  opacity: 0.9;
}

.cancel-button {
  background-color: #dc3545; /* Red cancel button */
  color: white;
}

.cancel-button:hover {
  opacity: 0.9;
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