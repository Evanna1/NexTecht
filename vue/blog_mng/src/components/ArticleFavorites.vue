<template>
  <div class="article-favorites">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h3 class="favorites-title">文章(ID:{{ this.articleId }})的收藏用户</h3>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterFavorites" placeholder="输入关键词搜索...">
      </div>
      <div class="filter-select">
        <select v-model="searchField" id="search-field">
          <option value="">不限</option>
          <option value="id">用户ID</option>
          <option value="username">用户名</option>
          <option value="create_at">收藏时间</option>
        </select>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else class="favorites-content">
      <div class="table-wrapper">
        <table class="favorites-table">
          <thead>
            <tr>
              <th>用户ID</th>
              <th>用户名</th>
              <th>昵称</th>
              <th>头像</th>
              <th>收藏时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="favorite in filteredFavorites" :key="favorite.id">
              <td>
                <a @click="showUserInfo(favorite.id)">{{ favorite.id }}</a>
              </td>
              <td>
                <a @click="showUserInfo(favorite.id)">{{ favorite.username }}</a>
              </td>
              <td>{{ favorite.nickname }}</td>
              <td>{{ favorite.avatar }}</td>
              <td>{{ formatDate(favorite.create_at) }}</td>
            </tr>
            <tr v-if="filteredFavorites.length === 0">
              <td colspan="5" class="no-data">没有符合条件的收藏记录</td>
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
    initialFavorites: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      favorites: this.initialFavorites,
      localIsLoading: false,
      searchKeyword: '',
      searchField: '',
      filteredFavorites: [...this.initialFavorites]
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
        if (newVal && !this.initialFavorites.length) {
          this.fetchArticleFavorites();
        }
      }
    },
    initialFavorites(newVal) {
      this.favorites = newVal;
      this.filteredFavorites = [...newVal];
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchArticleFavorites() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/favorites/${this.articleId}`, // 使用新的 API 接口
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.favorites = response.data.favorites; // 使用新的数据字段
          this.filteredFavorites = [...this.favorites];
        }
      } catch (error) {
        console.error('获取文章收藏者列表失败:', error);
        alert('获取文章收藏者列表失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
    },
    filterFavorites() {
      if (!this.searchKeyword) {
        this.filteredFavorites = [...this.favorites];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredFavorites = this.favorites.filter(favorite => {
        if (!this.searchField) {
          return (
            favorite.id.toString().toLowerCase().includes(keyword) ||
            favorite.username.toLowerCase().includes(keyword) ||
            this.formatDate(favorite.create_at).toLowerCase().includes(keyword)
          );
        } else {
          let value = favorite[this.searchField];
          if (this.searchField === 'create_at') {
            return this.formatDate(value).toLowerCase().includes(keyword);
          }
          return value && value.toString().toLowerCase().includes(keyword);
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
.article-favorites {
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
  margin-top: 10px;
}

.favorites-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.search-filter-container {
  display: flex;
  gap: 16px;
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

.favorites-content {
  padding-top: 20px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 30px;
}

.favorites-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.favorites-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.favorites-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.favorites-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.favorites-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.favorites-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.favorites-table td a {
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
