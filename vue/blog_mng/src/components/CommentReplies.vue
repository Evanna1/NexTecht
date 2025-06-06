<template>
  <div class="comment-replies-container">
    <button @click="backToList" class="back-button">返回</button>
    <div class="header-container">
      <h2 class="list-title">评论(ID: {{ this.commentId }})的回复列表</h2>
      <div class="search-filter-container">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="currentColor" class="search-icon">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
          <input type="text" v-model="searchKeyword" @input="filterReplies" placeholder="输入关键词搜索回复...">
        </div>
        <div class="filter-select">
          <select v-model="searchField" id="search-field" @change="filterReplies">
            <option value="">不限</option>
            <option value="id">回复ID</option> <option value="author">作者</option>
            <option value="create_time">创建时间</option>
            <option value="status">状态</option>
            </select>
        </div>
      </div>
    </div>

    <div v-if="mergedIsLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>
    <div v-else class="content-wrapper">
      <div class="comment-info-card">
        <h3>当前评论内容：</h3>
        <h3><span class="comment-content-text">{{ commentContent }}</span></h3>
        <p>回复总数：<span class="reply-count-number">{{ replyCount }}</span></p>
      </div>
      <div class="table-wrapper">
        <table class="replies-table">
          <thead>
            <tr>
              <th>回复ID</th>
              <th>作者</th>
              <th>创建时间</th>
              <th>状态</th>
              <th>所属文章ID</th> <th>父评论/回复ID</th> <th>深度</th>
              <th>点赞数</th>
              <th>回复数</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(reply, index) in filteredReplies" :key="reply.id" :class="{ 'even-row': index % 2 === 1 }">
              <td>{{ reply.id }}</td>
              <td>
                <a @click="showUserInfo(reply.user.id)" class="clickable">
                  {{ reply.user.nickname || reply.user.username }}
                </a>
              </td>
              <td>{{ formatDate(reply.create_time) }}</td>
              <td>
                <span :class="['status-badge', formatStatusClass(reply.status)]">{{ formatStatus(reply.status) }}</span>
              </td>
              <td>
                <a @click="showArticleDetail(reply.article_id)" class="clickable">{{ reply.article_id }}</a>
              </td>
              <td>
                <a v-if="reply.parent_id" @click="showCommentParent(reply.parent_id)" class="clickable">
                  {{ reply.parent_id }}
                </a>
                <span v-else>无</span>
              </td>
              <td>{{ reply.depth }}</td>
              <td>
                 <a @click="showReplyLikeUsers(reply.id)" class="clickable">{{ reply.like_count }}</a>
              </td>
              <td>
                 <a @click="showCommentReplies(reply.id)" class="clickable">{{ reply.reply_count }}</a>
              </td>
              <td>
                <button class="action-button" @click="showCommentReview(reply.id)">详情</button>
                <button class="action-button delete-button" @click="deleteReply(reply.id)">删除</button>
              </td>
            </tr>
            <tr v-if="filteredReplies.length === 0">
              <td colspan="12" class="no-data">{{ searchKeyword || searchField ? '没有符合条件的回复' : '暂无评论回复' }}</td>
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
    commentId: { // 这个 commentId 是当前正在查看其回复的评论的 ID
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
      commentContent: '',
      replyCount: 0,
      replies: [], // 原始回复数据
      localIsLoading: false,
      searchKeyword: '', // 搜索关键词
      searchField: '',   // 搜索字段
      filteredReplies: [] // 过滤后的回复数据
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadCommentReplies();
  },
  watch: {
    // 监听 commentId 变化，重新加载回复
    commentId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.loadCommentReplies();
        }
      }
    },
    // 当 replies 数据更新时，重置 filteredReplies
    replies(newVal) {
      this.filteredReplies = [...newVal];
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
        0: '正常',
        1: '已删除',
        2: '屏蔽',
        3: '举报'
      };
      return statusMap[status] || '未知状态';
    },
    formatStatusClass(status) {
      switch (status) {
        case 0: return 'normal';
        case 1: return 'blocked';
        case 2: return 'blocked';
        case 3: return 'reported';
        default: return '';
      }
    },
    formatApprovalStatusClass(status) {
      switch (status) {
        case 0: return 'pending';
        case 1: return 'normal';
        case 2: return 'blocked';
        default: return '';
      }
    },
    async loadCommentReplies() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.commentId}/replies`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.commentContent = data.comment_content;
          this.replyCount = data.reply_count;
          this.replies = data.replies.map(reply => ({ // 假设后端返回的回复ID是 `id`
            ...reply,
            // 确保回复的 id 是正确的，如果后端返回的是 reply_id，需要在这里映射
            id: reply.id || reply.reply_id // 优先使用 id 字段，如果不存在则使用 reply_id
          }));
          this.filteredReplies = [...this.replies];
        } else {
          console.error('获取评论回复失败:', data.message);
          this.commentContent = '评论加载失败';
          this.replyCount = 0;
          this.replies = [];
          this.filteredReplies = [];
        }
      } catch (error) {
        console.error('请求评论回复接口失败:', error);
        alert('加载评论回复失败，请检查网络或稍后再试。');
        this.commentContent = '评论加载失败';
        this.replyCount = 0;
        this.replies = [];
        this.filteredReplies = [];
      } finally {
        this.localIsLoading = false;
      }
    },
    filterReplies() {
      const keyword = this.searchKeyword.toLowerCase();

      if (!keyword && !this.searchField) {
        this.filteredReplies = [...this.replies];
        return;
      }

      this.filteredReplies = this.replies.filter(reply => {
        if (this.searchField) {
          let value;
          switch (this.searchField) {
            case 'id': // 对应回复的 id
              value = String(reply.id);
              break;
            case 'author':
              value = reply.user.username;
              break;
            case 'create_time':
              value = this.formatDate(reply.create_time);
              break;
            case 'status':
              value = this.formatStatus(reply.status);
              break;
            case 'is_approved':
              value = this.formatApprovalStatus(reply.is_approved);
              break;
            // 如果后端回复数据中包含 article_id 或 parent_id，可以在这里添加 case
            case 'article_id':
              value = reply.article_id; // 假设回复数据中也有 article_id
              break;
            case 'parent_id':
              value = reply.parent_id; // 假设回复数据中也有 parent_id
              break;
            default:
              value = '';
              break;
          }
          return value && value.toString().toLowerCase().includes(keyword);
        } else {
          return (
            String(reply.id).toLowerCase().includes(keyword) || 
            (reply.user.username && reply.user.username.toLowerCase().includes(keyword)) ||
            this.formatDate(reply.create_time).toLowerCase().includes(keyword) ||
            this.formatStatus(reply.status).toLowerCase().includes(keyword) ||
            (reply.article_id && String(reply.article_id).toLowerCase().includes(keyword)) || // 假设回复数据中也有 article_id
            (reply.parent_id && String(reply.parent_id).toLowerCase().includes(keyword)) // 假设回复数据中也有 parent_id
          );
        }
      });
    },
    async deleteReply(replyId) {
      if (!confirm('确定要删除这条回复吗？此操作不可逆。')) {
        return;
      }
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          `http://localhost:5000/manager/comment/${replyId}/delete`, // 假设删除回复也使用这个接口，传入回复ID
          {},
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        if (response.data.state === 1) {
          alert('删除成功');
          this.loadCommentReplies(); // 重新加载回复数据
        } else {
          alert('删除失败: ' + response.data.message);
        }
      } catch (error) {
        console.error('删除回复失败:', error);
        alert('删除失败，请稍后再试');
      }
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    showCommentReview(replyId) {
      // 这里的 showCommentReview 应该是指查看**回复**的详情
      this.$emit('show-comment-review', replyId); // 传递回复ID
    },
    showReplyLikeUsers(replyId) {
      this.$emit('show-comment-like-users', replyId); // 复用评论点赞的页面，传递回复ID
    },
    showCommentReplies(replyId) {
      // 当点击回复的回复数时，可能需要递归显示更深层的回复
      // 这里触发事件，父组件可以决定如何处理，例如加载此回复的子回复
      this.$emit('show-comment-replies', replyId);
    },
    showCommentParent(parentId) {
      // 显示父评论或父回复的详情
      this.$emit('show-comment-parent', parentId);
    },
    showArticleDetail(articleId) {
      // 显示文章详情
      this.$emit('show-articleDetail', articleId);
    },
    backToList() {
      this.$emit('back-to-list');
    }
  }
};
</script>

<style scoped>
/* 与评论列表页面的样式保持一致，并进行必要的调整 */
.comment-replies-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
  text-align: left;
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
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 10;
}

.back-button:hover {
  background-color: #4a90c2;
}

.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  margin-top: 10px; /* 调整标题与顶部距离 */
}

.list-title {
  font-size: 24px; /* 放大标题字体 */
  font-weight: 600;
  color: #333;
}


/* 搜索和筛选样式 */
.search-filter-container {
  display: flex;
  gap: 10px; /* 增加搜索框和下拉菜单之间的距离 */
  align-items: center;
  position: absolute;
  top: 255px; /* 根据实际标题高度调整 */
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
  width: 200px; /* 调整输入框宽度 */
}

.filter-select {
  display: flex;
  align-items: center;
}

.filter-select select {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 7px 10px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
  appearance: none;
  background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2020%2020%22%3E%3Cpath%20fill%3D%22%23666%22%20d%3D%22M5.293%207.293L10%2012l4.707-4.707a1%201%200%20011.414%201.414l-5.414%205.414a1%201%200%2001-1.414%200L3.879%208.707a1%201%200%20011.414-1.414z%22%2F%3E%3C%2Fsvg%3E');
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 12px;
  padding-right: 25px;
}

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
  z-index: 100;
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

.content-wrapper {
  margin-top: 20px;
}

.comment-info-card {
  background-color: #f8fafd;
  border: 1px solid #e0e9f1;
  border-radius: 8px;
  padding: 15px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.comment-info-card h3 {
  font-size: 18px;
  color: #333;
  margin-top: 0;
  margin-bottom: 10px;
  font-weight: 500;
}

.comment-info-card p {
  font-size: 16px;
  color: #555;
  margin-bottom: 0;
}

.comment-content-text {
  font-weight: 600;
  color: #000;
}

.table-wrapper {
  overflow-x: auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  margin-top: 80px;
}

.replies-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.replies-table thead {
  background-color: #f2f2f2;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.02);
}

.replies-table th {
  font-weight: 600;
  color: #555;
  padding: 12px 16px;
  text-align: left;
}

.replies-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.replies-table tbody tr.even-row {
  background-color: #f9f9f9;
}

.replies-table tbody tr:hover {
  background-color: #f5f5f5;
  transition: background-color 0.2s ease-in-out;
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

.reported {
  background-color: #fdf5e6;
  color: #b8860b;
}

.pending {
  background-color: #d9edf7;
  color: #31708f;
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
  background-color: #4a90c2;
}

.action-button.delete-button {
  background-color: #dc3545;
}

.action-button.delete-button:hover {
  background-color: #c82333;
}

.clickable {
  cursor: pointer;
  color: #5ea8da;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.clickable:hover {
  text-decoration: underline;
}

.avatar-container {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 8px;
  flex-shrink: 0;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style>