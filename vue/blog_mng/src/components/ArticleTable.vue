<template>
  <div class="article-table-container">
    <div class="header-container">
      <h2 class="list-title">文章管理</h2>
      <div class="search-filter-container">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
          <input type="text" v-model="searchKeyword" @input="filterArticles" placeholder="输入关键词搜索文章...">
        </div>
        <div class="filter-select">
          <select v-model="searchField" id="search-field">
            <option value="">不限</option>
            <option value="id">ID</option>
            <option value="title">标题</option>
            <option value="author">作者</option>
            <option value="create_time">创建时间</option>
            <option value="update_time">更新时间</option>
            <option value="tag">标签</option>
            <option value="status">状态</option>
            <option value="permission">权限</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>

    <div class="table-wrapper">
      <table class="article-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>作者</th>
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
            <td>{{ article.id }}</td>
            <td>{{ article.title }}</td>
            <td>
              <a @click="showUserInfo(article.user_id)">{{ article.author }}</a>
            </td>
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
            <td colspan="13" class="no-data">没有符合条件的文章</td>
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
</template>

<script>
import axios from 'axios';

export default {
  props: {
    articles: {
      type: Array,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    loadArticles: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      isPermissionModalOpen: false,
      permissionForm: {
        article_id: '',
        new_permission: '0'
      },
      currentArticle: null,
      searchKeyword: '',
      searchField: '',
      filteredArticles: this.articles
    };
  },
  watch: {
    articles: {
      handler(newVal) {
        this.filteredArticles = newVal;
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
    formatPermission(permission) {
      return permission === 0 ? '公开' : '屏蔽';
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
        this.loadArticles();
        this.closePermissionModal();
        alert('文章权限更新成功');
      } catch (error) {
        console.error('更新文章权限失败:', error);
        alert('更新权限失败，请稍后再试');
      }
    },
    showArticleDetail(articleId) {
      this.$emit('show-articleDetail', articleId);
    },
    showArticleFavorites(articleId) {
      this.$emit('show-articleFavorites', articleId);
    },
    showArticleCommentUsers(articleId) {
      this.$emit('show-articleCommentUsers', articleId);
    },
    showArticleLikeUsers(articleId) {
      this.$emit('show-articleLikeUsers', articleId);
    },
    showArticleBrowsers(articleId) {
      this.$emit('show-articleBrowsers', articleId);
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    filterArticles() {
      if (!this.searchKeyword) {
        this.filteredArticles = this.articles;
        return;
      }

      this.filteredArticles = this.articles.filter(article => {
        const keyword = this.searchKeyword.toLowerCase();
        if (!this.searchField) {
          return (
            article.id.toString().includes(keyword) ||
            article.title.toLowerCase().includes(keyword) ||
            article.author.toLowerCase().includes(keyword) ||
            this.formatDate(article.create_time).includes(keyword) ||
            this.formatDate(article.update_time).includes(keyword) ||
            (article.tag && article.tag.toLowerCase().includes(keyword)) ||
            this.formatStatus(article.status).toLowerCase().includes(keyword) ||
            (article.permission === 0 ? '公开' : '屏蔽').toLowerCase().includes(keyword)
          );
        } else {
          let value;
          switch (this.searchField) {
            case 'id':
              value = article.id;
              break;
            case 'title':
              value = article.title;
              break;
            case 'author':
              value = article.author;
              break;
            case 'create_time':
              value = this.formatDate(article.create_time);
              break;
            case 'update_time':
              value = this.formatDate(article.update_time);
              break;
            case 'tag':
              value = article.tag;
              break;
            case 'status':
              value = this.formatStatus(article.status);
              break;
            case 'permission':
              value = article.permission === 0 ? '公开' : '屏蔽';
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
}
</script>

<style scoped>
.article-table-container {
  padding: 24px; /* Matches user list container padding */
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06); /* Matches user list box-shadow */
  position: relative; /* Keep for loading overlay */
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px; /* Matches user list header margin */
}

.list-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.search-filter-container {
  display: flex;
  gap: 16px; /* Matches user list search/filter gap */
  align-items: center;
  margin-left: auto;
}

.search-box {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 6px; /* Matches user list search box border-radius */
  padding: 6px 12px; /* Matches user list search box padding */
  background-color: #fff;
}

.search-icon {
  width: 18px; /* Matches user list search icon size */
  height: 18px;
  margin-right: 8px; /* Matches user list search icon margin */
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
.filter-select label {
  font-size: 14px;
  color: #555;
  margin-right: 8px;
  margin-left: 10px;
}
.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px; /* Matches user list filter select border-radius */
  padding: 5px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); /* Matches user list table-wrapper shadow */
  margin-top: 20px;
}

.article-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.article-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02); /* Matches user list table header shadow */
}

.article-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px; /* Matches user list table header padding */
  text-align: left;
}

.article-table td {
  padding: 10px 16px; /* Matches user list table cell padding */
  border-bottom: 1px solid #eee;
}

.article-table tbody tr.even-row {
  background-color: #f9f9f9; /* Matches user list even row background */
}

.article-table tbody tr:hover {
  background-color: #f5f5f5; /* Matches user list hover background */
  transition: background-color 0.2s ease-in-out; /* Matches user list transition */
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* Specific status styles for articles, mimicking user status badges */
.normal { /* For '已发布' and '公开' */
  background-color: #dff0d8;
  color: #3c763d;
}

.blocked { /* For '已删除' and '屏蔽' */
  background-color: #fdecea;
  color: #d9534f;
}

.reported { /* New style for '被举报' */
  background-color: #fdf5e6; /* Light orange/yellow */
  color: #b8860b; /* Darker orange/yellow */
}

.action-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px; /* Matches user list button padding */
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s ease-in-out;
  margin-right: 8px; /* Matches user list button margin */
}

.action-button:hover {
  background-color: #4a90c2; /* Darker blue on hover */
}

.clickable {
  cursor: pointer;
  color: #5ea8da;
}

.clickable:hover {
  text-decoration: underline;
}

/* Modal styles - largely consistent with user list modal */
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
  background-color: #5ea8da; /* Green submit button */
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

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

/* Loading Overlay (taken directly from your original article list) */
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
  border-radius: 12px; /* Ensure it respects container border-radius */
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

.article-table td a {
  color: #5ea8da; /* 浅蓝色 */
  text-decoration: none;
}

</style>