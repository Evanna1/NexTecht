<template>
  <div class="user-liked-articles">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h3 class="liked-title">用户 {{ userInfo }} (ID: {{ userId }}) 点赞的文章</h3>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterLikedArticles" placeholder="输入关键词搜索文章...">
      </div>
      <div class="filter-select">
        <select v-model="searchField" id="search-field" @change="filterLikedArticles">
          <option value="">不限</option>
          <option value="article_info.id">文章ID</option>
          <option value="article_info.title">文章标题</option>
          <option value="article_info.author">文章作者</option>
          <option value="like_create_time">点赞时间</option>
        </select>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else class="liked-articles-content">
      <div class="table-wrapper">
        <table class="liked-articles-table">
          <thead>
            <tr>
              <th>文章ID</th>
              <th>文章标题</th>
              <th>文章作者</th>
              <th>点赞时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="article in filteredLikedArticles" :key="article.article_info.id">
              <td>
                <a @click="showArticleDetail(article.article_info.id)">{{ article.article_info.id }}</a>
              </td>
              <td>
                <a @click="showArticleDetail(article.article_info.id)">{{ article.article_info.title }}</a>
              </td>
              <td>{{ article.article_info.author }}</td>
              <td>{{ formatDate(article.like_create_time) }}</td>
            </tr>
            <tr v-if="filteredLikedArticles.length === 0">
              <td colspan="4" class="no-data">没有符合条件的点赞记录</td>
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
    userId: {
      type: [String, Number],
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      likedArticles: [],
      localIsLoading: false,
      userInfo: {},
      searchKeyword: '',
      searchField: '',
      filteredLikedArticles: []
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
          this.fetchUserLikedArticles();
          this.fetchUserInfo();
        }
      }
    },
    likedArticles: {
      handler(newVal) {
        this.filterLikedArticles();
      },
      deep: true
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchUserLikedArticles() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/${this.userId}/liked-articles`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.likedArticles = response.data.liked_articles;
          this.filterLikedArticles();
        }
      } catch (error) {
        console.error('获取用户点赞文章失败:', error);
        alert('获取用户点赞文章失败，请稍后再试');
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
    filterLikedArticles() {
      if (!this.searchKeyword && !this.searchField) {
        this.filteredLikedArticles = [...this.likedArticles];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredLikedArticles = this.likedArticles.filter(article => {
        if (!this.searchField) {
          return (
            article.article_info.id.toString().toLowerCase().includes(keyword) ||
            article.article_info.title.toLowerCase().includes(keyword) ||
            article.article_info.author.toLowerCase().includes(keyword) ||
            this.formatDate(article.like_create_time).toLowerCase().includes(keyword)
          );
        } else {
          let value = '';
          if (this.searchField.startsWith('article_info.')) {
            const nestedField = this.searchField.split('.')[1];
            value = article.article_info[nestedField];
          } else {
            value = article[this.searchField];
          }

          if (this.searchField === 'like_create_time') {
            return this.formatDate(value).toLowerCase().includes(keyword);
          }

          return value && value.toString().toLowerCase().includes(keyword);
        }
      });
    },
    showArticleDetail(articleId) {
      this.$emit('show-articleDetail', articleId);
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
.user-liked-articles {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
  text-align: left;
}

.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  margin-top: 50px;
}

.liked-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.search-filter-container {
  display: flex;
  gap: 2px;
  align-items: center;
  position: absolute;
  top: 140px;
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

.liked-articles-content {
  padding-top: 20px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 30px;
}

.liked-articles-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.liked-articles-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.liked-articles-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.liked-articles-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.liked-articles-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.liked-articles-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.liked-articles-table td a {
  color: #5ea8da;
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

.back-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  margin-top: 1px;
  position: absolute;
  top: 24px;
  left: 24px;
}

.back-button:hover {
  background-color: #4a90c2;
}
</style>