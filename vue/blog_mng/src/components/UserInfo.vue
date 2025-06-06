<template>
    <div class="admin-user-profile-container">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在加载用户数据...</p>
    </div>

    <div v-else class="admin-profile-card">
      <button @click="backToList" class="back-button">返回</button>
      <div class="profile-header">
        <div class="user-avatar-admin">
          <img :src="user.avatar" :alt="user.nickname" class="avatar-admin">
        </div>
        <div class="user-basic-info-admin">
          <h2 class="username-admin">{{ user.username }}</h2>
          <p class="intro-admin">个人简介：{{ user.intro || '该用户很懒，没有留下任何介绍。' }}</p>
        </div>
      </div>

      <div class="profile-details-section">
        <h3>基本资料</h3>
        <div class="detail-grid">
          <div class="detail-item-admin">
            <span class="detail-label-admin">昵称：</span>
            <span class="detail-value-admin email-value">{{ user.nickname }}</span>
          </div>
          <div class="detail-item-admin">
            <span class="detail-label-admin">状态：</span>
            <span class="detail-value-admin" :class="{'status-active-admin': user.u_status === 0, 'status-inactive-admin': user.u_status === 1}">
              {{ formatStatus(user.u_status) }}
            </span>
          </div>
          <div class="detail-item-admin">
            <span class="detail-label-admin">邮箱：</span>
            <span class="detail-value-admin email-value">{{ user.email }}</span>
          </div>
          <div class="detail-item-admin">
            <span class="detail-label-admin">手机号：</span>
            <span class="detail-value-admin">{{ user.phone }}</span>
          </div>
          <div class="detail-item-admin">
            <span class="detail-label-admin">注册时间：</span>
            <span class="detail-value-admin">{{ formatDate(user.create_at) }}</span>
          </div>
          <div class="detail-item-admin">
            <span class="detail-label-admin">最后登录时间：</span>
            <span class="detail-value-admin">{{ formatDate(user.last_login_at) }}</span>
          </div>
        </div>
      </div>
      <div class="profile-details-section">
        <h3>用户活动统计</h3>
        <div class="data-stats-grid">
          <div @click="showUserLikedArticles(user.id)"class="stat-item">
            <span class="stat-label">发布文章数</span>
            <span class="stat-value">{{ user.article_count }}</span>
          </div>
          <div @click="showUserComments(user.id)"class="stat-item">
            <span class="stat-label">发布评论数</span>
            <span class="stat-value">{{ user.comment_count }}</span>
          </div>
          <div @click="showUserLikedArticles(user.id)"class="stat-item">
            <span class="stat-label">点赞数</span>
            <span class="stat-value">{{ user.like_count }}</span>
          </div>
          <div @click="showFollowers(user.id)"class="stat-item">
            <span class="stat-label">粉丝数</span>
            <span class="stat-value">{{ user.followers_count }}</span>
          </div>
          <div @click="showFollowing(user.id)"class="stat-item">
            <span class="stat-label">关注数</span>
            <span class="stat-value">{{ user.followings_count }}</span>
          </div>
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
    }
  },
  data() {
    return {
      user: {},
      localIsLoading: false
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadUserInfo();
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
        1: '封禁'
      };
      return statusMap[status] || '未知状态';
    },
    async loadUserInfo() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/user/search`,
          {
            params: {
              user_id: this.userId
            },
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.user = data.user;
        } else {
          console.error('获取用户信息失败:', data.message);
          alert(data.message);
        }
      } catch (error) {
        console.error('请求用户信息接口失败:', error);
        alert('获取用户信息失败，请稍后再试');
      } finally {
        this.localIsLoading = false;
      }
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
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
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
.admin-user-profile-container {
  padding: 25px;
  background-color: #f5f7fa; /* 浅灰色背景，更具管理系统感 */
  min-height: calc(100vh - 60px); /* 假设顶部有固定导航栏 */
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.admin-profile-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  padding: 30px;
  width: 100%;
  max-width: 960px; /* 适当放宽最大宽度以容纳更多信息 */
  box-sizing: border-box;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 8px;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #409EFF; /* Ant Design 蓝色 */
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  font-size: 1em;
  color: #666;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: flex-start; 
  padding-bottom: 25px;
  margin-bottom: 25px;
  border-bottom: 1px solid #e8e8e8; 
  flex-wrap: wrap; 
  gap: 20px; 
}

.user-avatar-admin {
  order: 1; 
}

.user-basic-info-admin {
  order: 0; 
}

.avatar-admin {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #409EFF;
  box-shadow: 0 0 0 5px rgba(64, 158, 255, 0.1);
}

.user-basic-info-admin {
  flex-grow: 1;
  min-width: 200px;
}

.username-admin {
  font-size: 1.8em;
  color: #333;
  margin-top: 0;
  margin-bottom: 5px;
  font-weight: 600;
  text-align: center;
}

.nickname-admin, .intro-admin {
  font-size: 0.95em;
  color: #666;
  margin-bottom: 5px;
  line-height: 1.5;
  text-align: center;
}

.profile-actions-admin {
  margin-left: auto; /* 让按钮靠右 */
  display: flex;
  gap: 10px; /* 按钮之间间距 */
  flex-wrap: wrap; /* 允许在小屏幕上换行 */
}

/* 按钮样式 */
.btn-back-list, .btn-action-admin, .btn-danger, .btn-success {
  background-color: #409EFF; /* 主要按钮颜色 */
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: background-color 0.2s ease, transform 0.1s ease;
  white-space: nowrap; /* 防止按钮文本换行 */
}

.btn-back-list:hover, .btn-action-admin:hover {
  background-color: #66b1ff;
}
.btn-back-list:active, .btn-action-admin:active {
  transform: translateY(1px);
}

.btn-danger {
  background-color: #F56C6C; /* 禁用/删除操作的红色 */
}
.btn-danger:hover {
  background-color: #f78989;
}

.btn-success {
  background-color: #67C23A; /* 启用操作的绿色 */
}
.btn-success:hover {
  background-color: #85ce61;
}


.profile-details-section {
  margin-bottom: 30px;
  background-color: #fbfcfd; /* 每个区块的背景 */
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 20px 25px;
}

.profile-details-section h3 {
  font-size: 1.3em;
  color: #333;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 10px 30px; 
}

.detail-item-admin {
  display: flex;
  align-items: baseline; 
  padding: 8px 0; 
}

.detail-label-admin {
  font-size: 0.9em;
  color: #909399;
  font-weight: 500;
  flex-shrink: 0; 
  width: 120px; 
  text-align: left; 
  margin-right: 15px; 
}

.detail-value-admin {
  font-size: 1em;
  color: #303133;
  font-weight: 400;
  word-break: break-all;
  flex-grow: 1; 
  text-align: left;
}

.detail-value-admin.status-active-admin {
  color: #67C23A; 
  font-weight: 600;
}

.detail-value-admin.status-inactive-admin {
  color: #F56C6C; 
  font-weight: 600;
}

/* 数据统计区域 */
.data-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); 
  gap: 15px; /* 减小间距 */
  text-align: center;
}

.stat-item {
  background-color: #f9fafc; 
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
}

.stat-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.stat-label {
  font-size: 0.85em; /* 标签字号略小 */
  color: #909399;
  margin-bottom: 6px; 
  font-weight: 500;
}

.stat-value {
  font-size: 1.6em; /* 数字字号略小 */
  color: #303133;
  font-weight: 700; /* 强调数字 */
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .user-avatar-admin {
    margin-right: 0;
    margin-bottom: 15px;
  }
  .profile-actions-admin {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
  .detail-label-admin {
    text-align: left; /* 小屏幕上标签左对齐 */
    min-width: auto;
    width: auto;
    margin-right: 10px;
    padding-right: 0;
  }
}
</style>