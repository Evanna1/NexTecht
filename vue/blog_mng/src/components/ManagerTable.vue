<template>
  <div class="manager-section-container">
    <div class="header-container">
      <h2 class="list-title">管理员管理</h2>
      <div class="actions-and-search-row"> <div class="add-button-container">
          <button class="action-button add-button" @click="openAddModal">添加管理员</button>
        </div>
        <div class="search-filter-container">
          <div class="search-box">
            <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
              <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
            </svg>
            <input type="text" v-model="searchKeyword" @input="filterManagers" placeholder="输入关键词搜索管理员...">
          </div>
          <div class="filter-select">
            <select v-model="searchField" id="search-field">
              <option value="">不限</option>
              <option value="mng_id">ID</option>
              <option value="mng_name">用户名</option>
              <option value="mng_nickname">昵称</option>
              <option value="mng_gender">性别</option>
              <option value="mng_email">邮箱</option>
              <option value="mng_phone">手机号</option>
              <option value="mng_create_at">注册时间</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="table-wrapper">
      <table class="manager-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>性别</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(manager, index) in filteredManagers" :key="manager.mng_id" :class="{ 'even-row': index % 2 === 1 }">
            <td>{{ manager.mng_id }}</td>
            <td>{{ manager.mng_name }}</td>
            <td>{{ manager.mng_nickname }}</td>
            <td>{{ manager.mng_gender }}</td>
            <td>{{ manager.mng_email }}</td>
            <td>{{ manager.mng_phone }}</td>
            <td>{{ formatDate(manager.mng_create_at) }}</td>
            <td>
              <button class="action-button delete-button" @click="confirmDelete(manager.mng_id)">删除</button>
            </td>
          </tr>
          <tr v-if="filteredManagers.length === 0">
            <td colspan="8" class="no-data">没有符合条件的管理员</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isAddModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeAddModal">&times;</span>
        <h2>添加新管理员</h2>
        <form @submit.prevent="submitAddManager">
          <div class="form-group">
            <label for="m_name">用户名</label>
            <input type="text" id="m_name" v-model="addForm.m_name" required>
          </div>
          <div class="form-group">
            <label for="m_password">密码</label>
            <input type="password" id="m_password" v-model="addForm.m_password" required>
          </div>
          <div class="form-group">
            <label for="confirm_password">确认密码</label>
            <input type="password" id="confirm_password" v-model="addForm.confirm_password" required>
          </div>
          <div class="form-group">
            <label for="m_gender">性别</label>
            <select id="m_gender" v-model="addForm.m_gender" required>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          <div class="form-group">
            <label for="m_nickname">昵称</label>
            <input type="text" id="m_nickname" v-model="addForm.m_nickname" required>
          </div>
          <div class="form-group">
            <label for="m_phone">电话</label>
            <input type="tel" id="m_phone" v-model="addForm.m_phone" required>
          </div>
          <div class="form-group">
            <label for="m_email">邮箱</label>
            <input type="email" id="m_email" v-model="addForm.m_email" required>
          </div>
          <button type="submit" class="submit-button">添加</button>
          <button type="button" @click="closeAddModal" class="cancel-button">取消</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    managers: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      isAddModalOpen: false,
      addForm: {
        m_name: '',
        m_password: '',
        confirm_password: '',
        m_gender: '',
        m_nickname: '',
        m_phone: '',
        m_email: ''
      },
      managerToDelete: null,
      searchKeyword: '',
      searchField: '',
      filteredManagers: []
    }
  },
  watch: {
    managers: {
      handler(newVal) {
        this.filteredManagers = newVal;
      },
      immediate: true
    }
  },
  methods: {
    openAddModal() {
      this.isAddModalOpen = true;
    },
    closeAddModal() {
      this.isAddModalOpen = false;
      this.addForm = {
        m_name: '',
        m_password: '',
        confirm_password: '',
        m_gender: '',
        m_nickname: '',
        m_phone: '',
        m_email: ''
      };
    },
    async submitAddManager() {
      if (!this.addForm.m_password || !this.addForm.confirm_password) {
        alert('请输入密码和确认密码');
        return;
      }
      if (this.addForm.m_password !== this.addForm.confirm_password) {
        alert('两次输入的密码不一致');
        return;
      }

      if (!this.addForm.m_name || !this.addForm.m_gender || !this.addForm.m_nickname || !this.addForm.m_phone || !this.addForm.m_email) {
        alert('请填写所有必填字段');
        return;
      }

      try {
        const token = localStorage.getItem('token');
        const response = await axios.post('http://localhost:5000/manager/add_mng', {
          m_name: this.addForm.m_name,
          m_password: this.addForm.m_password,
          m_gender: this.addForm.m_gender,
          m_nickname: this.addForm.m_nickname,
          m_phone: this.addForm.m_phone,
          m_email: this.addForm.m_email
        }, {
          headers: {
            'Authorization': 'Bearer ' + token,
          }
        });

        const data = response.data;
        if (data.state === 1) {
          alert(data.message);
          this.closeAddModal();
          this.$emit('refresh-managers'); // 刷新管理员列表
        } else {
          alert(`添加失败: ${data.message}`);
        }
      } catch (error) {
        console.error('Error adding manager:', error);
        if (error.response && error.response.data && error.response.data.message) {
          alert(`添加管理员失败: ${error.response.data.message}`);
        } else {
          alert('添加失败，请稍后再试');
        }
      }
    },
    confirmDelete(managerId) {
      const managerName = this.managers.find(m => m.mng_id === managerId)?.mng_name || '该管理员';
      if (confirm(`确定要删除管理员 ${managerName} 吗？`)) {
        this.deleteManager(managerId);
      }
    },
    async deleteManager(managerId) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.delete('http://localhost:5000/manager/delete_mng', {
          headers: {
            'Authorization': 'Bearer ' + token,
          },
          data: {
            delete_by: 'mng_id',
            value: managerId
          }
        });

        const data = response.data;
        if (data.state === 1) {
          alert(data.message);
          this.$emit('refresh-managers'); // 刷新管理员列表
        } else {
          alert(`删除失败: ${data.message}`);
        }
      } catch (error) {
        console.error('Error deleting manager:', error);
        alert(error.response?.data?.message || '删除失败，请稍后再试');
      }
    },
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    filterManagers() {
      if (!this.searchKeyword) {
        this.filteredManagers = this.managers;
        return;
      }
      const keyword = this.searchKeyword.toLowerCase();
      this.filteredManagers = this.managers.filter(manager => {
        if (!this.searchField) { // 不限条件搜索
          return (
            manager.mng_id.toString().includes(keyword) ||
            manager.mng_name.toLowerCase().includes(keyword) ||
            manager.mng_nickname.toLowerCase().includes(keyword) ||
            manager.mng_gender.toLowerCase().includes(keyword) ||
            manager.mng_email.toLowerCase().includes(keyword) ||
            manager.mng_phone.toLowerCase().includes(keyword) ||
            this.formatDate(manager.mng_create_at).toLowerCase().includes(keyword)
          );
        } else {
          let value;
          if (this.searchField === 'mng_create_at') { // 如果搜索字段是注册时间，则格式化后比较
            value = this.formatDate(manager.mng_create_at);
          } else {
            // 对其他字段进行小写转换以进行不区分大小写的搜索
            value = manager[this.searchField];
          }
          return value && value.toString().toLowerCase().includes(keyword);
        }
      });
    }
  }
}
</script>

<style scoped>
.manager-section-container {
  padding: 24px; /* 与用户/文章/评论列表容器一致 */
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06); /* 与用户/文章/评论列表阴影一致 */
  position: relative;
}

.header-container {
  display: flex;
  flex-direction: column; /* 垂直排列子项：标题在上面，操作/搜索在下面 */
  align-items: flex-start; /* 左对齐 */
  margin-bottom: 24px; /* 与其他列表头部间隔一致 */
  width: 100%; /* 确保头部容器宽度为100% */
}

.list-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0; /* 标题下方留出一定空间给操作/搜索行 */
}

.actions-and-search-row { /* 新增的容器，用于并排显示按钮和搜索 */
  display: flex;
  justify-content: space-between; /* 按钮靠左，搜索靠右 */
  align-items: center; /* 垂直居中对齐 */
  width: 100%; /* 占据整行宽度 */
  flex-wrap: wrap; /* 允许换行，适应小屏幕 */
  gap: 16px; /* 元素间的间距 */
}

.action-button { /* 统一的按钮样式 */
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 8px 12px; /* 与其他列表按钮内边距一致 */
  border-radius: 4px; /* 与其他列表按钮圆角一致 */
  cursor: pointer;
  font-size: 14px; /* 统一字体大小 */
  transition: background-color 0.2s ease-in-out;
}

.action-button:hover {
  background-color: #4a90c2; /* 悬停颜色 */
}

.add-button {
  padding: 10px 15px; /* 添加按钮可以稍微大一点 */
  font-size: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06); /* 按钮阴影 */
}

.search-filter-container { /* 搜索和筛选的容器 */
  display: flex;
  align-items: center;
  gap: 16px; /* 搜索框和筛选下拉间距 */
  flex-wrap: wrap; /* 允许换行 */
  margin-left: auto; /* 让搜索部分靠右对齐 */
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); /* 与其他列表表格容器阴影一致 */
  margin-top: 20px;
  width: 100%; /* 确保表格容器宽度为100% */
}

.manager-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px; /* 统一表格字体大小 */
  color: #333;
  white-space: nowrap; /* 防止内容换行 */
}

.manager-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02); /* 与其他列表表头阴影一致 */
}

.manager-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px; /* 与其他列表表头内边距一致 */
  text-align: left;
}

.manager-table td {
  padding: 10px 16px; /* 与其他列表表格单元格内边距一致 */
  border-bottom: 1px solid #eee;
}

.manager-table tbody tr.even-row {
  background-color: #f9f9f9; /* 与其他列表偶数行背景一致 */
}

.manager-table tbody tr:hover {
  background-color: #f5f5f5; /* 与其他列表鼠标悬停背景一致 */
  transition: background-color 0.2s ease-in-out; /* 与其他列表过渡效果一致 */
}

.manager-table tbody td:last-child {
  text-align: center; /* 操作列居中 */
}

.delete-button {
  background-color: #dc3545; /* 红色删除按钮 */
}

.delete-button:hover {
  background-color: #c82333; /* 红色悬停 */
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

/* 模态框样式 - 与用户/文章/评论列表模态框一致 */
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
  width: 400px; /* 统一模态框宽度 */
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
  margin-top: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px; /* 统一按钮字体大小 */
  transition: opacity 0.2s ease-in-out;
}

.submit-button {
  background-color: #5ea8da; /* 绿色提交按钮 */
  color: white;
  margin-right: 10px;
}

.submit-button:hover {
  opacity: 0.9;
}

.cancel-button {
  background-color: #dc3545; /* 红色取消按钮 */
  color: white;
}

.cancel-button:hover {
  opacity: 0.9;
}
</style>