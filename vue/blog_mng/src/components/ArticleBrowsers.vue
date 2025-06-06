<template>
  <div class="article-browsers">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h2 class="browsers-title">文章(ID:{{ this.articleId }})的浏览用户</h2>
    </div>
    <div class="search-filter-container">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
          <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
        </svg>
        <input type="text" v-model="searchKeyword" @input="filterBrowsers" placeholder="输入关键词搜索用户...">
      </div>
      <div class="filter-select">
        <select v-model="searchField" id="search-field">
          <option value="">不限</option>
          <option value="user_info.id">用户ID</option>
          <option value="user_info.username">用户名</option>
          <option value="browse_time">浏览时间</option>
        </select>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading">
      加载中...
    </div>
    <div v-else class="browsers-content">
      <div class="table-wrapper">
        <table class="browsers-table">
          <thead>
            <tr>
              <th>用户ID</th>
              <th>用户名</th>
              <th>昵称</th>
              <th>头像</th>
              <th>浏览时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="browser in filteredBrowsers" :key="browser.user_info.id">
              <td>
                <a @click="showUserInfo(browser.user_info.id)">{{ browser.user_info.id }}</a>
              </td>
              <td>
                <a @click="showUserInfo(browser.user_info.id)">{{ browser.user_info.username }}</a>
              </td>
              <td>{{ browser.user_info.nickname }}</td>
              <td>{{ browser.user_info.avatar }}</td>
              <td>{{ formatDate(browser.browse_time) }}</td>
            </tr>
            <tr v-if="filteredBrowsers.length === 0">
              <td colspan="5" class="no-data">没有符合条件的浏览记录</td>
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
    initialBrowsers: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      browsers: this.initialBrowsers,
      localIsLoading: false,
      searchKeyword: '',
      searchField: '',
      filteredBrowsers: [...this.initialBrowsers] // 初始化为所有浏览记录
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
        if (newVal && !this.initialBrowsers.length) {
          this.fetchArticleBrowsers();
        }
      }
    },
    initialBrowsers(newVal) {
      this.browsers = newVal;
      this.filteredBrowsers = [...newVal]; // 当 initialBrowsers 更新时，重置 filteredBrowsers
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async fetchArticleBrowsers() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/article/${this.articleId}/browsers`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          this.browsers = response.data.browser_users;
          this.filteredBrowsers = [...this.browsers]; // 获取数据后初始化 filteredBrowsers
        }
      } catch (error) {
        console.error('获取文章浏览者列表失败:', error);
        alert('获取文章浏览者列表失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
    },
    filterBrowsers() {
      if (!this.searchKeyword) {
        this.filteredBrowsers = [...this.browsers];
        return;
      }

      const keyword = this.searchKeyword.toLowerCase();
      this.filteredBrowsers = this.browsers.filter(browser => {
        if (!this.searchField) {
          return (
            browser.user_info.id.toString().toLowerCase().includes(keyword) ||
            browser.user_info.username.toLowerCase().includes(keyword) ||
            this.formatDate(browser.browse_time).toLowerCase().includes(keyword)
          );
        } else {
          let value = '';
          if (this.searchField.startsWith('user_info.')) {
            const nestedField = this.searchField.split('.')[1];
            value = browser.user_info[nestedField];
          } else {
            value = browser[this.searchField];
          }

          if (this.searchField === 'browse_time') {
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
.article-browsers {
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

.browsers-content {
  padding-top: 20px;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 30px; /* 缩小搜索框与列表的间距 */
}

.browsers-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.browsers-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.browsers-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.browsers-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.browsers-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.browsers-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.browsers-table td a {
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