<template>
  <div class="home-container">
    <!-- 左侧装饰元素 -->
    <div class="side-decoration left-decoration"></div>
    <!-- 右侧装饰元素 -->
    <div class="side-decoration right-decoration"></div>

    <HeaderBar @search="handleSearch" :initialKeyword="keyword" />
    <div class="search-bar">
      <input
        type="text"
        v-model="searchKeyword"
        placeholder="搜索文章标题、内容、作者或标签"
        @keyup.enter="handleSearch(searchKeyword)"
      />
      <button @click="handleSearch(searchKeyword)">搜索</button>
    </div>
    <div class="tabs">
      <button :class="{ active: activeTab === 'recommend' }" @click="setActiveTab('recommend')">
        <i class="fa fa-thumbs-up"></i> 推荐
      </button>
      <button :class="{ active: activeTab === 'follow' }" @click="setActiveTab('follow')">
        <i class="fa fa-heart"></i> 关注
      </button>
      <button :class="{ active: activeTab === 'hot' }" @click="setActiveTab('hot')">
        <i class="fa fa-fire"></i> 热榜
      </button>
    </div>

    <div v-if="isLoading" class="loading-message">正在加载文章...</div>
    <div v-else-if="filteredPosts.length === 0 && keyword" class="no-results-message">
      没有找到与 "{{ keyword }}"相关的文章。
    </div>
    <div v-else-if="filteredPosts.length === 0 && activeTab !== 'recommend' && !keyword" class="no-results-message">
      此分类下暂无文章。
    </div>
    <div class="post-list" v-else>
      <div class="post-card" v-for="post in filteredPosts" :key="post.id" @click="goToPost(post.id)">
        <h3>{{ post.title }}</h3>
        <p class="author">作者：{{ post.user?.username || post.authorName || '未知作者' }}</p>
        <p class="content">{{ getExcerpt(post.content) }}</p>
        <div v-if="post.tags && post.tags.length > 0" class="post-tags">
          <span v-for="tag in post.tags" :key="tag" class="tag-item" @click.stop="searchByTag(tag)">
            {{ tag }}
          </span>
        </div>
        <p v-if="activeTab === 'recommend' && post.score" class="recommend-score">推荐度：{{ post.score }}</p>
        <p v-if="activeTab === 'hot' && post.hot_score" class="hot-score">热度：{{ post.hot_score }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import HeaderBar from '@/components/HeaderBar.vue';
import axios from 'axios';

const route = useRoute();
const router = useRouter();

type TabType = 'recommend' | 'follow' | 'hot';
const activeTab = ref<TabType>('recommend');
const keyword = ref('');
const searchKeyword = ref(''); // 用于搜索输入框的双向绑定
const isLoading = ref(false);

interface User {
  id: number;
  username: string;
  avatar?: string;
}

interface Post {
  id: number | string; // 确保 id 可以是 number 或 string，以适应不同接口
  userId: number;
  title: string;
  content: string;
  tags?: string[];
  user?: User;
  authorName?: string;
  createdAt: string;
  views?: number;
  likes?: number;
  score?: number; // 用于存储推荐度分数
  hot_score?: number; // 用于存储热度分数
}

const allPosts = ref<Post[]>([]);

const fetchPosts = async () => {
  isLoading.value = true;
  console.log(`Fetching posts for tab: ${activeTab.value}, keyword: ${keyword.value}`);
  try {
    let url = '';
    const headers: any = {};
    const params: any = {};
    const token = localStorage.getItem('token');
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    if (activeTab.value === 'recommend') {
      url = 'http://127.0.0.1:5000/article/recommend';
      if (keyword.value) {
        params.keyword = keyword.value;
      }
    } else if (activeTab.value === 'follow') {
      url = 'http://127.0.0.1:5000/following/articles';
    } else if (activeTab.value === 'hot') {
      url = 'http://127.0.0.1:5000/article/hot';
    } else if (keyword.value) {
      url = 'http://127.0.0.1:5000/article/search';
      params.search = keyword.value;
    } else {
      allPosts.value = [];
      isLoading.value = false;
      return;
    }

    if (url) {
      const response = await axios.get(url, { headers, params });
      if (response.data && response.data.state === 1) {
        if (activeTab.value === 'recommend' && Array.isArray(response.data.recommendations)) {
          allPosts.value = response.data.recommendations.map((item: any) => ({
            id: item.article_id,
            userId: item.userId,
            title: item.title,
            content: item.content,
            tags: item.tags || [],
            user: item.user,
            authorName: item.authorName,
            createdAt: item.createdAt,
            views: item.views,
            likes: item.likes,
            //score: item.score,
          } as Post));
        } else if (activeTab.value === 'follow' && Array.isArray(response.data.articles)) {
          allPosts.value = response.data.articles.map((post: any) => ({
            id: post.id,
            userId: post.user_id,
            title: post.title,
            content: post.content,
            tags: post.tag ? post.tag.split(',') : [],
            user: { id: post.user_id, username: post.author },
            authorName: post.author,
            createdAt: post.create_time,
            views: post.read_count,
            likes: post.like_count,
          } as Post));
        } else if (activeTab.value === 'hot' && Array.isArray(response.data.articles)) {
          allPosts.value = response.data.articles.map((post: any) => ({
            id: post.id,
            userId: post.userId,
            title: post.title,
            content: post.content,
            tags: post.tags || [],
            user: post.user,
            authorName: post.authorName,
            createdAt: post.create_time,
            views: post.read_count,
            likes: post.like_count,
            //hot_score: post.hot_score,
          } as Post));
        } else {
          console.warn("No posts data found or in unexpected format", response.data);
        }
      } else {
        console.warn("Fetch posts failed", response.data);
      }
    } else {
      allPosts.value = [];
    }
  } catch (error) {
    console.error('Error fetching posts:', error);
    allPosts.value = [];
  } finally {
    isLoading.value = false;
  }
};

const filteredPosts = computed(() => {
  let listToFilter = [...allPosts.value];

  if (!keyword.value) {
    return listToFilter;
  }

  const searchTerm = keyword.value.toLowerCase();
  return listToFilter.filter(post =>
    (post.title && post.title.toLowerCase().includes(searchTerm)) ||
    (post.content && post.content.toLowerCase().includes(searchTerm)) ||
    (post.user?.username && post.user.username.toLowerCase().includes(searchTerm)) ||
    (post.authorName && post.authorName.toLowerCase().includes(searchTerm)) ||
    (post.tags && post.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
  );
});

const handleSearch = (newKeyword: string) => {
  keyword.value = newKeyword;
  router.push({ query: newKeyword ? { search: newKeyword } : {} });
};

watch(() => route.query.search, (newSearchTerm) => {
  const term = Array.isArray(newSearchTerm) ? newSearchTerm[0] : newSearchTerm;
  keyword.value = term || '';
}, { immediate: true });

watch(activeTab, () => {
  searchKeyword.value = '';
  keyword.value = '';
  router.push({ query: {} });
  fetchPosts();
});

watch(keyword, () => {
  fetchPosts();
});

onMounted(() => {
  fetchPosts();
});

function setActiveTab(tab: TabType) {
  activeTab.value = tab;
}

function goToPost(id: number | string) {
  router.push(`/post/${id}`);
}

function getExcerpt(content: string, length: number = 100): string {
  if (!content) return '暂无内容预览...';
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = content;
  const text = tempDiv.textContent || tempDiv.innerText || '';
  return text.length > length ? text.slice(0, length) + '...' : text;
}

function searchByTag(tag: string) {
  if (!tag) return;
  searchKeyword.value = tag;
  handleSearch(tag);
}
</script>

<style scoped>
/* 引入 Font Awesome 样式，你需要确保你的项目已经包含了 Font Awesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css');

.home-container {
  padding: 0;
  background: #f9f9f9;
  min-height: 100vh;
  padding-top: 60px; /* 确保内容不被固定的 HeaderBar 遮挡 */
  font-family: Arial, sans-serif;
  position: relative; /* 用于定位左右装饰元素 */
}

/* 左右装饰元素的样式 */
.side-decoration {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100px; /* 装饰元素的宽度 */
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.8));
  pointer-events: none; /* 防止装饰元素影响鼠标事件 */
}

.left-decoration {
  left: 0;
}

.right-decoration {
  right: 0;
}

.search-bar {
  display: flex;
  justify-content: center;
  padding: 15px 20px; /* 恢复一些上下 padding */
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  border-radius: 25px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  /* 添加上外边距，使其往下移 */
  margin-top: 30px;
}

.search-bar input[type="text"] {
  flex-grow: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 25px 0 0 25px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
  max-width: 800px;
}

.search-bar input[type="text"]:focus {
  border-color: #007bff;
}

.search-bar button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 0 25px 25px 0;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.search-bar button:hover {
  background-color: #0056b3;
}

.tabs {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  padding: 0 10px;
  flex-wrap: wrap;
}

.tabs button {
  padding: 10px 20px;
  margin: 5px;
  background: #e9ecef;
  border: none;
  cursor: pointer;
  border-radius: 20px;
  font-size: 16px;
  color: #495057;
  transition: background-color 0.2s ease, color 0.2s ease;
  display: flex; /* 使图标和文字对齐 */
  align-items: center; /* 垂直居中 */
}

.tabs button:hover,
.tabs button.active {
  background: #007bff;
  color: white;
  font-weight: bold;
}

/* Font Awesome 图标 */
.tabs button i.fa {
  margin-right: 8px;
  font-size: 18px; /* 调整图标大小 */
  vertical-align: middle; /* 使图标与文字垂直居中 */
}

/* 为不同的 Tab 图标设置颜色 */
.tabs button:nth-child(1) i.fa { /* 推荐图标 */
  color: #28a745; /* 绿色 */
}

.tabs button:nth-child(2) i.fa { /* 关注图标 */
  color: #dc3545; /* 红色 */
}

.tabs button:nth-child(3) i.fa { /* 热榜图标 */
  color: #ffc107; /* 黄色 */
}

.tabs button.active:nth-child(1) i.fa,
.tabs button.active:nth-child(2) i.fa,
.tabs button.active:nth-child(3) i.fa {
  color: white; /* 激活状态时图标颜色为白色 */
}

/* Font Awesome 类名 */
.fa-thumbs-up::before { content: "\f164"; } /* 推荐 */
.fa-heart::before { content: "\f004"; } /* 关注 - 更换为心形图标 */
.fa-fire::before { content: "\f06d"; } /* 热榜 */

.post-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 16px 20px;
}

.post-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  border: 1px solid transparent;
  transition: border-color 0.3s;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  border-color: #007bff;
}

.post-card h3 {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #343a40;
}

.post-card .author {
  color: #6c757d;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.post-card .content {
  font-size: 16px;
  color: #495057;
  line-height: 1.7;
  margin-bottom: 15px;
}

.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag-item {
  background-color: #e0f7fa;
  color: #00acc1;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.tag-item:hover {
  background-color: #007bff;
  color: white;
}

.recommend-score,
.hot-score {
  font-size: 14px;
  color: #007bff;
  margin-top: 8px;
}

.loading-message,
.no-results-message {
  text-align: center;
  padding: 40px 20px;
  font-size: 18px;
  color: #6c757d;
}

@media (max-width: 768px) {
  .tabs button {
    padding: 8px 15px;
    font-size: 15px;
  }
  .post-card h3 {
    font-size: 20px;
  }
  .post-card .content {
    font-size: 15px;
  }
}
</style>