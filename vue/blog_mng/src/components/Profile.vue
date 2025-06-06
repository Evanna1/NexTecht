<template>
  <div class="profile">
    <div class="avatar-wrapper">
      <img 
        :src="profile.mng_avatar ? '/' + profile.mng_avatar : '/mng_avatar.jpg'" 
        alt="头像" 
        class="avatar" 
        @error="handleImgError"
      />
    </div>
    <div class="info">
      <p><strong>管理员ID：</strong>{{ profile.mng_id }}</p>
      <p><strong>姓名：</strong>{{ profile.mng_name }}</p>
      <p><strong>昵称：</strong>{{ profile.mng_nickname }}</p>
      <p><strong>性别：</strong>{{ profile.mng_gender }}</p>
      <p><strong>电话：</strong>{{ profile.mng_phone }}</p>
      <p><strong>邮箱：</strong>{{ profile.mng_email }}</p>
      <p><strong>注册时间：</strong>{{ formattedDate }}</p>
      <button @click="openEditModal" class="edit-button">修改个人信息</button>
    </div>

    <!-- 编辑模态框 -->
    <div v-if="isEditModalOpen" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeEditModal">&times;</span>
        <h2>修改个人信息</h2>
        <form @submit.prevent="updateProfile">
          <div class="form-group">
            <label for="m_name">姓名</label>
            <input type="text" id="m_name" v-model="editForm.m_name" required>
          </div>
          <div class="form-group">
            <label for="m_nickname">昵称</label>
            <input type="text" id="m_nickname" v-model="editForm.m_nickname" required>
          </div>
          <div class="form-group">
            <label for="m_gender">性别</label>
            <select id="m_gender" v-model="editForm.m_gender" required>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          <div class="form-group">
            <label for="m_email">邮箱</label>
            <input type="email" id="m_email" v-model="editForm.m_email">
          </div>
          <div class="form-group">
            <label for="m_phone">电话</label>
            <input type="tel" id="m_phone" v-model="editForm.m_phone">
          </div>
          <div class="form-group">
            <label for="current_password">当前密码 (如需修改密码请输入)</label>
            <input type="password" id="current_password" v-model="editForm.current_password">
          </div>
          <div class="form-group">
            <label for="m_password">新密码 (如需修改密码请输入)</label>
            <input type="password" id="m_password" v-model="editForm.m_password">
          </div>
          <div class="form-group">
            <label for="confirm_password">确认新密码 (如需修改密码请输入)</label>
            <input type="password" id="confirm_password" v-model="editForm.confirm_password">
          </div>
          <button type="submit" class="submit-button">保存修改</button>
          <button type="button" @click="closeEditModal" class="cancel-button">取消</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    profile: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isEditModalOpen: false,
      editForm: {
        m_name: '',
        m_nickname: '',
        m_gender: '',
        m_email: '',
        m_phone: '',
        current_password: '',
        m_password: '',
        confirm_password: ''
      }
    }
  },
  computed: {
    formattedDate() {
      if (!this.profile.mng_create_at) return '-'
      return new Date(this.profile.mng_create_at).toLocaleString()
    }
  },
  methods: {
    handleImgError(event) {
      event.target.src = '/mng_avatar.jpg' // 默认头像
    },
    openEditModal() {
      // 将当前管理员信息填充到表单中
      this.editForm = {
        m_name: this.profile.mng_name || '',
        m_nickname: this.profile.mng_nickname || '',
        m_gender: this.profile.mng_gender || '',
        m_email: this.profile.mng_email || '',
        m_phone: this.profile.mng_phone || '',
        current_password: '',
        m_password: '',
        confirm_password: ''
      }
      this.isEditModalOpen = true
    },
    closeEditModal() {
      this.isEditModalOpen = false
    },
    async updateProfile() {
      // 构造请求体，只包含修改的字段
      const updateData = {}
      if (this.editForm.m_name !== this.profile.mng_name) updateData.m_name = this.editForm.m_name
      if (this.editForm.m_nickname !== this.profile.mng_nickname) updateData.m_nickname = this.editForm.m_nickname
      if (this.editForm.m_gender !== this.profile.mng_gender) updateData.m_gender = this.editForm.m_gender
      if (this.editForm.m_email !== this.profile.mng_email) updateData.m_email = this.editForm.m_email
      if (this.editForm.m_phone !== this.profile.mng_phone) updateData.m_phone = this.editForm.m_phone
      if (this.editForm.m_password !== this.editForm.confirm_password) {
          alert('新密码和确认密码不一致')
          return
        }
      if (this.editForm.m_password || this.editForm.current_password) {
        updateData.current_password = this.editForm.current_password
        updateData.m_password = this.editForm.m_password
      }

      // 如果没有修改任何信息，直接关闭模态框
      if (Object.keys(updateData).length === 0) {
        alert('未对任何信息进行修改')
        this.closeEditModal()
        return
      }

      try {
        const token = localStorage.getItem('token'); // 获取 JWT
        const response = await axios.put('http://localhost:5000/manager/update_profile', updateData, {
          headers: {
            'Authorization': 'Bearer ' + token,
          }
        });

        const data = response.data; // 成功响应
        if (data.state === 1) {
          alert(data.message);
          this.closeEditModal();
          this.$emit('profile-updated');
        } 
      } catch (error) {
        console.error('Error updating profile:', error);
        if (error.response && error.response.data && error.response.data.message) {
          alert(`个人信息更新失败: ${error.response.data.message}`);
        } else {
          alert('更新失败，请稍后再试');
        }
      }
    }
  }
}
</script>

<style scoped>
.profile {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 40px;
  padding: 30px;
  background-color: #f9fbfd;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #eee;
}

.avatar-wrapper {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #ddd;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease-in-out;
}

.avatar:hover {
  transform: scale(1.05);
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info p {
  margin: 0;
  font-size: 17px;
  color: #2c3e50;
  line-height: 1.6;
}

.info p strong {
  font-weight: 600;
  color: #34495e;
}

.edit-button {
  padding: 6px 15px; 
  background-color: #5ea8da;
  color: white;
  border: none;
  border-radius: 3px; 
  cursor: pointer;
  font-size: 14px; 
  transition: background-color 0.3s;
  width: 140px; 
  height: 30px; 
  text-align: center; 
}

.edit-button:hover {
  background-color: #17a0d2;
}

.modal {
  position: fixed;
  z-index: 1;
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
  background-color: #fefefe;
  margin: auto;
  padding: 20px;
  border: 1px solid #888;
  width: 60%;
  max-width: 600px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.submit-button, .cancel-button {
  padding: 10px 15px;
  margin-top: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.submit-button {
  background-color: #4CAF50;
  color: white;
  margin-right: 10px;
}

.submit-button:hover {
  background-color: #45a049;
}

.cancel-button {
  background-color: #f44336;
  color: white;
}

.cancel-button:hover {
  background-color: #d32f2f;
}
</style>