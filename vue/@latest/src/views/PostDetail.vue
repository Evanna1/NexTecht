<template>
  <div class="post-detail-container">
    <HeaderBar @search="handleSearch" :initialKeyword="keyword" />
    <div class="card title-card">
      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-meta" v-if="post.author">
        <span
          class="clickable-author"
          @click="
            post.user_id !== null && currentUserId !== null ? goToAuthorProfile(post.user_id) : null
          "
          >作者: {{ post.author }}</span
        >
        <span>创建时间: {{ formatDate(post.create_time) }}</span>
        <span v-if="post.update_time">更新时间: {{ formatDate(post.update_time) }}</span>
        <span v-if="post.read_count !== undefined && post.read_count !== null"
          >阅读量: {{ post.read_count }}</span
        >
      </div>
      <div v-if="post.tag" class="post-tags">
        <span
          v-for="(tag, index) in post.tag.split('，')"
          :key="index"
          class="tag-item"
          @click.stop="searchByTag(tag.trim())"
        >
          {{ tag.trim() }}
        </span>
      </div>
      <button
        v-if="currentUserId && post.user_id !== null && post.user_id === currentUserId"
        @click="openEditModal"
        class="action-button edit-article-button"
      >
        <i class="fas fa-pencil-alt"></i> 编辑文章
      </button>
    </div>
    <div class="card content-card">
      <div class="post-content" v-html="post.content"></div>
    </div>

    <div class="card interaction-card">
      <div class="interaction-buttons">
        <button
          @click="toggleArticleLike"
          class="interaction-button like-button"
          :class="{ liked: isLiked }"
        >
          ❤️ {{ post.like_count || 0 }}
        </button>

        <button
          @click="toggleArticleFavorite"
          class="interaction-button favorite-button"
          :class="{ favorited: isFavorited }"
        >
          ⭐ {{ post.favorite_count || 0 }}
        </button>

        <button
          v-if="
            currentUserId &&
            post.user_id !== null &&
            post.user_id === currentUserId &&
            post.like_count > 0
          "
          @click="viewLikers"
          class="action-button view-list-button"
        >
          查看 {{ post.like_count }} 个点赞
        </button>
        <button
          v-if="
            currentUserId &&
            post.user_id !== null &&
            post.user_id === currentUserId &&
            post.favorite_count > 0
          "
          @click="viewFavoriters"
          class="action-button view-list-button"
        >
          查看 {{ post.favorite_count }} 个收藏
        </button>
      </div>
    </div>

    <div v-if="showLikersModal" class="modal-overlay" @click.self="showLikersModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>点赞用户列表</h3>
          <button @click="showLikersModal = false" class="close-button">&times;</button>
        </div>
        <div v-if="loadingLikers" class="loading-list">加载中...</div>
        <div v-else-if="likers.length === 0" class="empty-list">暂无用户点赞此文章。</div>
        <div v-else class="user-list">
          <div v-for="(user, index) in likers" :key="index" class="user-list-item">
            <img :src="user.avatar || '/default_avatar.png'" alt="Avatar" class="user-avatar" />
            <span>{{ user.nickname }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showFavoritersModal" class="modal-overlay" @click.self="showFavoritersModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>收藏用户列表</h3>
          <button @click="showFavoritersModal = false" class="close-button">&times;</button>
        </div>
        <div v-if="loadingFavoriters" class="loading-list">加载中...</div>
        <div v-else-if="favoriters.length === 0" class="empty-list">暂无用户收藏此文章。</div>
        <div v-else class="user-list">
          <div v-for="(user, index) in favoriters" :key="index" class="user-list-item">
            <img :src="user.avatar || '/default_avatar.png'" alt="Avatar" class="user-avatar" />
            <span>{{ user.nickname }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>🪄编辑文章</h3>
          <button @click="closeEditModal" class="close-button">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="editTitle">文章标题:</label>
            <input id="editTitle" v-model="editForm.title" placeholder="请输入文章标题..." />
          </div>
          <div class="form-group">
            <label for="editTag">文章标签 (以逗号“，”分隔):</label>
            <input id="editTag" v-model="editForm.tag" placeholder="例如：Vue，JavaScript，前端" />
          </div>
          <div class="form-group">
            <label>文章内容:</label>
            <div class="editor-container">
              <Toolbar
                style="border-bottom: 1px solid #ccc"
                :editor="editorRef"
                :defaultConfig="toolbarConfig"
                :mode="editorMode"
              />
              <Editor
                style="height: 300px; overflow-y: hidden"
                v-model="editForm.content"
                :defaultConfig="editorConfig"
                :mode="editorMode"
                @onCreated="handleEditorCreated"
              />
            </div>
          </div>
          <div class="form-group checkbox-group">
            <label> <input type="checkbox" v-model="editForm.isPublic" /> 公开文章 </label>
          </div>
        </div>
        <div class="modal-footer">
          <button
            @click="submitArticleEdit"
            :disabled="isSubmitting"
            class="action-button primary-button"
          >
            {{ isSubmitting ? '保存中...' : '保存修改' }}
          </button>
          <button @click="closeEditModal" class="action-button secondary-button">取消</button>
        </div>
      </div>
    </div>

    <div class="card comments-card">
      <h2 class="comments-title">评论区</h2>

      <div class="add-comment-form">
        <textarea
          v-model="newCommentContent"
          :placeholder="replyingTo ? `回复 ${replyingTo.user.username}:` : '发表评论...'"
          rows="4"
          ref="commentInput"
        ></textarea>
        <div class="form-actions">
          <button v-if="replyingTo" @click="cancelReply" class="cancel-reply-button">
            取消回复
          </button>
          <button @click="submitComment" :disabled="!newCommentContent.trim()">发送</button>
        </div>
      </div>

      <div class="comment-list">
        <div v-if="loadingComments" class="loading-comments">加载评论中...</div>
        <div v-if="comments.length === 0 && !loadingComments" class="comments-placeholder">
          暂无评论，快来发表第一条评论吧！
        </div>

        <div v-for="comment in comments" :key="comment.id">
          <div v-if="comment.status === 0 || comment.status === 3" class="comment-item">
            <div class="comment-meta">
              <span class="comment-author">{{ comment.user?.username || 'Deleted User' }}</span>
              <span class="comment-time">{{ formatDate(comment.create_time) }}</span>
            </div>
            <div class="comment-content">
              <p>{{ comment.content }}</p>
            </div>
            <div class="comment-actions">
              <button @click="startReply(comment)" class="action-button reply-button">
                回复 ({{ comment.reply_count || 0 }})
              </button>
              <button
                @click="toggleLikeComment(comment)"
                class="action-button like-button"
                :class="{ liked: comment.is_liked }"
              >
                ❤️ {{ comment.like_count || 0 }}
              </button>
              <button @click="reportComment(comment.id)" class="action-button report-button">
                举报
              </button>
              <button
                v-if="currentUserId && comment.user?.id === currentUserId"
                @click="deleteComment(comment.id)"
                class="action-button delete-button"
              >
                删除
              </button>
            </div>

            <div v-if="comment.reply_count > 0" class="replies-section">
              <button
                v-if="!comment.showReplies && !comment.loadingReplies"
                @click="fetchReplies(comment)"
                class="load-replies-button"
              >
                查看全部 {{ comment.reply_count }} 条回复
              </button>
              <button
                v-if="comment.showReplies && comment.replies && comment.replies.length > 0"
                @click="comment.showReplies = false"
                class="load-replies-button"
              >
                收起回复
              </button>
              <div v-if="comment.loadingReplies" class="loading-replies">加载中...</div>

              <div
                v-if="comment.showReplies && comment.replies && comment.replies.length > 0"
                class="reply-list"
              >
                <div v-for="reply in comment.replies" :key="reply.id">
                  <div
                    v-if="reply.status === 0 || reply.status === 3"
                    class="comment-item reply-item"
                  >
                    <div class="comment-meta">
                      <span class="comment-author">{{
                        reply.user?.username || 'Deleted User'
                      }}</span>
                      <span class="comment-time">{{ formatDate(reply.create_time) }}</span>
                    </div>
                    <div class="comment-content">
                      <span v-if="reply.parent_id" class="reply-to">
                        回复 @{{ getParentAuthorUsername(reply.parent_id) }}:
                      </span>
                      {{ reply.content }}
                    </div>
                    <div class="comment-actions">
                      <button
                        @click="toggleLikeComment(reply)"
                        class="action-button like-button"
                        :class="{ liked: reply.is_liked }"
                      >
                        ❤️ {{ reply.like_count || 0 }}
                      </button>
                      <button @click="reportComment(reply.id)" class="action-button report-button">
                        举报
                      </button>
                      <button
                        v-if="currentUserId && reply.user?.id === currentUserId"
                        @click="deleteComment(reply.id)"
                        class="action-button delete-button"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="pagination.total_pages > 1 && !loadingComments" class="comments-pagination">
        <button
          @click="goToPage(pagination.current_page - 1)"
          :disabled="pagination.current_page === 1"
        >
          上一页
        </button>
        <span>第 {{ pagination.current_page }} / {{ pagination.total_pages }} 页</span>
        <button
          @click="goToPage(pagination.current_page + 1)"
          :disabled="pagination.current_page === pagination.total_pages"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { format } from 'date-fns'
import HeaderBar from '@/components/HeaderBar.vue'
// 导入 Wangeditor 的组件和样式
import { Editor, Toolbar } from '@wangeditor/editor-for-vue' // 如果你用的是 Vue 版本的封装
import '@wangeditor/editor/dist/css/style.css'
// 仅导入类型，请注意这里的 'type' 关键字
import type { IEditorConfig, IToolbarConfig } from '@wangeditor/editor' // 添加 IToolbarConfig 也是个好习惯
// 定义文章数据的响应式引用
// 增加 is_liked_by_current_user 和 is_favorited_by_current_user 字段
interface Article {
  id: number | null
  title: string
  content: string
  author: string // username
  user_id: number | null // <-- Need this from backend
  create_time: string | null
  update_time: string | null
  read_count: number
  like_count: number // 文章喜欢数
  favorite_count: number // 文章收藏数
  tag: string | null // 新增：文章标签字段
  permission: number
}

const post = ref<Article>({
  id: null,
  title: '',
  content: '',
  author: '',
  user_id: null, // Need this from backend
  create_time: null,
  update_time: null,
  read_count: 0,
  like_count: 0,
  favorite_count: 0,
  tag: null, // 新增：初始化标签字段
  permission: 0, // 新增：初始化权限字段
})

// 单独的状态变量，用于控制按钮的选中/未选中样式
// These will be updated by separate API calls
const isLiked = ref(false)
const isFavorited = ref(false)

// 定义评论的数据结构和响应式引用
interface Comment {
  id: number
  content: string
  article_id: number
  create_time: string | null
  update_time: string | null
  status: number // 评论状态 (0:正常, 1:已删除, 2:屏蔽, 3:举报)
  is_approved: number // 审核状态 (0:待审核, 1:已通过, 2:未通过)
  like_count: number // 评论点赞数
  reply_count: number // 子评论数
  depth: number // 评论层级 (1为顶级，2为子评论)
  parent_id: number | null // 父评论ID
  user: {
    // 嵌套的用户信息
    id: number
    username: string
    nickname: string // <-- Use nickname for display (assuming backend provides)
    avatar: string // <-- Assuming backend provides avatar
  }
  is_liked?: boolean // 当前用户是否已点赞该评论 (来自后端接口)
  replies?: Comment[] // 用于存储子评论
  showReplies?: boolean // 用于控制子评论的展开/收起
  loadingReplies?: boolean // 用于表示子评论正在加载中
}

// Interface for liker/favoriter users
interface UserInfo {
  nickname: string
  avatar: string
  // Optionally add user_id if needed for navigation later
  user_id: number
}

const comments = ref<Comment[]>([])
const newCommentContent = ref('')
const replyingTo = ref<Comment | null>(null)
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_items: 0,
  per_page: 10,
})
const loadingComments = ref(false)

const route = useRoute()
const router = useRouter()
const commentInput = ref<HTMLTextAreaElement | null>(null)
// 获取当前登录用户的 ID (从 localStorage 获取)
const currentUserId = ref<number | null>(null)

// --- 新增用于查看点赞/收藏用户的响应式数据 ---
const likers = ref<UserInfo[]>([])
const favoriters = ref<UserInfo[]>([])
const showLikersModal = ref(false)
const showFavoritersModal = ref(false)
const loadingLikers = ref(false)
const loadingFavoriters = ref(false)
// --- 新增结束 ---
// 编辑文章相关状态
// 编辑文章相关状态
const showEditModal = ref(false)
// WangEditor 实例的引用，这里我们直接用它来控制编辑器
const editorRef = ref<any>(null) // 使用 ref 来存储编辑器实例
const isSubmitting = ref(false)

const editForm = ref({
  title: '',
  tag: '',
  content: '',
  isPublic: true, // 前端仍然使用布尔值来方便 UI 交互
})

// Wangeditor 配置
const toolbarConfig: Partial<IToolbarConfig> = {
  // 使用 Partial
  excludeKeys: [
    'fullScreen',
    'insertVideo',
    'uploadVideo',
    'uploadImage',
    'insertTable',
    'todo',
    'group-more-style',
    'group-image',
    'group-indent',
    'group-justify',
    'group-link',
    'group-history',
  ],
}
// Wangeditor 编辑器配置
const editorConfig: Partial<IEditorConfig> = {
  // 使用 Partial
  placeholder: '请输入文章内容...',
  autoFocus: false,
  readOnly: false, // 模态框中应该是可编辑的
  MENU_CONF: {
    uploadImage: {
      server: 'http://127.0.0.1:5000/upload/image', // 你的 Flask 上传图片接口
      fieldName: 'file',
      customInsert(res: any, insertFn: Function) {
        // res 即服务端的返回结果
        if (res.state === 1 && res.url) {
          insertFn(res.url, res.alt, res.href) // 插入图片
        } else {
          alert('图片上传失败: ' + (res.message || '未知错误'))
        }
      },
    },
  },
}
const editorMode = 'default' // 编辑器模式

// Wangeditor 创建回调
const handleEditorCreated = (instance: any) => {
  editorRef.value = instance
  // 在编辑器创建后立即设置内容，确保编辑器 DOM 准备就绪
  if (editorRef.value && editForm.value.content) {
    editorRef.value.setHtml(editForm.value.content)
  }
}

// 文章编辑相关功能
// 打开编辑模态框并初始化编辑器
const openEditModal = async () => {
  // 权限检查：确保只有文章作者本人才能编辑
  if (currentUserId.value === null || post.value.user_id !== currentUserId.value) {
    alert('您无权编辑此文章！')
    return
  }
  // --- 修改点 3: openEditModal 中将 permission (number) 转换为 isPublic (boolean) ---
  // 使用当前文章数据初始化表单
  editForm.value = {
    title: post.value.title || '',
    tag: post.value.tag || '',
    content: post.value.content || '',
    isPublic: post.value.permission === 0, // ✨ permission 为 0 表示公开，所以 isPublic 为 true
  }

  showEditModal.value = true
  console.log('showEditModal is now:', showEditModal.value) // Confirm it's true
  // 使用 nextTick 确保模态框的 DOM 已经渲染，然后编辑器组件才会创建
  await nextTick()
  // 注意：这里不需要手动调用 createEditor 了，
  // 因为我们使用的是 <Editor> 组件，它会在 v-if 为 true 时自动创建
  // 编辑器实例会在 handleEditorCreated 中赋值给 editorRef.value
}

// 关闭编辑模态框并销毁编辑器
const closeEditModal = () => {
  // 销毁编辑器以防止内存泄漏
  if (editorRef.value) {
    editorRef.value.destroy()
    editorRef.value = null
  }
  showEditModal.value = false
}

// --- 修改点 4: submitArticleEdit 中将 isPublic (boolean) 转换为 permission (number) ---
// 提交文章编辑
const submitArticleEdit = async () => {
  if (!post.value.id) return

  if (!editForm.value.title.trim() || !editorRef.value.getHtml().trim()) {
    alert('标题和内容不能为空！')
    return
  }

  if (!confirm('确定要保存文章修改吗？')) {
    return
  }

  isSubmitting.value = true

  try {
    const token = localStorage.getItem('token')
    if (!token) {
      alert('请先登录！')
      router.push('/login')
      return
    }

    const payload = {
      title: editForm.value.title,
      content: editorRef.value.getHtml(), // 从编辑器实例获取 HTML 内容
      tag: editForm.value.tag.trim(),
      permission: editForm.value.isPublic ? 0 : 1, // ✨ 后端接收 permission，这里根据 isPublic 转换为 0 或 1
      // 假设后端 'permission: 0' 是公开，'permission: 1' 是私密
    }

    const response = await axios.put(
      `http://127.0.0.1:5000/article/update/${post.value.id}`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      },
    )
    alert('文章更新成功！')

    // 更新本地文章数据
    post.value = {
      ...post.value,
      title: editForm.value.title,
      content: editorRef.value.getHtml(),
      tag: editForm.value.tag.trim(),
      permission: editForm.value.isPublic ? 0 : 1, // ✨ 更新本地 post 对象的 permission
      update_time: new Date().toISOString(), // 假设后端返回新的时间戳，这里暂时用本地时间
    }

    // 关闭模态框
    closeEditModal()
  } catch (error) {
    console.error('更新文章时发生错误:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录！')
        router.push('/login')
      } else if (error.response.status === 403) {
        alert('您无权修改此文章！')
      } else {
        alert(`更新失败: ${error.response.data?.message || error.message}`)
      }
    } else {
      alert(`更新失败: ${error instanceof Error ? error.message : String(error)}`)
    }
  } finally {
    isSubmitting.value = false
  }
}

// 清理编辑器：在组件卸载前销毁编辑器实例
onBeforeUnmount(() => {
  if (editorRef.value) {
    editorRef.value.destroy()
    editorRef.value = null
  }
})

// 原始的 goBack 函数 (保留) - 功能不变
function goBack() {
  // Consider a more dynamic back route if needed
  router.back() // This is often better than a fixed route
  // Or if you always want to go to profile:
  // router.push('/profile');
}

// 新增：跳转到作者主页
const goToAuthorProfile = (authorId: number | null) => {
  if (authorId === null) {
    console.warn('Author ID is not available.')
    return
  }
  // 假设作者主页路由是 /user/:id
  // 如果作者是当前用户，可以考虑跳转到自己的主页路由，或者不做区分
  if (authorId === currentUserId.value) {
    router.push({ name: 'MyProfile' }) // Assuming you have a named route for current user profile
  } else {
    router.push({ name: 'OtherUserProfile', params: { userId: authorId } }) // Assuming a named route for other user profiles
  }
}

// 计算属性：分割文章标签字符串
const articleTags = computed(() => {
  if (!post.value.tag) {
    return []
  }
  // 使用中文逗号分割标签
  return post.value.tag
    .split('，')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)
})

// 辅助函数：格式化日期字符串
const formatDate = (dateString: string | null): string => {
  if (!dateString) {
    return '未知时间'
  }
  try {
    return format(new Date(dateString), 'yyyy-MM-dd HH:mm:ss')
  } catch (e) {
    console.error('Error formatting date:', e)
    return dateString
  }
}

// 辅助函数：根据父评论ID获取父评论的作者用户名 (用于子评论显示 "回复@...")
const getParentAuthorUsername = (parent_id: number | null): string => {
  if (!parent_id) return '未知用户'
  // Find the parent comment first in top-level comments
  const parentComment = comments.value.find((c) => c.id === parent_id)
  if (parentComment) {
    // Assuming comment.user?.username or nickname exists
    return parentComment.user?.username || parentComment.user?.nickname || 'Deleted User'
  }

  // If not found in top-level comments, check replies of top-level comments
  for (const comment of comments.value) {
    if (comment.replies) {
      const parentReply = comment.replies.find((r) => r.id === parent_id)
      if (parentReply) {
        // Assuming reply.user?.username or nickname exists
        return parentReply.user?.username || parentReply.user?.nickname || 'Deleted User'
      }
    }
  }

  return '未知用户'
}

// 获取文章详情 (用于页面加载时获取文章信息，但不包括用户是否点赞收藏的状态)
const fetchArticleDetails = async (articleId: string) => {
  try {
    // Note: This endpoint is assumed NOT to return is_liked/is_favorited by current user
    const token = localStorage.getItem('token') // Get token (still useful for potentially protected articles or getting author_id if needed)
    const response = await axios.get(`http://127.0.0.1:5000/user/article_content/${articleId}`, {
      headers: {
        // Include token even if optional for the endpoint itself, might be needed for author_id
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    })

    console.log('Article API Response (Details only):', response.data)

    if (response.data.state === 1 && response.data.article) {
      // Assign fetched data to post.value
      // Assume backend provides article ID, author user ID, and tag
      post.value = {
        ...post.value, // Keep defaults if needed
        ...response.data.article, // Overwrite with fetched data
        // We need to ensure response.data.article includes user_id and tag here
        user_id: response.data.article.user_id !== undefined ? response.data.article.user_id : null, // Ensure user_id is assigned
        tag: response.data.article.tag !== undefined ? response.data.article.tag : null, // Ensure tag is assigned
        permission:
          response.data.article.permission !== undefined ? response.data.article.permission : 0, // Ensure permission is assigned
      }

      // Do NOT set isLiked or isFavorited here
    } else {
      console.error('Error fetching post details: Invalid response state', response.data)
      alert('加载文章失败：' + (response.data.message || '未知错误'))
      // If article fails to load, redirect
      router.push('/')
    }
  } catch (error) {
    console.error('Error fetching article details:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 404) {
        alert('文章未找到！')
        router.push('/')
      } else {
        alert('加载文章详情失败：' + (error.response.data?.message || error.message))
        router.push('/')
      }
    } else {
      alert('加载文章详情失败：' + (error instanceof Error ? error.message : String(error)))
      router.push('/')
    }
  }
}

// --- New: Check if current user liked the article ---
const checkArticleLikedStatus = async (articleId: number) => {
  const token = localStorage.getItem('token')
  if (!token) {
    isLiked.value = false // Not logged in, so not liked
    return
  }

  try {
    // Assuming a backend endpoint like GET /alike/check_liked/<article_id>
    const response = await axios.get(`http://127.0.0.1:5000/alike/check_liked/${articleId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    console.log('Check Liked Response:', response.data)
    if (response.data.state === 1) {
      isLiked.value = response.data.is_liked || false // Assuming response has is_liked boolean
    } else {
      console.error('Error checking like status:', response.data.message)
      isLiked.value = false // Assume not liked on error
    }
  } catch (error) {
    console.error('Error checking like status:', error)
    if (axios.isAxiosError(error) && error.response && error.response.status === 401) {
      console.log('User token invalid for like check.')
      // No need to alert or redirect here, just treat as not logged in/not liked
      isLiked.value = false
    } else {
      console.error('Failed to check like status:', error)
      isLiked.value = false // Assume not liked on other errors
    }
  }
}

// --- New: Check if current user favorited the article ---
const checkArticleFavoritedStatus = async (articleId: number) => {
  const token = localStorage.getItem('token')
  if (!token) {
    isFavorited.value = false // Not logged in, so not favorited
    return
  }

  try {
    // Assuming a backend endpoint like GET /article/check_favorited/<article_id>
    const response = await axios.get(
      `http://127.0.0.1:5000/favorites/check_favorited/${articleId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )
    console.log('Check Favorited Response:', response.data)
    if (response.data.state === 1) {
      isFavorited.value = response.data.is_favorited || false // Assuming response has is_favorited boolean
    } else {
      console.error('Error checking favorite status:', response.data.message)
      isFavorited.value = false // Assume not favorited on error
    }
  } catch (error) {
    console.error('Error checking favorite status:', error)
    if (axios.isAxiosError(error) && error.response && error.response.status === 401) {
      console.log('User token invalid for favorite check.')
      // No need to alert or redirect here, just treat as not logged in/not favorited
      isFavorited.value = false
    } else {
      console.error('Failed to check favorite status:', error)
      isFavorited.value = false // Assume not favorited on other errors
    }
  }
}

// 获取评论列表 (顶级评论，带分页) - 代码保持不变 (除非后端评论API也需要认证才能返回用户点赞状态)
// Based on your first comment code, it seems the comments API *does* support including is_liked based on token.
const fetchComments = async (page: number = 1) => {
  const articleId = route.params.id
  if (!articleId || typeof articleId !== 'string') return

  loadingComments.value = true
  try {
    const token = localStorage.getItem('token') // 获取 token
    const response = await axios.get(`http://127.0.0.1:5000/article/${articleId}/comments`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }), // Only add token if exists
      },
      params: {
        page: page,
        per_page: pagination.value.per_page,
      },
    })

    if (response.data.state === 1) {
      // Ensure comment.is_liked is correctly initialized from backend response if available
      comments.value = response.data.comments.map((comment: Comment) => ({
        ...comment,
        replies: [],
        showReplies: false,
        loadingReplies: false,
        is_liked: comment.is_liked || false, // Initialize is_liked from backend or false
      }))
      pagination.value = {
        current_page: response.data.current_page,
        total_pages: response.data.total_pages,
        total_items: response.data.total_items,
        per_page: response.data.per_page,
      }
    } else {
      console.error('Error fetching comments: Invalid response state', response.data)
      comments.value = [] // Clear comments on error
      pagination.value = { current_page: 1, total_pages: 1, total_items: 0, per_page: 10 }
    }
  } catch (error) {
    console.error('Error fetching comments:', error)
    // Comments might be visible to non-logged-in users, only alert/redirect on specific errors
    if (axios.isAxiosError(error) && error.response && error.response.status === 401) {
      console.log('User token invalid for comments fetch, may not get personalized like status.')
      // No need to alert or redirect here if comments are publicly visible
    } else {
      console.error('Failed to fetch comments:', error)
      // Optionally alert for other errors if comments are critical
    }
    comments.value = []
    pagination.value = { current_page: 1, total_pages: 1, total_items: 0, per_page: 10 }
  } finally {
    loadingComments.value = false
  }
}

// 获取子评论列表 - 代码保持不变 (更新了 is_liked 初始化)
const fetchReplies = async (parentComment: Comment) => {
  if (!parentComment || parentComment.reply_count === 0) return

  if (parentComment.replies && parentComment.replies.length > 0 && parentComment.showReplies) {
    parentComment.showReplies = false
    return
  }
  if (parentComment.replies && parentComment.replies.length > 0 && !parentComment.showReplies) {
    parentComment.showReplies = true
    return
  }

  parentComment.loadingReplies = true
  try {
    const token = localStorage.getItem('token') // Get token
    const response = await axios.get(`http://127.0.0.1:5000/comment/${parentComment.id}/replies`, {
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }), // Only add token if exists
      },
    })

    if (response.data.state === 1) {
      // Ensure reply.is_liked is correctly initialized
      parentComment.replies = response.data.replies.map((reply: Comment) => ({
        ...reply,
        is_liked: reply.is_liked || false, // Initialize is_liked from backend or false
      }))
      parentComment.showReplies = true
    } else {
      console.error('Error fetching replies: Invalid response state', response.data)
      // Only alert for critical errors, not just missing personalized state
      // alert("加载回复失败: " + (response.data.message || "未知错误"));
      parentComment.replies = []
    }
  } catch (error) {
    console.error('Error fetching replies:', error)
    if (axios.isAxiosError(error) && error.response && error.response.status === 401) {
      console.log('User token invalid for replies fetch, may not get personalized like status.')
      // No need to alert or redirect here if replies are publicly visible
    } else {
      console.error('Failed to fetch replies:', error)
      // Optionally alert for other errors
    }
    parentComment.replies = []
  } finally {
    parentComment.loadingReplies = false
  }
}

// 提交评论或回复 - 代码保持不变
const submitComment = async () => {
  const articleId = post.value.id
  if (!articleId || typeof articleId !== 'number') {
    // Check if articleId is number after fetch
    console.error('Article ID is not loaded yet.')
    alert('文章信息未加载，无法发表评论。')
    return
  }
  if (!newCommentContent.value.trim()) return

  if (!currentUserId.value) {
    alert('请先登录才能发表评论！')
    router.push('/login')
    return
  }

  const payload: { content: string; parent_id?: number | null } = {
    // Allow parent_id to be null
    content: newCommentContent.value.trim(),
  }

  if (replyingTo.value) {
    payload.parent_id = replyingTo.value.id
  } else {
    payload.parent_id = null // Explicitly set to null for top-level comments
  }

  try {
    const token = localStorage.getItem('token') // 获取 token
    const response = await axios.post(
      `http://127.0.0.1:5000/comment/${articleId}/create`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      },
    )

    if (response.data.state === 1) {
      alert('评论发表成功！')
      newCommentContent.value = ''
      replyingTo.value = null

      // Refresh comments, ideally stay on the current page
      // Re-fetch comments to see the new one and updated counts
      fetchComments(pagination.value.current_page)
    } else {
      console.error('Error submitting comment: Invalid response state', response.data)
      alert('评论发表失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('Error submitting comment:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能发表评论！')
        router.push('/login')
      } else {
        alert('评论发表失败：' + (error.response.data?.message || error.message))
      }
    } else {
      alert('评论发表失败：' + (error instanceof Error ? error.message : String(error)))
    }
  }
}

// 开始回复某个评论 - 代码保持不变 (增加了登录检查)
const startReply = (comment: Comment) => {
  // 如果用户未登录，提示登录
  if (!currentUserId.value) {
    alert('请先登录才能回复评论！')
    router.push('/login')
    return
  }
  replyingTo.value = comment
  newCommentContent.value = ''
  nextTick(() => {
    if (commentInput.value) {
      commentInput.value.focus()
    }
  })
  // Fetch replies when starting a reply (if not already shown)
  if (!comment.showReplies && comment.reply_count > 0) {
    // Only fetch if there are replies to show
    fetchReplies(comment)
  }
}

// 取消回复 - 代码保持不变
const cancelReply = () => {
  replyingTo.value = null
  newCommentContent.value = ''
}

// 切换评论的点赞状态 - 代码保持不变
const toggleLikeComment = async (comment: Comment) => {
  if (!currentUserId.value) {
    alert('请先登录才能点赞评论！')
    router.push('/login')
    return
  }

  const url = comment.is_liked
    ? `http://127.0.0.1:5000/comment/unlike/${comment.id}`
    : `http://127.0.0.1:5000/comment/like/${comment.id}`

  try {
    const token = localStorage.getItem('token') // 获取 token
    const response = await axios.post(
      url,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    // 后端接口返回 updated count 和 is_liked
    if (response.data.state === 1 || response.data.state === 0) {
      comment.like_count = response.data.like_count // 使用后端返回的最新点赞数
      comment.is_liked = response.data.is_liked // 使用后端返回的最新状态
      console.log(response.data.message)
    } else {
      console.error('Error toggling comment like: Invalid response state', response.data)
      alert('操作失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('Error toggling comment like:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能点赞评论！')
        router.push('/login')
      } else {
        alert('操作失败：' + (error.response.data?.message || error.message))
      }
    } else {
      alert('操作失败：' + (error instanceof Error ? error.message : String(error)))
    }
  }
}

// 举报评论 - 代码保持不变
const reportComment = async (commentId: number) => {
  if (!confirm('确定要举报这条评论吗？')) {
    return
  }
  if (!currentUserId.value) {
    alert('请先登录才能举报评论！')
    router.push('/login')
    return
  }
  try {
    const token = localStorage.getItem('token') // 获取 token
    const response = await axios.post(
      `http://127.0.0.1:5000/comment/report/${commentId}`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    if (response.data.state === 1) {
      alert('评论举报成功！感谢您的反馈。')
      // Optimistically update the status in the frontend list
      const findAndUpdateComment = (comments: Comment[], id: number) => {
        for (const c of comments) {
          if (c.id === id) {
            c.status = 3 // Assuming status 3 means reported
            return true
          }
          if (c.replies && findAndUpdateComment(c.replies, id)) {
            return true
          }
        }
        return false
      }
      findAndUpdateComment(comments.value, commentId)
    } else {
      console.error('Error reporting comment: Invalid response state', response.data)
      alert('举报失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('Error reporting comment:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能举报评论！')
        router.push('/login')
      } else {
        alert('举报失败：' + (error.response.data?.message || error.message))
      }
    } else {
      alert('举报失败：' + (error instanceof Error ? error.message : String(error)))
    }
  }
}

// 删除评论 - 代码保持不变
const deleteComment = async (commentId: number) => {
  if (!confirm('确定要删除这条评论吗？')) {
    return
  }
  if (!currentUserId.value) {
    alert('请先登录才能删除评论！')
    router.push('/login')
    return
  }
  try {
    const token = localStorage.getItem('token') // 获取 token
    const response = await axios.delete(`http://127.0.0.1:5000/comment/delete/${commentId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.data.state === 1) {
      alert('评论删除成功！')
      // Remove the comment/reply from the frontend list
      const removeComment = (comments: Comment[], id: number): boolean => {
        for (let i = 0; i < comments.length; i++) {
          if (comments[i].id === id) {
            comments.splice(i, 1)
            return true
          }
          if (comments[i].replies && removeComment(comments[i].replies!, id)) {
            comments[i].reply_count = Math.max(0, comments[i].reply_count - 1) // Decrement parent reply count
            return true
          }
        }
        return false
      }
      removeComment(comments.value, commentId)
    } else {
      console.error('Error deleting comment: Invalid response state', response.data)
      alert('删除失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('Error deleting comment:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录或您无权删除此评论！')
        router.push('/login')
      } else if (error.response.status === 403) {
        alert('您无权删除此评论！')
      } else {
        alert('删除失败：' + (error.response.data?.message || error.message))
      }
    } else {
      alert('删除失败：' + (error instanceof Error ? error.message : String(error)))
    }
  }
}

// 分页跳转 - 代码保持不变
const goToPage = (page: number) => {
  if (page >= 1 && page <= pagination.value.total_pages && page !== pagination.value.current_page) {
    fetchComments(page)
    nextTick(() => {
      document.querySelector('.comments-card')?.scrollIntoView({ behavior: 'smooth' })
    })
  }
}

// --- 新增的文章点赞/取消点赞功能 ---
const toggleArticleLike = async () => {
  const articleId = post.value.id
  if (!articleId || typeof articleId !== 'number') {
    console.error('Article ID is not loaded yet.')
    return
  }

  if (!currentUserId.value) {
    alert('请先登录才能点赞文章！')
    router.push('/login')
    return
  }

  // Determine URL based on current isLiked status
  const url = isLiked.value
    ? `http://127.0.0.1:5000/alike/unlike/${articleId}` // Unlike endpoint
    : `http://127.0.0.1:5000/alike/like/${articleId}` // Like endpoint

  const token = localStorage.getItem('token') // Get token

  try {
    const response = await axios.post(
      url,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    // --- Update state based on backend response ---
    if (response.data.state === 1) {
      // Backend should ideally return the new count and status
      if (response.data.hasOwnProperty('like_count')) {
        post.value.like_count = response.data.like_count
      }
      // Update isLiked status based on the action taken
      isLiked.value = !isLiked.value // Toggle state optimistically or based on response if available
      // If backend explicitly returns is_liked:
      // if (response.data.hasOwnProperty('is_liked')) { isLiked.value = response.data.is_liked; }
    } else if (response.data.state === 0) {
      // Handle specific backend errors
      alert(response.data.message || '操作失败')
    } else {
      console.error('Error toggling article like: Invalid response state', response.data)
      alert('操作失败')
    }
  } catch (error: any) {
    console.error('Error toggling article like:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能点赞文章！')
        router.push('/login')
      } else {
        alert(`操作失败: ${error.response.data?.message || error.response.status}`)
      }
    } else {
      alert(`操作失败: ${error instanceof Error ? error.message : String(error)}`)
    }
    // If an error occurred after an optimistic update, you might need to revert the state
    // This is why getting the final state from the backend is preferred.
  }
}

// --- 新增的文章收藏/取消收藏功能 ---
const toggleArticleFavorite = async () => {
  const articleId = post.value.id
  if (!articleId || typeof articleId !== 'number') {
    console.error('Article ID is not loaded yet.')
    return
  }

  if (!currentUserId.value) {
    alert('请先登录才能收藏文章！')
    router.push('/login')
    return
  }

  // Determine URL based on current isFavorited status
  const url = isFavorited.value
    ? `http://127.0.0.1:5000/article/unfavorite/${articleId}` // Unfavorite endpoint
    : `http://127.0.0.1:5000/article/favorite/${articleId}` // Favorite endpoint

  const token = localStorage.getItem('token') // Get token

  try {
    const response = await axios.post(
      url,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    // --- Update state based on backend response ---
    if (response.data.state === 1) {
      // Backend should ideally return the new count and status
      if (response.data.hasOwnProperty('favorite_count')) {
        post.value.favorite_count = response.data.favorite_count
      }
      // Update isFavorited status based on the action taken
      isFavorited.value = !isFavorited.value // Toggle state optimistically or based on response if available
      // If backend explicitly returns is_favorited:
      // if (response.data.hasOwnProperty('is_favorited')) { isFavorited.value = response.data.is_favorited; }
    } else if (response.data.state === 0) {
      alert(response.data.message || '操作失败')
    } else {
      console.error('Error toggling article favorite: Invalid response state', response.data)
      alert('操作失败')
    }
  } catch (error: any) {
    console.error('Error toggling article favorite:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能收藏文章！')
        router.push('/login')
      } else {
        alert(`操作失败: ${error.response.data?.message || error.response.status}`)
      }
    } else {
      alert(`操作失败: ${error instanceof Error ? error.message : String(error)}`)
    }
    // If an error occurred after an optimistic update, you might need to revert the state
  }
}

// --- 新增：获取点赞用户列表 ---
const fetchLikers = async () => {
  const articleId = post.value.id
  if (!articleId || typeof articleId !== 'number') {
    console.error('Article ID is not loaded yet.')
    return
  }

  if (!currentUserId.value || post.value.user_id !== currentUserId.value) {
    alert('您无权查看此列表！') // Should not happen if button is correctly hidden, but good safeguard
    return
  }

  loadingLikers.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      // Should be covered by currentUserId check, but double check
      alert('请先登录才能查看点赞用户列表！')
      router.push('/login')
      return
    }
    const response = await axios.get(`http://127.0.0.1:5000/alike/list/${articleId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.data.state === 1) {
      likers.value = response.data.data // Assuming 'data' field contains the list [{ nickname, avatar }]
      showLikersModal.value = true // Show the modal on success
    } else {
      console.error('Error fetching likers:', response.data)
      alert('获取点赞用户列表失败：' + (response.data.message || '未知错误'))
      likers.value = [] // Clear the list on error
      showLikersModal.value = false // Hide modal on error
    }
  } catch (error: any) {
    console.error('Error fetching likers:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能查看点赞用户列表！')
        router.push('/login')
      } else if (error.response.status === 403) {
        alert('您无权查看此列表！') // Permission denied for non-author
      } else {
        alert(`获取点赞用户列表失败: ${error.response.data?.message || error.response.status}`)
      }
    } else {
      alert(`获取点赞用户列表失败: ${error instanceof Error ? error.message : String(error)}`)
    }
    likers.value = [] // Clear the list on error
    showLikersModal.value = false // Hide modal on error
  } finally {
    loadingLikers.value = false
  }
}

function searchByTag(tag: string) {
  if (!tag) return
  // Navigate to home and set the search query
  router.push({ path: '/', query: { search: tag } })
}

// --- 新增：获取收藏用户列表 ---
const fetchFavoriters = async () => {
  const articleId = post.value.id
  if (!articleId || typeof articleId !== 'number') {
    console.error('Article ID is not loaded yet.')
    return
  }

  if (!currentUserId.value || post.value.user_id !== currentUserId.value) {
    alert('您无权查看此列表！') // Should not happen if button is correctly hidden, but good safeguard
    return
  }

  loadingFavoriters.value = true
  // Simulate the backend endpoint for getting favoriters
  const url = `http://127.0.0.1:5000/article/favorite/list/${articleId}` // Assuming this endpoint exists

  try {
    const token = localStorage.getItem('token')
    if (!token) {
      // Should be covered by currentUserId check, but double check
      alert('请先登录才能查看收藏用户列表！')
      router.push('/login')
      return
    }
    const response = await axios.get(url, {
      // Assuming GET method for list
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    // Assuming backend response structure is similar to get_likers: { state, message, data: [{ nickname, avatar }] }
    if (response.data.state === 1) {
      favoriters.value = response.data.data // Assuming 'data' field contains the list
      showFavoritersModal.value = true // Show the modal on success
    } else {
      console.error('Error fetching favoriters:', response.data)
      alert('获取收藏用户列表失败：' + (response.data.message || '未知错误'))
      favoriters.value = [] // Clear the list on error
      showFavoritersModal.value = false // Hide modal on error
    }
  } catch (error: any) {
    console.error('Error fetching favoriters:', error)
    if (axios.isAxiosError(error) && error.response) {
      if (error.response.status === 401) {
        alert('请先登录才能查看收藏用户列表！')
        router.push('/login')
      } else if (error.response.status === 403) {
        alert('您无权查看此列表！') // Permission denied for non-author
      } else {
        alert(`获取收藏用户列表失败: ${error.response.data?.message || error.response.status}`)
      }
    } else {
      alert(`获取收藏用户列表失败: ${error instanceof Error ? error.message : String(error)}`)
    }
    favoriters.value = [] // Clear the list on error
    showFavoritersModal.value = false // Hide modal on error
  } finally {
    loadingFavoriters.value = false
  }
}

// Add click handlers for the view buttons
const viewLikers = () => {
  fetchLikers()
}

const viewFavoriters = () => {
  fetchFavoriters()
}

onMounted(async () => {
  const postId = route.params.id
  if (!postId || typeof postId !== 'string') {
    console.error('Article ID is missing!')
    router.push('/') // Redirect if ID is missing
    return
  }

  // 1. 尝试获取当前用户 ID (从 localStorage 获取)
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId) {
    const parsedUserId = parseInt(storedUserId, 10)
    if (!isNaN(parsedUserId)) {
      currentUserId.value = parsedUserId
    }
  }

  // 2. 加载文章详情 (不包含用户点赞收藏状态)
  await fetchArticleDetails(postId)

  // 3. 如果文章详情加载成功且用户已登录，则单独检查当前用户对文章的点赞和收藏状态
  // Ensure post.value.id is a number before calling check status functions
  if (post.value.id !== null && typeof post.value.id === 'number' && currentUserId.value !== null) {
    checkArticleLikedStatus(post.value.id)
    checkArticleFavoritedStatus(post.value.id)
  }

  // 4. 加载评论 (评论的点赞状态可能随评论API返回，如果后端支持)
  if (post.value.id !== null) {
    // Ensure article ID is available before fetching comments
    fetchComments(1) // Load first page of top-level comments
  }
})
</script>

<style scoped>
/* Keep your existing styles and the new styles for clickable author, view buttons, and modals */

/* Make author name clickable */
.post-meta .clickable-author {
  cursor: pointer;
  text-decoration: underline;
  color: #0077cc; /* Link color */
  transition: color 0.2s ease;
}
.post-meta .clickable-author:hover {
  color: #0056b3; /* Darker color on hover */
}

/* New styles for article tags */
.post-tags {
  margin-top: 10px;
  text-align: center;
}

.tag-item {
  display: inline-block; /* Allows margin between tags */
  background-color: #e0f7fa; /* Light blue background */
  color: #0077cc;
  padding: 4px 10px;
  margin: 0 5px 5px 0; /* Add margin to separate tags */
  border-radius: 12px; /* Rounded corners */
  font-size: 13px;
  border: 1px solid #b2ebf2; /* Subtle border */
}
.tag-item:hover {
  background-color: #b2ebf2;
}

/* New styles for liked/favorited interaction buttons */
.interaction-button.like-button.liked {
  background-color: #e53935; /* Red background */
  color: white; /* White text */
}

.interaction-button.favorite-button.favorited {
  background-color: #fbc02d; /* Yellow background */
  color: white; /* White text */
}

/* New style for view list buttons */
.action-button.view-list-button {
  background-color: #e0e0e0;
  color: #333;
  padding: 10px 15px;
  font-size: 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: flex; /* Use flexbox for alignment */
  align-items: center;
  gap: 5px; /* Space between icon (if any) and text */
}
.action-button.view-list-button:hover {
  background-color: #d5d5d5;
}

/* Comment section styles (keeping unchanged) */
.logo-absolute {
  position: absolute;
  top: 20px;
  left: 30px;
  font-family: 'Great Vibes', cursive;
  font-size: 42px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
  z-index: 1000;
}
.post-detail-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
  font-family: 'Helvetica Neue', sans-serif;
}

.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
  padding: 30px;
  margin-bottom: 30px;
  transition:
    box-shadow 0.3s ease,
    transform 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.title-card {
  text-align: center;
}

.post-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  margin-bottom: 15px; /* Add space below title */
}

/* Meta info styles */
.post-meta {
  font-size: 14px;
  color: #555;
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.post-meta span {
  white-space: nowrap;
}

.content-card {
  line-height: 1.7;
  font-size: 16px;
  color: #333;
}

/* Blockquote style */
.post-content >>> blockquote {
  margin-left: 0;
  padding-left: 1em;
  border-left: 4px solid #ccc;
  color: #555;
  font-style: italic;
}

/* Interaction area styles */
.interaction-card {
  text-align: center;
}

.interaction-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 15px;
  flex-wrap: wrap; /* Allow buttons to wrap */
}

.interaction-button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  transition:
    background-color 0.3s ease,
    transform 0.1s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.interaction-button:hover {
  transform: translateY(-1px);
}

.like-button {
  background-color: #ffebee;
  color: #e53935;
}

.like-button:hover {
  background-color: #ef9a9a;
}

.favorite-button {
  background-color: #fff9c4;
  color: #fbc02d;
}

.favorite-button:hover {
  background-color: #fff59d;
}

.interaction-note {
  font-size: 14px;
  color: #777;
  margin-top: 0;
}

/* Comment section styles */
.comments-card {
  /* Inherits .card styles */
}

.comments-title {
  font-size: 24px;
  font-weight: 600;
  margin-top: 0;
  margin-bottom: 20px;
  text-align: center;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

/* Comment form styles */
.add-comment-form {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.add-comment-form textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  box-sizing: border-box;
  margin-bottom: 10px;
  transition: border-color 0.3s ease;
}

.add-comment-form textarea:focus {
  border-color: #0077cc;
  outline: none;
  box-shadow: 0 0 5px rgba(0, 119, 204, 0.3);
}

.form-actions {
  text-align: right;
}

.form-actions button {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-left: 10px;
}

.form-actions button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.form-actions button:not(:disabled):hover {
  opacity: 0.9;
}

.form-actions button:last-child {
  background-color: #0077cc;
  color: white;
}

.cancel-reply-button {
  background-color: #f0f0f0;
  color: #333;
}

/* Comment list styles */
.comment-list {
  margin-top: 20px;
}

.comments-placeholder {
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 20px 0;
}

.loading-comments,
.loading-replies {
  text-align: center;
  color: #666;
  padding: 10px 0;
}

.comment-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

/* Reply styles */
.reply-item {
  margin-left: 20px;
  border-left: 3px solid #ddd;
  background-color: #f5f5f5;
  padding-left: 15px;
}

.comment-meta {
  font-size: 13px;
  color: #777;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-author {
  font-weight: bold;
  color: #555;
}

.comment-content p {
  margin: 0 0 10px 0;
  line-height: 1.6;
  word-wrap: break-word;
}

.comment-actions {
  font-size: 13px;
  color: #777;
  display: flex;
  gap: 15px;
  align-items: center;
  margin-top: 10px;
}

.action-button {
  background: none;
  border: none;
  padding: 0;
  font-size: 13px;
  color: #777;
  cursor: pointer;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-button:hover {
  color: #000;
  text-decoration: underline;
}

.action-button.like-button:hover {
  color: #e53935;
}
/* Liked state */
.action-button.like-button.liked {
  color: #e53935;
  font-weight: bold;
}

.action-button.reply-button:hover {
  color: #0077cc;
}
.action-button.report-button:hover {
  color: #ff9800;
}
.action-button.delete-button:hover {
  color: #f44336;
}

.edit-article-button {
  /* ... 其他样式 ... */
  margin-top: 20px; /* 按钮上方的间距 */
  margin-left: auto; /* 关键：将按钮推到最右边 */
}

.reply-to {
  font-weight: bold;
  color: #0077cc;
  margin-right: 5px;
}

.replies-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #eee;
}

/* Reply list styles */
.reply-list {
  margin-top: 10px;
}

.load-replies-button {
  background: none;
  border: none;
  color: #0077cc;
  cursor: pointer;
  font-size: 13px;
  margin-bottom: 10px;
  display: block;
  text-align: left;
  transition: text-decoration 0.2s ease;
}
.load-replies-button:hover {
  text-decoration: underline;
}

/* Comment pagination styles */
.comments-pagination {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.comments-pagination button {
  padding: 8px 15px;
  font-size: 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
  cursor: pointer;
  margin: 0 5px;
  transition: background-color 0.2s ease;
}

.comments-pagination button:hover:not(:disabled) {
  background-color: #f0f0f0;
}

.comments-pagination button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.comments-pagination span {
  margin: 0 10px;
  font-size: 15px;
  color: #555;
}

/* --- Modal and User List Styles --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 25px;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  max-height: 80%;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  transition: color 0.2s ease;
}
.close-button:hover {
  color: #666;
}

.loading-list,
.empty-list {
  text-align: center;
  color: #666;
  padding: 20px 0;
}

.user-list-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}
.user-list-item:last-child {
  border-bottom: none;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 15px;
  object-fit: cover;
}

.user-list-item span {
  font-size: 16px;
  color: #555;
}

/* --- Modal Overlay --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

/* --- Modal Content --- */
.modal-content {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
  width: 95%;
  max-width: 980px;
  display: flex;
  flex-direction: column;
  height: 90vh;
  max-height: 90vh;
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

/* --- Modal Header --- */
.modal-header {
  padding: 20px 30px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.8em;
  color: #4578ab;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 2.5em;
  color: #6c757d;
  cursor: pointer;
  padding: 0 8px;
  transition:
    color 0.2s ease,
    transform 0.2s ease;
}

.close-button:hover {
  color: #495057;
  transform: rotate(90deg);
}

/* --- Modal Body --- */
.modal-body {
  padding: 30px;
  flex-grow: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
  font-size: 1em;
}

.form-group input:not([type='checkbox']) {
  width: calc(100% - 24px); /* Full width minus padding */
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1em;
  color: #343a40;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.form-group input:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.25); /* Standard focus ring */
  outline: none;
}

/* --- Editor Container (for rich text editor) --- */
.editor-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 5px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  overflow: hidden;
  min-height: 400px;
}

.editor-container .w-e-toolbar,
.editor-container .tox-editor-header {
  border-bottom: 1px solid #e0e0e0 !important;
  padding: 8px 10px;
  background-color: #f8f9fa;
  z-index: 1001;
}

.editor-container .w-e-text-container,
.editor-container .tox-edit-area {
  flex-grow: 1;
  overflow-y: auto;
  min-height: 250px;
  padding: 15px;
}

/* --- Checkbox Group --- */
.checkbox-group {
  display: flex;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 25px;
}

.checkbox-group input[type='checkbox'] {
  margin-right: 12px;
  transform: scale(1.25);
  accent-color: #28a745;
}

.checkbox-group label {
  margin-bottom: 0;
  font-weight: normal;
  color: #343a40;
  cursor: pointer;
}

/* --- Modal Footer --- */
.modal-footer {
  padding: 20px 30px; /* Match header padding */
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background-color: #f8f9fa;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

/* --- Action Buttons --- */
.action-button {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  font-size: 1.05em;
  cursor: pointer;
  transition: all 0.25s ease;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.primary-button {
  background-color: #4578ab;
  color: #ffffff;
  text-decoration: none;
}

.primary-button:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
  text-decoration: none;
  color: #ffffff;
}

.primary-button:active {
  transform: none;
  box-shadow: none;
  background-color: #4578ab;
  color: #ffffff;
  text-decoration: none;
}

.primary-button:disabled {
  background-color: #e0e0e0;
  color: #a0a0a0;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
  text-decoration: none;
}

.secondary-button {
  background-color: #f0f2f5; /* Very light, subtle gray */
  color: #555555; /* Darker text for readability */
  text-decoration: none;
}

.secondary-button:hover {
  background-color: #e0e2e5; /* Slightly darker gray on hover */
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Subtle black shadow on hover */
  text-decoration: none;
  color: #555555; /* Ensure text stays original color on hover */
}

.secondary-button:active {
  transform: none;
  box-shadow: none;
  background-color: #f0f2f5; /* Keep original background color on click */
  color: #555555; /* IMPORTANT: Keep text original color on click */
  text-decoration: none;
}

/* --- Animations --- */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-40px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* --- Responsive Adjustments --- */
@media (max-width: 992px) {
  .modal-content {
    max-width: 850px; /* Adjust for medium screens */
    height: 90vh;
  }
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-width: 95%; /* Allow it to be wider on smaller screens if needed */
    margin: 15px;
    height: 90vh;
  }
  .modal-header h3 {
    font-size: 1.6em;
  }
  .close-button {
    font-size: 2.2em;
  }
  .modal-body,
  .modal-footer,
  .modal-header {
    padding: 20px;
  }
  .action-button {
    padding: 10px 20px;
    font-size: 1em;
  }
}

@media (max-width: 480px) {
  .modal-footer {
    flex-direction: column;
    gap: 10px;
  }
  .action-button {
    width: 100%;
    text-align: center;
  }
  .modal-body {
    padding: 15px;
  }
  .editor-container .w-e-text-container,
  .editor-container .tox-edit-area {
    min-height: 200px; /* Smaller min-height for mobile */
  }
}
</style>
