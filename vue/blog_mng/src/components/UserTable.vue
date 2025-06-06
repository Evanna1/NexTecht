<template>
  <div class="user-list-container">
    <div class="header-container">
      <h2 class="list-title">用户管理</h2>
      <div class="search-filter-container">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
          <input type="text" v-model="searchKeyword" @input="filterUsers" placeholder="输入关键词搜索用户...">
        </div>
        <div class="filter-select">
          <select v-model="searchField" id="search-field">
            <option value="">不限</option>
            <option value="id">ID</option>
            <option value="username">用户名</option>
            <option value="nickname">昵称</option>
            <option value="gender">性别</option>
            <option value="email">邮箱</option>
            <option value="phone">手机号</option>
            <option value="create_at">注册时间</option>
            <option value="is_online">登录状态</option>
            <option value="last_login_at">最后登录时间</option>
            <option value="u_status">状态</option>
          </select>
        </div>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="user-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>头像</th>
            <th>性别</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>注册时间</th>
            <th>最后登录</th>
            <th>登录状态</th>
            <th>状态</th>
            <th>发布权限</th>
            <th>评论权限</th>
            <th>文章数</th>
            <th>评论数</th>
            <th>点赞数</th>
            <th>粉丝数</th>
            <th>关注数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(user, index) in filteredUsers" :key="user.id" :class="{ 'even-row': index % 2 === 1 }">
            <td>
              <a @click="showUserInfo(user.id)" class="clickable">{{ user.id }}</a>
            </td>
            <td>
              <a @click="showUserInfo(user.id)" class="clickable">{{ user.username }}</a>
            </td>
            <td>{{ user.nickname }}</td>
            <td>
              <div class="avatar-container">
                <img :src="user.avatar || defaultAvatar" alt="头像" class="avatar" />
              </div>
            </td>
            <td>{{ user.gender }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.phone }}</td>
            <td>{{ formatDate(user.create_at) }}</td>
            <td>{{ formatDate(user.last_login_at) }}</td>
            <td>
              <span :class="['status-dot', user.is_online ? 'online' : 'offline']"></span>
              {{ user.is_online ? '在线' : '离线' }}
            </td>
            <td>
              <span :class="['status-badge', user.u_status === 0 ? 'normal' : 'blocked']">
                {{ user.u_status === 0 ? '正常' : '封禁' }}
              </span>
            </td>
            <td>{{ user.is_publish === 1 ? '有' : '无' }}</td>
            <td>{{ user.is_comment === 1 ? '有' : '无' }}</td>
            <td @click="showUserPublishedArticles(user.id)" class="clickable">{{ user.article_count }}</td>
            <td @click="showUserComments(user.id)" class="clickable">{{ user.comment_count }}</td>
            <td @click="showUserLikedArticles(user.id)" class="clickable">{{ user.like_count }}</td>
            <td @click="showFollowers(user.id)" class="clickable">{{ user.followers_count }}</td>
            <td @click="showFollowing(user.id)" class="clickable">{{ user.followings_count }}</td>
            <td>
              <button class="action-button" @click="openStatusModal(user)">修改状态</button>
              <button class="action-button" @click="openPermissionModal(user)">修改权限</button>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="19" class="no-data">没有符合条件的用户</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isStatusModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeStatusModal">&times;</span>
        <h2>修改用户状态</h2>
        <form @submit.prevent="submitStatusChange">
          <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" v-model="statusForm.username" readonly>
          </div>
          <div class="form-group">
            <label for="new_status">新状态</label>
            <select id="new_status" v-model="statusForm.new_status">
              <option value="0">正常</option>
              <option value="1">封禁</option>
            </select>
          </div>
          <button type="submit" class="submit-button">提交</button>
          <button type="button" @click="closeStatusModal" class="cancel-button">取消</button>
        </form>
      </div>
    </div>

    <div v-if="isPermissionModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closePermissionModal">&times;</span>
        <h2>修改用户权限</h2>
        <form @submit.prevent="submitPermissionChange">
          <div class="form-group">
            <label for="username_perm">用户名</label>
            <input type="text" id="username_perm" v-model="permissionForm.username" readonly>
          </div>
          <div class="form-group">
            <label for="is_publish">发布权限</label>
            <select id="is_publish" v-model="permissionForm.is_publish">
              <option value="1">有</option>
              <option value="0">无</option>
            </select>
          </div>
          <div class="form-group">
            <label for="is_comment">评论权限</label>
            <select id="is_comment" v-model="permissionForm.is_comment">
              <option value="1">有</option>
              <option value="0">无</option>
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
    users: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      searchKeyword: '',
      searchField: '',
      filteredUsers: this.users,
      isStatusModalOpen: false,
      isPermissionModalOpen: false,
      statusForm: {
        username: '',
        new_status: '0'
      },
      permissionForm: {
        username: '',
        is_publish: '1',
        is_comment: '1'
      },
      currentStatusUser: null,
      currentPermissionUser: null
    };
  },
  watch: {
    users: {
      handler(newVal) {
        this.filteredUsers = newVal;
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
    filterUsers() {
      if (!this.searchKeyword) {
        this.filteredUsers = this.users;
        return;
      }

      this.filteredUsers = this.users.filter(user => {
        const keyword = this.searchKeyword.toLowerCase();
        if (!this.searchField) {
          return (
            user.id.toString().toLowerCase().includes(keyword) ||
            user.username.toLowerCase().includes(keyword) ||
            user.nickname.toLowerCase().includes(keyword) ||
            (user.gender && user.gender.toLowerCase().includes(keyword)) ||
            user.email.toLowerCase().includes(keyword) ||
            (user.phone && user.phone.toLowerCase().includes(keyword)) ||
            (user.create_at && this.formatDate(user.create_at).includes(keyword)) ||
            (user.last_login_at && this.formatDate(user.last_login_at).includes(keyword)) ||
            (user.is_online ? '在线' : '离线').toLowerCase().includes(keyword) ||
            (user.u_status === 0 ? '正常' : '封禁').toLowerCase().includes(keyword)
          );
        } else {
          let value = user[this.searchField];
          if (this.searchField === 'create_at' || this.searchField === 'last_login_at') {
            value = this.formatDate(value);
          } else if (this.searchField === 'is_online') {
            value = user.is_online ? '在线' : '离线';
          } else if (this.searchField === 'u_status') {
            value = user.u_status === 0 ? '正常' : '封禁';
          }
          return value && value.toString().toLowerCase().includes(keyword);
        }
      });
    },
    openStatusModal(user) {
      this.statusForm.username = user.username;
      this.statusForm.new_status = user.u_status;
      this.currentStatusUser = user;
      this.isStatusModalOpen = true;
    },
    closeStatusModal() {
      this.isStatusModalOpen = false;
    },
    openPermissionModal(user) {
      this.permissionForm.username = user.username;
      this.permissionForm.is_publish = user.is_publish;
      this.permissionForm.is_comment = user.is_comment;
      this.currentPermissionUser = user;
      this.isPermissionModalOpen = true;
    },
    closePermissionModal() {
      this.isPermissionModalOpen = false;
    },
    async submitStatusChange() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://localhost:5000/manager/update_user_status',
          {
            u_account: this.statusForm.username,
            new_status: parseInt(this.statusForm.new_status)
          },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );

        if (response.data.state === 1) {
          this.$emit('refresh-users');
          this.closeStatusModal();
          alert('状态更新成功');
        } else {
          alert(`状态更新失败: ${response.data.message}`);
        }
      } catch (error) {
        if (error.response && error.response.status === 400) {
          alert(`状态更新失败: ${error.response.data.message}`);
        } else {
          console.error('更新用户状态失败:', error);
          alert('更新状态失败，请稍后再试');
        }
      }
    },
    async submitPermissionChange() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://localhost:5000/manager/update_user_permission',
          {
            u_account: this.permissionForm.username,
            is_publish: parseInt(this.permissionForm.is_publish),
            is_comment: parseInt(this.permissionForm.is_comment)
          },
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );

        if (response.data.state === 1) {
          this.$emit('refresh-users');
          this.closePermissionModal();
          alert('权限更新成功');
        } else {
          alert(`权限更新失败: ${response.data.message}`);
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400 || error.response.status === 403) {
            alert(`权限更新失败: ${error.response.data.message}`);
          } else {
            alert(`服务器返回错误: ${error.response.status}`);
          }
        } else {
          console.error('更新用户权限失败:', error);
          alert('更新权限失败，请稍后再试');
        }
      }
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    showFollowers(userId) {
      this.$emit('show-followers', userId);
    },
    showFollowing(userId) {
      this.$emit('show-following', userId);
    },
    showUserComments(userId) {
      this.$emit('show-userComments', userId);
    },
    showUserLikedArticles(userId) {
      this.$emit('show-userLikedArticles', userId);
    },
    showUserPublishedArticles(userId) {
      this.$emit('show-userPublishedArticles', userId);
    }
  }
}
</script>

<style scoped>
.user-list-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.list-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.search-filter-container {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-left: auto; /* 将搜索和筛选移到右侧 */
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
.filter-select label {
  font-size: 14px;
  color: #555;
  margin-right: 8px;
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

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 20px;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.user-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.user-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.user-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.user-table tbody tr.even-row {
  background-color: #f9f9f9;
}

.user-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
}

.avatar-container {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
   border: 1px solid #c9c7c7;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.online {
  background-color: #5cb85c;
}

.offline {
  background-color: #d9534f;
}

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
  background-color: #5ea8da;
}

.clickable {
  cursor: pointer;
  color: #5ea8da;
}

.clickable:hover {
  text-decoration: underline;
}

.modal {
  position: fixed;
  z-index: 10;
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
  background-color: #fff;
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
  background-color: #28a745;
  color: white;
  margin-right: 10px;
}

.submit-button:hover {
  opacity: 0.9;
}

.cancel-button {
  background-color: #dc3545;
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
</style>