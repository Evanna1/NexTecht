<template>
  <div class="article-likers">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h3 class="likers-title">文章(ID:{{ this.articleId }})的点赞用户</h3>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
           <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterLikers" placeholder="输入关键词搜索...">
      </div>
      <div class="filter-select">
        <select v-model="searchField" id="search-field">
          <option value="">不限</option>
          <option value="user_info.id">用户ID</option>
          <option value="user_info.username">用户名</option>
          <option value="like_create_time">点赞时间</option>
        </select>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else class="likers-content">
      <div class="table-wrapper">
        <table class="likers-table">
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
            <tr v-for="liker in filteredLikers" :key="liker.user_info.id">
              <td>
                <a @click="showUserInfo(liker.user_info.id)">{{ liker.user_info.id }}</a>
              </td>
              <td>
                <a @click="showUserInfo(liker.user_info.id)">{{ liker.user_info.username }}</a>
              </td>
              <td>{{ liker.user_info.nickname }}</td>
              <td>{{ liker.user_info.avatar }}</td>
              <td>{{ formatDate(liker.like_create_time) }}</td>
            </tr>
            <tr v-if="filteredLikers.length === 0">
              <td colspan="5" class="no-data">没有符合条件的点赞记录</td>
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
    initialLikers: { // 将 initialBrowsers 改为 initialLikers
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      likers: this.initialLikers, // 将 browsers 改为 likers
      localIsLoading: false,
      searchKeyword: '',
      searchField: '',
      filteredLikers: [...this.initialLikers] // 将 filteredBrowsers 改为 filteredLikers
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
        if (newVal && !this.initialLikers.length) { // 检查 initialLikers
          this.fetchArticleLikers(); // 调用新的获取点赞列表方法
        }
      }
    },
    initialLikers(newVal) { // 监听 initialLikers
      this.likers = newVal;
      this.filteredLikers = [...newVal]; // 当 initialLikers 更新时，重置 filteredLikers
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchArticleLikers() { // 修改方法名以反映其功能
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/article/${this.articleId}/like-users`, // 更新 API 接口
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.likers = response.data.like_users; // 更新数据字段
          this.filteredLikers = [...this.likers]; // 获取数据后初始化 filteredLikers
        }
      } catch (error) {
        console.error('获取文章点赞用户列表失败:', error);
        alert('获取文章点赞用户列表失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
    },
    filterLikers() { // 修改方法名
      if (!this.searchKeyword) {
        this.filteredLikers = [...this.likers]; // 修改过滤数组
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredLikers = this.likers.filter(liker => { // 修改过滤对象
        if (!this.searchField) {
          return (
            liker.user_info.id.toString().toLowerCase().includes(keyword) ||
            liker.user_info.username.toLowerCase().includes(keyword) ||
            this.formatDate(liker.like_create_time).toLowerCase().includes(keyword) // 修改搜索字段
          );
        } else {
          let value = '';
          if (this.searchField.startsWith('user_info.')) {
            const nestedField = this.searchField.split('.')[1];
            value = liker.user_info[nestedField];
          } else {
            value = liker[this.searchField];
          }

          if (this.searchField === 'like_create_time') { // 修改搜索字段
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
/* 样式与文章浏览列表基本相同，只修改了少量类名以反映“点赞” */
.article-likers {
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

.likers-title { /* 修改类名 */
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

.likers-content { /* 修改类名 */
  padding-top: 20px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 30px;
}

.likers-table { /* 修改类名 */
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.likers-table thead { /* 修改类名 */
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.likers-table th { /* 修改类名 */
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.likers-table td { /* 修改类名 */
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.likers-table tbody tr:nth-child(even) { /* 修改类名 */
  background-color: #f9f9f9;
}

.likers-table tbody tr:hover { /* 修改类名 */
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.likers-table td a { /* 修改类名 */
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