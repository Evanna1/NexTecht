<template>
  <div class="article-detail-container">
    <button @click="backToList" class="back-button">返回</button>
    <h2>文章详情</h2>
    <div v-if="mergedIsLoading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else class="article-content-wrapper">
      <h3 class="article-title">{{ article.title }}</h3>
      <div class="article-meta">
        <div class="article-meta-inline">
          <span><strong>作者:</strong> {{ article.author }}</span>
          <span class="separator">|</span>
          <span><strong>创建时间:</strong> {{ formatDate(article.create_time) }}</span>
          <span class="separator">|</span>
          <span><strong>更新时间:</strong> {{ formatDate(article.update_time) }}</span>
        </div>
      </div>
      <div class="article-body">
        <h4>文章内容:</h4>
        <div class="article-text" v-html="article.content"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    articleId: {
      type: [String, Number],
      required: true,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      article: {},
      localIsLoading: false,
    }
  },
  computed: {
    mergedIsLoading() {
      return this.isLoading || this.localIsLoading
    },
  },
  watch: {
    articleId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchArticleDetail()
        }
      },
    },
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '无'
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    stripHtmlTags(str) {
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = str
      return tempDiv.textContent || tempDiv.innerText || ''
    },
    async fetchArticleDetail() {
      this.localIsLoading = true
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get(
          `http://localhost:5000/manager/article_detail/${this.articleId}`,
          {
            headers: {
              Authorization: 'Bearer ' + token,
            },
          },
        )
        if (response.data.state === 1) {
          this.article = response.data.article
        }
      } catch (error) {
        console.error('获取文章详情失败:', error)
        alert('获取文章详情失败，请稍后再试')
      } finally {
        this.localIsLoading = false
      }
    },
    backToList() {
      this.$emit('back-to-list')
    },
  },
}
</script>

<style scoped>
.article-detail-container {
  padding: 30px;
  background-color: #f9fafb; /* Lighter background for the whole page/section */
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  text-align: left;
  max-width: 900px; /* Limit width for better readability */
  margin: 40px auto; /* Center the container */
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}

h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 600;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 15px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 250px;
  font-size: 18px;
  color: #555;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #5ea8da;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.article-content-wrapper {
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
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

.article-body h4 {
  font-size: 18px;
  color: #334455;
  margin-bottom: 15px;
  border-left: 4px solid #5ea8da;
  padding-left: 10px;
}

.article-text >>> blockquote {
  margin-left: 0;
  padding-left: 1em;
  border-left: 4px solid #ccc;
  color: #555;
  font-style: italic;
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
