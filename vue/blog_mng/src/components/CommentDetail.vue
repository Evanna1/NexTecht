<template>
  <div class="comment-review-wrapper">
    <button @click="backToList" class="back-button">返回</button>
    <h2 class="page-title">评论(ID:{{ this.parentId }})详情</h2>

    <div v-if="mergedIsLoading" class="loading-state-overlay">
      <div class="loading-spinner"></div>
      <p>加载中，请稍候...</p>
    </div>

    <div v-else class="comment-review-content">
      <div class="comment-details-card">
        <div @click="showUserInfo(Comment.user.id)"class="user-info" v-if="Comment.user">
          <img
            :src="Comment.user.avatar || '/default-avatar.png'"
            :alt="Comment.user.username"
            class="avatar"
          />
          <span>{{ Comment.user.username || '匿名用户' }}</span>
        </div>

        <div class="article-meta-inline">
          <span><strong>创建时间:</strong> {{ formatDate(Comment.create_time) }}</span>
          <span v-if="Comment.parent_id" @click="showCommentDeatail(Comment.parent_id)">
            <strong>父评论ID:</strong>{{ Comment.parent_id }}
          </span>
          <span v-else><strong>父评论ID:无</strong></span>
          <span class="separator">|</span>
          <span><strong>当前状态:</strong> {{ formatStatus(Comment.status) }}</span>
          <span class="separator">|</span>
          <span @click="showCommentLikeUsers(Comment.id)" class="article-meta-inline">
            <strong>点赞数:</strong> {{ Comment.like_count || 0 }}
          </span>
          <span class="separator">|</span>
           <span @click="showCommentReplies(Comment.id)" class="article-meta-inline">
            <strong>回复数:</strong> {{ Comment.reply_count || 0 }}
          </span>
        </div>

        <div class="comment-body">
          <h4>评论内容:</h4>
        </div>
        <div class="comment-text">
          <p>{{ Comment.content }}</p>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-message-overlay">
      <div class="error-content">
        <p>错误：{{ error }}</p>
        <button @click="retryLoad" class="action-button retry-button">重试加载</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CommentDetail',
  props: {
    parentId: {
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
      Comment: {},
      localIsLoading: false,
      error: null
    };
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading;
    }
  },
  created() {
    this.loadCommentDetail();
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
    async loadCommentDetail() {
      this.localIsLoading = true;
      this.error = null;

      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:5000/manager/comment/${this.parentId}`,
          {
            headers: {
              'Authorization': 'Bearer ' + token
            }
          }
        );

        if (response.data.state === 1) {
          this.Comment = { ...response.data.target_comment };
        } else {
          throw new Error(response.data.message || '获取评论信息失败');
        }
      } catch (error) {
        console.error('请求评论详情接口失败:', error);
        this.error = error.message || '获取评论失败，请稍后再试';
      } finally {
        this.localIsLoading = false;
      }
    },
    showCommentLikeUsers(commentId) {
      this.$emit('show-comment-like-users', commentId);
    },
    showCommentReplies(commentId) {
      this.$emit('show-comment-replies', commentId);
    },
    showCommentDeatail(commentId) {
      this.$emit('show-comment-detail', commentId);
    },
    showUserInfo(userId) {
      this.$emit('show-user-info', userId);
    },
    backToList() {
      this.$emit('back-to-list');
    },
    retryLoad() {
      this.loadCommentDetail();
    }
  }
};
</script>

<style scoped>
/* 继承第一个页面的整体容器和基础样式 */
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

/* 页面标题 */
.page-title {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
}

/* 加载状态覆盖层 */
.loading-state-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9); /* 更透明 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 16px; /* 匹配容器圆角 */
}

.loading-spinner {
  border: 5px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 5px solid #5ea8da;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 主要内容容器 */
.comment-review-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}

/* 评论详情卡片 */
.comment-details-card {
  margin-bottom: 30px;
}

/* 文章/评论标题 */
.article-title {
  color: #1a2a3a;
  font-size: 28px;
  margin-bottom: 20px;
  line-height: 1.3;
  font-weight: 700;
  text-align: center;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center; /* 确保垂直居中对齐 */
  margin-bottom: 20px; /* 增加底部间距 */
  padding-bottom: 20px; /* 增加底部填充，为虚线留出空间 */
  border-bottom: 1px dashed #e9ecef; /* 添加虚线 */
  /* 这里的 font-size 和 color 会被 user-info span 覆盖 */
}

/* 调整用户名文本的样式，使其与“创建时间”的字体和颜色一致 */
.user-info span {
  font-size: 15px; /* 匹配 .article-meta-inline span 的字体大小 */
  color: #667788; /* 匹配 .article-meta-inline span 的颜色 */
  line-height: 1.2; /* 调整行高，有助于对齐 */
}

.avatar {
  width: 45px; /* 稍大一点 */
  height: 45px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 12px;
  background-color: #f0f0f0;
  border: 2px solid #eee; /* 添加边框 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); /* 添加阴影 */
}

/* 行内元数据 */
.article-meta-inline {
  font-size: 15px;
  color: #667788; /* 这是 span 的默认颜色 */
  margin-bottom: 25px;
  text-align: center;
  padding-bottom: 15px;
}

.article-meta-inline span {
  display: inline-block;
  margin: 0 10px;
}

.article-meta-inline strong {
  color: #4a5a6a; /* 这是“创建时间”等粗体文字的颜色 */
}

/* 评论内容展示 */
.comment-text {
  background-color: #fcfcfc;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-size: 16px;
  line-height: 1.8;
  color: #444;
  white-space: pre-wrap;
  min-height: 100px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 25px; /* 添加间距 */
}

/* 元数据（创建时间、点赞数等） - 此处样式可能不需要变动，因为 article-meta-inline 已经处理了大部分 */
.article-meta {
  font-size: 15px;
  color: #667788;
  padding-bottom: 15px;
  margin-bottom: 25px;
  display: grid; /* 使用 Grid 布局 */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* 响应式列 */
  gap: 10px; /* 列间距 */
}

.article-meta p {
  margin-bottom: 0; /* 移除默认段落外边距 */
  line-height: 1.6;
}

.article-meta strong {
  color: #4a5a6a;
}

/* 按钮样式 */
.back-button {
  background-color: #5ea8da;
  color: white;
  border: none;
  padding: 10px 20px; /* 稍大 */
  border-radius: 8px; /* 圆角 */
  cursor: pointer;
  font-size: 16px; /* 稍大 */
  transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
  margin-bottom: 20px; /* 与下方内容保持间距 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.back-button:hover {
  background-color: #4a90c2;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.back-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* 错误消息覆盖层 */
.error-message-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.95); /* 更不透明 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 16px;
}

.error-content {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #dc3545; /* 错误颜色 */
  font-size: 18px;
}

.retry-button {
  background-color: #f5a623; /* 醒目的重试按钮颜色 */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
  margin-top: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.retry-button:hover {
  background-color: #e09a1e;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.retry-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* 评论状态小标签（可选，如果需要突出显示） */
.comment-status {
  background-color: #5ea8da; /* 蓝色背景 */
  color: white;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block; /* 保持在行内 */
  margin-left: 15px; /* 与标题保持距离 */
}

.comment-body h4 {
  font-size: 18px;
  color: #334455;
  margin-bottom: 15px;
  border-left: 4px solid #5ea8da;
  padding-left: 10px;
}

/* 不同状态的不同颜色 (可选) */
.comment-status.status-0 { background-color: #28a745; } /* 正常 - 绿色 */
.comment-status.status-1 { background-color: #dc3545; } /* 已删除 - 红色 */
.comment-status.status-2 { background-color: #ffc107; color: #333; } /* 屏蔽 - 黄色 */
.comment-status.status-3 { background-color: #6c757d; } /* 举报 - 灰色 */
</style>