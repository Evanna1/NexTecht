<template>
  <div class="comment-review-wrapper">
    <button @click="backToList" class="back-button">返回</button>
    <h2 class="page-title">评论(ID: {{ this.commentId }})的审核</h2>

    <div v-if="mergedIsLoading" class="loading-state-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>

    <div v-else class="comment-review-content">
      <div class="comment-details-card">
        <h3 class="article-title">评论内容</h3>
        <div class="article-meta">
          <div class="article-meta-inline">
            <span><strong>作者:</strong>{{ commentAuthor }} </span>
            <span class="separator">|</span>
            <span><strong>创建时间:</strong>{{ formatDate(createTime)}}</span>
            <span><strong>当前状态:</strong> {{ status === 0 ? '正常' : '封禁' }}</span>
          </div>
        </div>
        <p class="comment-text">{{ commentContent }}</p>
      </div>

      <div class="status-actions-group">
        <div class="status-toggle-buttons">
          <label class="status-label">是否屏蔽评论：</label>
          <button @click="toggleCommentStatus(1)" :class="{ 'active-status': commentStatus === 1 }" class="status-button">
            <i>是</i>
          </button>
          <button @click="toggleCommentStatus(0)" :class="{ 'active-status': commentStatus === 0 }" class="status-button">
            <i>否</i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    commentId: {
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
      localIsLoading: false,
      isBlocked: false // 用于跟踪评论是否被屏蔽
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadCommentContent();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无';
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    async loadCommentContent() {
      this.localIsLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.commentId}/content`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        const data = response.data;
        if (data.state === 1) {
          this.commentContent = data.content;
          this.commentAuthor = data.author;
          this.createTime = data.create_time;
          this.updateTime = data.update_time;
          this.status=data.status;
        } else {
          console.error('获取评论内容失败:', data.message);
        }
      } catch (error) {
        console.error('请求评论内容接口失败:', error);
      } finally {
        this.localIsLoading = false;
      }
    },
    async approveComment() {
      await this.reviewComment(true);
    },
    async rejectComment() {
      await this.reviewComment(false);
    },
    async toggleCommentStatus(action) {
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `http://localhost:5000/manager/comment/${this.commentId}/status`,
          { status: action }, // 0: 不屏蔽, 1: 屏蔽
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );
        this.isBlocked = action === 1;
        alert('评论状态更新成功');
        this.loadCommentContent(); // 调用此方法刷新评论内容
      } catch (error) {
        console.error('更新评论状态失败:', error);
        alert('更新评论状态失败，请稍后再试');
      }
    },
    backToList() {
       this.$emit('show-comments');
    }
  }
};
</script>

<style scoped>
/* Overall container and base styling */
.comment-review-wrapper {
  padding: 30px;
  background-color: #f9fafb; /* Lighter background for the entire page/section */
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  max-width: 800px; /* Limit width for better focus */
  margin: 40px auto; /* Center the container */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  position: relative; /* For positioning the loading overlay */
}

.page-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
}

.article-title {
  color: #1a2a3a;
  font-size: 28px;
  margin-bottom: 20px;
  line-height: 1.3;
  font-weight: 700;
  text-align: center;
}

.article-meta {
  font-size: 15px;
  color: #667788;
  border-bottom: 1px dashed #e9ecef;
  padding-bottom: 15px;
  margin-bottom: 25px;
}

.article-meta p {
  margin-bottom: 8px;
  line-height: 1.6;
}

.article-meta p:last-child {
  margin-bottom: 0;
}

.article-meta strong {
  color: #4a5a6a;
}

.article-meta-inline {
  font-size: 15px;
  color: #667788;
  margin-bottom: 25px; /* Adjust as needed */
  text-align: center; /* Center the line */
  border-bottom: 1px dashed #e9ecef; /* Keep the existing separator line */
  padding-bottom: 15px; /* Keep existing padding */
}

.article-meta-inline span {
  display: inline-block; /* Allows vertical alignment and spacing */
  margin: 0 10px; /* Space between items */
}

.article-meta-inline .separator {
  color: #cccccc; /* Lighter color for the separator */
  font-weight: normal;
}

.article-meta-inline strong {
  color: #4a5a6a;
}

/* Loading State */
.loading-state-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9); /* More opaque */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100; /* Ensure it's on top */
  border-radius: 16px; /* Match container border-radius */
}

.loading-spinner {
  border: 5px solid rgba(0, 0, 0, 0.1); /* Thicker border */
  border-radius: 50%;
  border-top: 5px solid #5ea8da; /* Main color */
  width: 50px; /* Larger spinner */
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Main Content Wrapper */
.comment-review-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}

/* Section Headings */
h3, h4 {
  color: #1a2a3a;
  margin-top: 0; /* Reset default margin */
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee; /* Subtle separator for sections */
  font-size: 22px;
  font-weight: 600;
}

h4 {
  font-size: 18px;
  color: #334455;
  border-bottom: none; /* Only apply to h3 */
  margin-top: 30px; /* Space above new sections */
}

/* Comment Content Display */
.comment-details-card {
  margin-bottom: 30px;
}

.comment-text {
  background-color: #fcfcfc;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-size: 16px;
  line-height: 1.8;
  color: #444;
  white-space: pre-wrap; /* Preserves formatting like line breaks from user input */
  min-height: 100px; /* Ensure a minimum height for comment display */
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05); /* Subtle inner shadow */
}

/* Button Styling */
.action-button {
  display: inline-flex; /* Align icon and text */
  align-items: center;
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
  margin-right: 15px; /* Space between buttons */
  margin-bottom: 15px; /* For wrapping buttons */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-decoration: none; /* Ensure no underline if it's a link */
}

.action-button:hover {
  background-color: #4c7ea1;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.action-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.button-icon {
  margin-right: 8px; /* Space between icon and text */
  font-size: 18px;
}

/* Specific Button Colors */
.approve-button {
  background-color: #28a745; /* Green for approve */
}
.approve-button:hover {
  background-color: #218838;
}

.reject-button {
  background-color: #dc3545; /* Red for reject */
}
.reject-button:hover {
  background-color: #c82333;
}

.back-button {
  background-color: #6c757d; /* Gray for back */
}
.back-button:hover {
  background-color: #5a6268;
}

/* Button Groups */
.review-actions-group, .status-actions-group {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px dashed #eee; /* Subtle top border for section separation */
}

.button-group {
  display: flex;
  flex-wrap: wrap; /* Allow buttons to wrap */
  gap: 15px; /* Space between buttons */
  margin-top: 15px;
}

/* Status Toggle */
.status-toggle-buttons {
  display: flex;
  align-items: center;
  margin-top: 15px;
}

.status-label {
  margin-right: 15px;
  font-size: 16px;
  color: #333333;
  font-weight: 600;
}

.status-button {
  background-color: #83b4e5;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s ease;
  margin-top: 1px;
  margin-right: 10px; 
  display: inline-flex; 
  align-items: center;  
  justify-content: center; 
}

.status-button:hover {
  background-color: #3e5b71;
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
}

.back-button:hover {
  background-color: #4a90c2;
}
</style>