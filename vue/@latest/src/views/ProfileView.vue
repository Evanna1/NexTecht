<template>
  <div>
    <div class="logo-wrapper">
      <HeaderBar @search="handleSearch" :initialKeyword="keyword" />
      <router-link to="/" class="home-btn" title="主页">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          fill="none"
          stroke="#0077cc"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          viewBox="0 0 24 24"
        >
          <path d="M3 12l9-9 9 9" />
          <path d="M9 21V12H15V21" />
        </svg>
      </router-link>
    </div>

    <div class="profile-container">
      <div class="profile-card">
        <img :src="user.avatar || defaultAvatar" alt="头像" class="avatar" />
        <div class="user-info">
          <h2 class="nickname">{{ user.username }}</h2>
          <p class="bio">{{ user.intro || '这个人很懒，什么都没有写。' }}</p>
          <div class="user-meta">
            <span>邮箱：{{ user.email }}</span>
            <span>注册时间：{{ user.register_time }}</span>
            <span>文章：{{ posts.length }}</span>
            <span @click="activeTab = 'following'" class="clickable-meta"
              >关注：{{ user.following_count }}</span
            >
            <span @click="activeTab = 'followers'" class="clickable-meta"
              >粉丝：{{ user.follower_count }}</span
            >
          </div>
          <button class="edit-profile-btn" @click="openEditModal">修改个人信息</button>
        </div>
      </div>
    </div>

    <div class="profile-tabs">
      <div class="tab-item" :class="{ active: activeTab === 'posts' }" @click="activeTab = 'posts'">
        我的文章 ({{ posts.length }})
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'likes' }"
        @click="((activeTab = 'likes'), fetchLikedArticles())"
      >
        我的喜欢 ({{ user.like_count }})
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'collections' }"
        @click="((activeTab = 'collections'), fetchCollectedArticles())"
      >
        我的收藏 ({{ user.collect_count }})
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'following' }"
        @click="((activeTab = 'following'), fetchFollowing())"
      >
        我的关注 ({{ user.following_count }})
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === 'followers' }"
        @click="((activeTab = 'followers'), fetchFollowers())"
      >
        我的粉丝 ({{ user.follower_count }})
      </div>

      <div
        class="tab-item"
        :class="{ active: activeTab === 'history' }"
        @click="((activeTab = 'history'), fetchBrowseHistory())"
      >
        浏览记录
      </div>
    </div>

    <div class="tab-content">
      <div v-if="activeTab === 'posts'" class="post-section">
        <h3>我的文章</h3>
        <div v-if="posts.length > 0" class="post-list">
          <div v-for="post in posts" :key="post.id" class="post-card" @click="goToPost(post.id)">
            <h4 class="post-title">{{ post.title }}</h4>
            <p class="post-excerpt">{{ getExcerpt(post.content) }}</p>
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
          </div>
        </div>
        <p v-else class="no-post">你还没有发表过任何文章。</p>
      </div>

      <div v-if="activeTab === 'likes'" class="liked-section">
        <h3>我的喜欢</h3>
        <p v-if="loadingLikes">加载中...</p>
        <p v-else-if="likedArticles.length === 0" class="no-item">你还没有喜欢的文章。</p>
        <div v-else class="post-list">
          <div
            v-for="article in likedArticles"
            :key="article.article_id"
            class="post-card"
            @click="goToPost(article.article_id)"
          >
            <h4 class="post-title">{{ article.title }}</h4>
            <p class="post-excerpt">{{ getExcerpt(article.content) }}</p>
            <div class="author-info">
              <img
                :src="article.author_avatar || defaultAvatar"
                alt="作者头像"
                class="author-avatar-small"
              />
              <span>{{ article.author_nickname }}</span>
              <span class="like-time">点赞于: {{ formatTime(article.like_time) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'collections'" class="collected-section">
        <h3>我的收藏</h3>
        <p v-if="loadingCollections">加载中...</p>
        <p v-else-if="collectedArticles.length === 0" class="no-item">你还没有收藏的文章。</p>
        <div v-else class="post-list">
          <div
            v-for="article in collectedArticles"
            :key="article.article_id"
            class="post-card"
            @click="goToPost(article.article_id)"
          >
            <h4 class="post-title">{{ article.title }}</h4>
            <p class="post-excerpt">{{ getExcerpt(article.content) }}</p>
            <div class="author-info">
              <img
                :src="article.author_avatar || defaultAvatar"
                alt="作者头像"
                class="author-avatar-small"
              />
              <span>{{ article.author_nickname }}</span>
              <span class="like-time">点赞于: {{ formatTime(article.like_time) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'following'" class="follow-section">
        <h3>我关注的人</h3>
        <p v-if="loadingFollowing">加载中...</p>
        <p v-else-if="followingList.length === 0" class="no-follow">你还没有关注任何人。</p>
        <div v-else class="follow-list">
          <div
            v-for="followedUser in followingList"
            :key="followedUser.id"
            class="follow-item"
            @click="goToUserProfile(followedUser.id)"
          >
            <img :src="followedUser.avatar || defaultAvatar" alt="头像" class="follow-avatar" />
            <div class="follow-info">
              <div class="follow-username">{{ followedUser.username }}</div>
              <div class="follow-intro">
                {{ followedUser.intro || '这个人很懒，什么都没有写。' }}
              </div>
            </div>
            <button
              :class="getFollowButtonClass(followedUser)"
              @click.stop="handleFollowButtonClick(followedUser)"
              :disabled="followedUser.statusLoading"
            >
              <span v-if="followedUser.statusLoading">...</span>
              <span v-else>{{ getFollowButtonText(followedUser) }}</span>
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'followers'" class="follow-section">
        <h3>我的粉丝</h3>
        <p v-if="loadingFollowers">加载中...</p>
        <p v-else-if="followersList.length === 0" class="no-follow">你还没有粉丝。</p>
        <div v-else class="follow-list">
          <div
            v-for="followerUser in followersList"
            :key="followerUser.id"
            class="follow-item"
            @click="goToUserProfile(followerUser.id)"
          >
            <img :src="followerUser.avatar || defaultAvatar" alt="头像" class="follow-avatar" />
            <div class="follow-info">
              <div class="follow-username">{{ followerUser.username }}</div>
              <div class="follow-intro">
                {{ followerUser.intro || '这个人很懒，什么都没有写。' }}
              </div>
            </div>
            <button
              :class="getFollowButtonClass(followerUser)"
              @click.stop="handleFollowButtonClick(followerUser)"
              :disabled="followerUser.statusLoading"
            >
              <span v-if="followerUser.statusLoading">...</span>
              <span v-else>{{ getFollowButtonText(followerUser) }}</span>
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'history'" class="Browse-history-section">
        <h3>浏览记录</h3>
        <p v-if="loadingHistory">加载中...</p>
        <p v-else-if="BrowseHistory.length === 0" class="no-item">你还没有浏览记录。</p>
        <div v-else class="post-list">
          <div
            v-for="article in BrowseHistory"
            :key="article.article_id"
            class="post-card"
            @click="goToPost(article.article_id)"
          >
            <h4 class="post-title">{{ article.title }}</h4>
            <p class="post-excerpt">{{ getExcerpt(article.content) }}</p>
            <div class="author-info">
              <img
                :src="article.avatar || defaultAvatar"
                alt="作者头像"
                class="author-avatar-small"
              />
              <span>{{ article.nickname }}</span>
              <span class="history-time">最近浏览于: {{ formatTime(article.browse_time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay">
      <div class="edit-profile-modal">
        <h3>修改个人信息</h3>
        <form @submit.prevent="saveProfile">
          <div class="avatar-container" @click="triggerEditAvatarUpload">
            <div class="avatar-wrapper">
              <img
                :src="(editForm.avatarUrl as string | null) || user.avatar || defaultAvatar"
                alt="头像"
                class="avatar-img"
              />
              <div class="avatar-overlay">
                <svg
                  class="upload-icon"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="white"
                >
                  <path d="M5 20h14v-2H5v2zm7-14l5 5h-3v4h-4v-4H7l5-5z" />
                </svg>
              </div>
              <input
                type="file"
                ref="editAvatarInput"
                @change="handleEditAvatarChange"
                hidden
                accept="image/*"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="edit-username">用户名:</label>
            <input id="edit-username" v-model="editForm.username" placeholder="用户名" />
            <p v-if="editErrors.username" class="error-message">{{ editErrors.username }}</p>
          </div>
          <div class="form-group">
            <label for="edit-intro">个人简介:</label>
            <textarea
              id="edit-intro"
              v-model="editForm.intro"
              placeholder="个人简介"
              rows="3"
            ></textarea>
            <p v-if="editErrors.intro" class="error-message">{{ editErrors.intro }}</p>
          </div>
          <div class="form-group">
            <label for="edit-email">邮箱:</label>
            <input id="edit-email" v-model="editForm.email" type="email" placeholder="邮箱" />
            <p v-if="editErrors.email" class="error-message">{{ editErrors.email }}</p>
          </div>
          <div class="form-group">
            <label for="edit-gender">性别:</label>
            <select id="edit-gender" v-model="editForm.gender">
              <option value="" disabled>请选择性别</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="未知">未知</option>
            </select>
            <p v-if="editErrors.gender" class="error-message">{{ editErrors.gender }}</p>
          </div>
          <div class="form-group">
            <label for="edit-phone">手机号:</label>
            <input id="edit-phone" v-model="editForm.phone" type="tel" placeholder="手机号" />
            <p v-if="editErrors.phone" class="error-message">{{ editErrors.phone }}</p>
          </div>

          <hr class="password-divider" />
          <h4>修改密码 (可选)</h4>

          <div class="form-group">
            <label for="edit-current-password">当前密码:</label>
            <input
              id="edit-current-password"
              v-model="editForm.currentPassword"
              type="password"
              placeholder="输入当前密码"
              autocomplete="current-password"
            />
            <p v-if="editErrors.currentPassword" class="error-message">
              {{ editErrors.currentPassword }}
            </p>
          </div>
          <div class="form-group">
            <label for="edit-new-password">新密码:</label>
            <input
              id="edit-new-password"
              v-model="editForm.newPassword"
              type="password"
              placeholder="输入新密码"
              autocomplete="new-password"
            />
            <p v-if="editErrors.newPassword" class="error-message">{{ editErrors.newPassword }}</p>
          </div>
          <div class="form-group">
            <label for="edit-confirm-password">确认新密码:</label>
            <input
              id="edit-confirm-password"
              v-model="editForm.confirmNewPassword"
              type="password"
              placeholder="再次输入新密码"
              autocomplete="new-password"
            />
            <p v-if="editErrors.confirmNewPassword" class="error-message">
              {{ editErrors.confirmNewPassword }}
            </p>
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="cancelEdit">取消</button>
            <button type="submit" class="save-btn" :disabled="savingProfile">
              <span v-if="savingProfile">保存中...</span>
              <span v-else>保存</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive } from 'vue'
import axios, { AxiosError, isAxiosError } from 'axios'
import { useRouter } from 'vue-router'
import HeaderBar from '@/components/HeaderBar.vue'
const router = useRouter()

// Interface for a user object in the follow lists, including follow status
interface UserWithStatus {
  id: number // Assuming ID is returned by /following and /followers
  username: string
  nickname?: string // Add if your API returns nickname
  avatar: string
  intro?: string
  // Status relative to the currently authenticated user
  is_following?: boolean // Does the current user follow THIS user?
  is_followed_by?: boolean // Is the current user followed by THIS user?
  is_mutual?: boolean // Are they mutually following? (is_following && is_followed_by)
  statusLoading?: boolean // To indicate status fetch or action is in progress
}

// Extended user ref for the PROFILE CARD
const user = ref({
  id: null as number | null, // Add user ID
  avatar: '',
  username: '',
  intro: '',
  email: '',
  register_time: '',
  gender: '', // Add gender
  phone: '', // Add phone
  follower_count: 0,
  following_count: 0,
  like_count: 0,
  collect_count: 0,
})

interface Post {
  id: number
  title: string
  content: string
  tag?: string
}

// Interface for a liked article (based on /alike/user/records)
interface LikedArticle {
  article_id: number
  title: string
  content: string // Backend provides content
  create_time: string // Article create time
  author_nickname: string // Author's nickname
  author_avatar: string // Author's avatar
  like_time: string // Time the user liked the article
}

// Interface for a collected article (based on /user/favorites) - Limited data
interface CollectedArticle {
  article_id: number
  title: string
  content: string // Backend provides content
  create_time: string // Article create time
  author_nickname: string // Author's nickname
  author_avatar: string // Author's avatar
  like_time: string // Time the user liked the article
}

// Define type for Browse History items
interface BrowseHistoryItem {
  article_id: number
  title: string
  content: string
  avatar?: string
  nickname: string
  browse_time: string // Timestamp for when the article was viewed
}

const posts = ref<Post[]>([])
const followingList = ref<UserWithStatus[]>([])
const followersList = ref<UserWithStatus[]>([]) // Corrected declaration

// New refs for liked and collected articles
const likedArticles = ref<LikedArticle[]>([])
const collectedArticles = ref<CollectedArticle[]>([])
const BrowseHistory = ref<BrowseHistoryItem[]>([])

const defaultAvatar = '/default-avatar.png' // Make sure this path is correct

// State for tabs - Added 'likes' and 'collections'
const activeTab = ref<'posts' | 'following' | 'followers' | 'likes' | 'collections' | 'history'>(
  'posts',
)
// Loading states for lists
const loadingFollowing = ref(false)
const loadingFollowers = ref(false)
const loadingLikes = ref(false) // New loading state
const loadingCollections = ref(false) // New loading state
const loadingHistory = ref(false)

// --- Edit Profile Modal State and Data ---
const showEditModal = ref(false)
const editForm = reactive({
  username: '',
  intro: '',
  email: '',
  gender: '',
  phone: '', // Add phone to edit form
  currentPassword: '', // Add current password field
  newPassword: '', // Add new password field
  confirmNewPassword: '', // Add confirm new password field
  avatarFile: null as File | null, // To hold the selected avatar file
  // Corrected type for avatarUrl preview
  avatarUrl: '' as string | null, // To display the selected avatar preview (Data URL or null)
})
const editAvatarInput = ref<HTMLInputElement | null>(null) // Ref for the file input
const savingProfile = ref(false) // Saving state

// Validation errors for edit form
const editErrors = reactive({
  username: '',
  intro: '',
  email: '',
  gender: '',
  phone: '',
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: '',
})

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    console.error('No token found, user is not authenticated.')
    // Decide how to handle unauthenticated users, e.g., redirect to login
    router.push('/login') // Redirect to login
    return
  }

  // Fetch Profile and initial data (posts)
  await fetchProfileAndInitialData(token)

  // If the URL has a query param indicating a tab, switch to it
  const tabFromQuery = router.currentRoute.value.query.tab as typeof activeTab.value
  if (
    tabFromQuery &&
    ['posts', 'following', 'followers', 'likes', 'collections'].includes(tabFromQuery)
  ) {
    activeTab.value = tabFromQuery
    // Trigger fetch for the list if it's a list tab
    // Check if the list is already loaded to avoid unnecessary fetches on mount if navigating back
    if (tabFromQuery === 'following' && followingList.value.length === 0 && !loadingFollowing.value)
      fetchFollowing()
    if (tabFromQuery === 'followers' && followersList.value.length === 0 && !loadingFollowers.value)
      fetchFollowers()
    if (tabFromQuery === 'likes' && likedArticles.value.length === 0 && !loadingLikes.value)
      fetchLikedArticles() // Fetch likes if tab is set
    if (
      tabFromQuery === 'collections' &&
      collectedArticles.value.length === 0 &&
      !loadingCollections.value
    )
      fetchCollectedArticles() // Fetch collections if tab is set
    if (tabFromQuery === 'history' && BrowseHistory.value.length === 0 && !loadingHistory.value)
      fetchBrowseHistory() // Fetch collections if tab is set
  }
})

// Watch for tab changes to fetch data
watch(activeTab, (newTab, oldTab) => {
  // Only fetch if the list is empty and not already loading
  if (newTab === 'following' && followingList.value.length === 0 && !loadingFollowing.value) {
    fetchFollowing()
  } else if (
    newTab === 'followers' &&
    followersList.value.length === 0 &&
    !loadingFollowers.value
  ) {
    fetchFollowers()
  } else if (newTab === 'likes' && likedArticles.value.length === 0 && !loadingLikes.value) {
    fetchLikedArticles() // Fetch likes when 'likes' tab becomes active
  } else if (
    newTab === 'collections' &&
    collectedArticles.value.length === 0 &&
    !loadingCollections.value
  ) {
    fetchCollectedArticles() // Fetch collections when 'collections' tab becomes active
  } else if (newTab === 'history' && BrowseHistory.value.length === 0 && !loadingHistory.value) {
    fetchBrowseHistory() // Fetch collections when 'collections' tab becomes active
  }
})

// Function to open the edit modal and initialize the form
function openEditModal() {
  resetEditForm() // Initialize form with current user data and clear errors
  showEditModal.value = true
}

// Function to fetch profile and initial data (like posts)
async function fetchProfileAndInitialData(token: string) {
  try {
    // 1. Fetch User Profile - Assuming 'id', 'gender', 'phone' are now returned
    const profileRes = await axios.get('http://127.0.0.1:5000/user/getProfile', {
      headers: { Authorization: `Bearer ${token}` },
    })

    let currentUserId: number | null = null

    if (profileRes.data.state === 1 && profileRes.data.data) {
      user.value = { ...user.value, ...profileRes.data.data }
      currentUserId = profileRes.data.data.id // Capture the user ID returned by the API

      // Initialize edit form with fetched data (done when opening modal)
      // Moved initialization to openEditModal
      // editForm.username = user.value.username;
      // ...
      // editForm.avatarUrl = user.value.avatar;
    } else {
      console.error('Failed to fetch profile:', profileRes.data.message)
      if (profileRes.data.code === 401) {
        // Check for specific unauthorized code if backend provides it
        alert('认证失败，请重新登录。')
        router.push('/login')
      } else {
        alert(`加载个人信息失败: ${profileRes.data.message || '未知错误'}`)
      }
      return // Stop if profile fetch fails, as we need user ID
    }

    // 2. Fetch Follow Counts (if user ID was successfully obtained)
    // This is done immediately on load to display counts on the profile card
    if (currentUserId !== null) {
      try {
        const followStatsRes = await axios.get(
          `http://127.0.0.1:5000/follow-count/${currentUserId}`,
          {
            headers: { Authorization: `Bearer ${token}` }, // Assuming follow-count might need auth now
          },
        )
        if (followStatsRes.data && typeof followStatsRes.data.following_count !== 'undefined') {
          user.value.following_count = followStatsRes.data.following_count
          user.value.follower_count = followStatsRes.data.follower_count
        } else {
          console.error(
            'Failed to fetch follow stats or data in unexpected format:',
            followStatsRes.data,
          )
          user.value.following_count = 0
          user.value.follower_count = 0
        }
      } catch (followError) {
        console.error('Error fetching follow stats:', followError)
        // Display default counts or show error message
        user.value.following_count = 0
        user.value.follower_count = 0
        // Optionally alert user if follow stats loading failed
        // alert(`加载关注/粉丝数失败: ${String(followError)}`);
      }
      //喜欢
      const likeStatsRes = await axios.get(`http://127.0.0.1:5000/user/like_count`, {
        headers: { Authorization: `Bearer ${token}` }, // Assuming follow-count might need auth now
      })
      if (likeStatsRes.data && typeof likeStatsRes.data.like_count !== 'undefined') {
        user.value.like_count = likeStatsRes.data.like_count
      } else {
        console.error(
          'Failed to fetch follow stats or data in unexpected format:',
          likeStatsRes.data,
        )
        user.value.like_count = 0
      }
      //收藏
      const collectStatsRes = await axios.get(`http://127.0.0.1:5000/user/collect_count`, {
        headers: { Authorization: `Bearer ${token}` }, // Assuming follow-count might need auth now
      })
      if (collectStatsRes.data && typeof collectStatsRes.data.collect_count !== 'undefined') {
        user.value.collect_count = collectStatsRes.data.collect_count
      } else {
        console.error(
          'Failed to fetch follow stats or data in unexpected format:',
          collectStatsRes.data,
        )
        user.value.collect_count = 0
      }
    } else {
      console.warn('User ID not available from profile fetch, skipping initial follow stats.')
    }

    // 3. Fetch User's Articles (initial tab content)
    // Assuming article/list is now for the authenticated user if no user ID is provided
    const postRes = await axios.get('http://127.0.0.1:5000/article/list', {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (postRes.data && Array.isArray(postRes.data.data)) {
      posts.value = postRes.data.data
    } else if (Array.isArray(postRes.data)) {
      posts.value = postRes.data // Fallback if data structure is inconsistent
    } else {
      console.error('Fetched posts data is not in expected format:', postRes.data)
      posts.value = []
    }
  } catch (error) {
    console.error('Error fetching initial data:', error)
    if (isAxiosError(error) && error.response?.status === 401) {
      alert('认证失败，请重新登录。')
      router.push('/login') // Redirect to login on auth failure
    } else {
      alert(`加载个人信息失败: ${String(error)}`)
    }
  }
}

// --- Edit Profile Modal Logic ---

// Trigger click on the hidden file input
function triggerEditAvatarUpload() {
  editAvatarInput.value?.click()
}

// Handle file selection for avatar
function handleEditAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]

    // Optional: Validate file type/size before setting
    if (!file.type.startsWith('image/')) {
      alert('请选择一个图片文件。')
      if (editAvatarInput.value) editAvatarInput.value.value = '' // Clear file input
      editForm.avatarFile = null
      editForm.avatarUrl = user.value.avatar // Reset preview
      return
    }
    if (file.size > 2 * 1024 * 1024) {
      // Example: 2MB limit
      alert('文件大小不能超过 2MB。')
      if (editAvatarInput.value) editAvatarInput.value.value = '' // Clear file input
      editForm.avatarFile = null
      editForm.avatarUrl = user.value.avatar // Reset preview
      return
    }

    editForm.avatarFile = file

    // Create a preview URL
    const reader = new FileReader()
    reader.onload = (e) => {
      // FileReader.result is string | ArrayBuffer | null depending on method, but readAsDataURL is string | null
      // We expect a string (the data URL) or null. Explicitly cast to string | null.
      editForm.avatarUrl = (e.target?.result as string | null) || null
    }
    reader.readAsDataURL(file)
  }
}

// Client-side validation for edit form
function validateEditForm(): boolean {
  let isValid = true
  // Reset previous errors
  Object.keys(editErrors).forEach((key) => (editErrors[key as keyof typeof editErrors] = ''))

  // Validate Username
  if (!editForm.username.trim()) {
    editErrors.username = '用户名不能为空。'
    isValid = false
  }

  // Validate Email (optional format check)
  if (!editForm.email.trim()) {
    editErrors.email = '邮箱不能为空。'
    isValid = false
  } else {
    // Simple email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(editForm.email.trim())) {
      editErrors.email = '请输入有效的邮箱格式。'
      isValid = false
    }
  }

  // Validate Phone (optional format check)
  if (editForm.phone.trim()) {
    // Phone is optional, validate only if entered
    // Simple phone format check (adjust regex based on expected format)
    const phoneRegex = /^\d{10,15}$/ // Example: 10-15 digits
    if (!phoneRegex.test(editForm.phone.trim())) {
      editErrors.phone = '请输入有效的手机号格式（例如：13812345678）。'
      isValid = false
    }
  }

  // Validate Password Fields ONLY if a new password is being set
  if (editForm.newPassword || editForm.confirmNewPassword) {
    if (!editForm.currentPassword) {
      editErrors.currentPassword = '修改密码需要输入当前密码。'
      isValid = false
    }
    if (!editForm.newPassword) {
      editErrors.newPassword = '请输入新密码。'
      isValid = false
    } else if (editForm.newPassword.length < 6) {
      // Example: minimum 6 characters
      editErrors.newPassword = '新密码至少需要6个字符。'
      isValid = false
    }
    if (!editForm.confirmNewPassword) {
      editErrors.confirmNewPassword = '请再次输入新密码。'
      isValid = false
    }
    if (
      editForm.newPassword &&
      editForm.confirmNewPassword &&
      editForm.newPassword !== editForm.confirmNewPassword
    ) {
      editErrors.confirmNewPassword = '两次输入的密码不一致。'
      isValid = false
    }
  }

  // No specific validation for bio or gender needed based on current requirements

  return isValid
}

// Save profile changes
async function saveProfile() {
  const token = localStorage.getItem('token')
  if (!token || savingProfile.value) return

  // Perform client-side validation
  if (!validateEditForm()) {
    console.log('Client-side validation failed.')
    return // Stop if validation fails
  }

  savingProfile.value = true

  const formData = new FormData()
  // Append fields
  formData.append('username', editForm.username.trim())
  formData.append('intro', editForm.intro || '')
  formData.append('email', editForm.email.trim())
  formData.append('gender', editForm.gender || '')
  formData.append('phone', editForm.phone.trim() || '') // Send phone, empty string if not entered

  // Append password fields ONLY if a new password is being set
  if (editForm.newPassword) {
    formData.append('current_password', editForm.currentPassword)
    formData.append('new_password', editForm.newPassword)
    // No need to send confirmNewPassword to backend, validation done on client side
  }
  // Append avatar file if selected
  if (editForm.avatarFile) {
    formData.append('avatar', editForm.avatarFile)
    console.log('Appending avatar file to FormData.') // Debug
  } else {
    console.log('No new avatar file selected.') // Debug
  }

  try {
    // Assuming your backend has an endpoint like /user/updateProfile that handles all updates
    const res = await axios.put('http://127.0.0.1:5000/user/updateProfile', formData, {
      headers: {
        // 'Content-Type': 'multipart/form-data', // Axios sets this automatically with FormData
        Authorization: `Bearer ${token}`,
      },
    })

    if (res.data.state === 1) {
      alert('个人信息更新成功！')
      // Update local user data with the response data
      // The backend should ideally return the updated user object including the new avatar URL, phone, etc.
      user.value = { ...user.value, ...res.data.data } // Assuming response.data.data contains the updated user object
      showEditModal.value = false // Close modal on success
      // Reset edit form state
      resetEditForm() // Reset form with the newly saved data
    } else {
      // Handle specific backend errors (e.g., wrong current password)
      if (res.data.code === 400 && res.data.message === 'Incorrect current password') {
        // Example backend error message
        editErrors.currentPassword = '当前密码不正确。'
        alert('当前密码不正确。')
      } else {
        alert(`更新失败: ${res.data.message || '未知错误'}`)
      }
      console.error('Backend update failed:', res.data.message)
    }
  } catch (error) {
    console.error('Error saving profile:', error)
    if (isAxiosError(error)) {
      // Handle network errors or other API errors (like 401 Unauthorized)
      if (error.response?.status === 401) {
        alert('认证失败，请重新登录。')
        router.push('/login')
      } else if (error.response?.data?.message) {
        // Display backend validation errors or other messages
        alert(`保存失败: ${error.response.data.message}`)
      } else {
        alert(`保存失败: ${error.message}`)
      }
    } else {
      alert(`保存失败: ${String(error)}`)
    }
  } finally {
    savingProfile.value = false
  }
}

// Cancel edit and close modal
function cancelEdit() {
  showEditModal.value = false
  resetEditForm() // Reset form state to currently displayed user data when cancelling
}

// Reset the edit form to current user data and clear errors
function resetEditForm() {
  editForm.username = user.value.username
  editForm.intro = user.value.intro || ''
  editForm.email = user.value.email
  editForm.gender = user.value.gender || ''
  editForm.phone = user.value.phone || '' // Initialize phone
  editForm.currentPassword = '' // Clear password fields
  editForm.newPassword = ''
  editForm.confirmNewPassword = ''
  editForm.avatarFile = null
  editForm.avatarUrl = user.value.avatar // Reset avatar preview to current avatar URL
  // Clear file input value so selecting the same file again triggers change event
  if (editAvatarInput.value) {
    editAvatarInput.value.value = ''
  }
  // Clear all validation errors
  Object.keys(editErrors).forEach((key) => (editErrors[key as keyof typeof editErrors] = ''))
}

// --- Follow/Follower List Specific Logic ---

// Fetch list of users the current user is following
async function fetchFollowing() {
  const token = localStorage.getItem('token')
  if (!token || !user.value.id || loadingFollowing.value) return

  loadingFollowing.value = true
  followingList.value = [] // Clear previous list
  try {
    // Assuming your backend has an endpoint like /following for the authenticated user
    const res = await axios.get('http://127.0.0.1:5000/following', {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (Array.isArray(res.data)) {
      // Fetch follow status for each user in the list
      const followingUsersWithStatus: UserWithStatus[] = []
      // Use Promise.all for parallel fetching of follow statuses if API can handle it
      // Or sequential fetch if needed
      for (const followedUser of res.data) {
        // Assuming followedUser object has 'id' and is a UserWithStatus partial
        if (followedUser.id) {
          const status = await fetchFollowStatus(followedUser.id)
          followingUsersWithStatus.push({ ...followedUser, ...status, statusLoading: false })
        } else {
          console.warn('Followed user object is missing ID:', followedUser)
          // Push with minimal info if ID is missing
          followingUsersWithStatus.push({
            id: followedUser.id || -1,
            username: followedUser.username || 'Unknown',
            avatar: followedUser.avatar || defaultAvatar,
            intro: followedUser.intro || 'No intro',
            statusLoading: false,
          })
        }
      }
      followingList.value = followingUsersWithStatus
    } else {
      // Handle cases where the response is not an array, maybe an empty list represented differently
      console.warn('Fetched following data is not an array or empty:', res.data)
      // Depending on API, res.data might be { message: "No following" } or similar
      // If it's not an array of users, treat it as an empty list
      if (!res.data || typeof res.data !== 'object' || Object.keys(res.data).length === 0) {
        followingList.value = []
      } else {
        console.error('Fetched following data is in unexpected format:', res.data)
        followingList.value = []
      }
    }
  } catch (error) {
    console.error('Error fetching following list:', error)
    followingList.value = []
    if (isAxiosError(error) && error.response?.status === 401) {
      alert('获取关注列表失败，请重新登录。')
      router.push('/login')
    } else {
      alert(`获取关注列表失败: ${String(error)}`)
    }
  } finally {
    loadingFollowing.value = false
  }
}

// Fetch list of users who follow the current user
async function fetchFollowers() {
  const token = localStorage.getItem('token')
  if (!token || !user.value.id || loadingFollowers.value) return

  loadingFollowers.value = true
  followersList.value = [] // Clear previous list
  try {
    // Assuming your backend has an endpoint like /followers for the authenticated user
    const res = await axios.get('http://127.0.0.1:5000/followers', {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (Array.isArray(res.data)) {
      // Fetch follow status for each user in the list
      const followerUsersWithStatus: UserWithStatus[] = []
      // Use Promise.all for parallel fetching of follow statuses if API can handle it
      // Or sequential fetch if needed
      for (const followerUser of res.data) {
        // Assuming followerUser object has 'id' and is a UserWithStatus partial
        if (followerUser.id) {
          const status = await fetchFollowStatus(followerUser.id)
          followerUsersWithStatus.push({ ...followerUser, ...status, statusLoading: false })
        } else {
          console.warn('Follower user object is missing ID:', followerUser)
          // Push with minimal info if ID is missing
          followerUsersWithStatus.push({
            id: followerUser.id || -1,
            username: followerUser.username || 'Unknown',
            avatar: followerUser.avatar || defaultAvatar,
            intro: followerUser.intro || 'No intro',
            statusLoading: false,
          })
        }
      }
      followersList.value = followerUsersWithStatus
    } else {
      // Handle cases where the response is not an array, maybe an empty list represented differently
      console.warn('Fetched followers data is not an array or empty:', res.data)
      if (!res.data || typeof res.data !== 'object' || Object.keys(res.data).length === 0) {
        followersList.value = []
      } else {
        console.error('Fetched followers data is in unexpected format:', res.data)
        followersList.value = []
      }
    }
  } catch (error) {
    console.error('Error fetching followers list:', error)
    followersList.value = []
    if (isAxiosError(error) && error.response?.status === 401) {
      alert('获取粉丝列表失败，请重新登录。')
      router.push('/login')
    } else {
      alert(`获取粉丝列表失败: ${String(error)}`)
    }
  } finally {
    loadingFollowers.value = false
  }
}

// Fetch follow status between current user and target user
// This is crucial for displaying the correct button text ('已关注', '去回关', etc.)
async function fetchFollowStatus(
  targetUserId: number,
): Promise<{ is_following?: boolean; is_followed_by?: boolean; is_mutual?: boolean }> {
  const token = localStorage.getItem('token')
  // Need current user ID and target ID. If current user ID is null, we can't determine status.
  if (!token || user.value.id === null || !targetUserId) return {}

  try {
    // Assuming your backend has an endpoint like /friends/{targetUserId} that returns the relationship status
    // This endpoint should return status relative to the AUTHENTICATED user (user.value.id) and targetUserId
    const res = await axios.get(`http://127.0.0.1:5000/friends/${targetUserId}`, {
      headers: { Authorization: `Bearer ${token}` }, // This endpoint should definitely require auth
    })
    // Returns { "is_following": bool, "is_followed_by": bool, "is_mutual": bool } based on authenticated user and targetUserId
    if (res.data && typeof res.data.is_following !== 'undefined') {
      return res.data
    } else {
      console.warn(
        `Follow status for user ${targetUserId} data is not in expected format:`,
        res.data,
      )
      return {} // Return empty status if format is wrong
    }
  } catch (error) {
    console.error(`Error fetching follow status for user ${targetUserId}:`, error)
    // Handle specific errors like 404 if user not found or 401 if not authenticated
    if (isAxiosError(error)) {
      if (error.response?.status === 404) {
        console.warn(`User ${targetUserId} not found when fetching follow status.`)
      } else if (error.response?.status === 401) {
        console.warn('Authentication required to fetch follow status.')
      } else {
        console.error(
          `API error fetching follow status for ${targetUserId}:`,
          error.response?.data?.message || error.message,
        )
      }
    } else {
      console.error(`Non-Axios error fetching follow status for ${targetUserId}:`, error)
    }
    return {} // Return empty status on any error
  }
}

// --- New Functions for Liked and Collected Articles ---

// Fetch list of articles the current user has liked
async function fetchLikedArticles() {
  const token = localStorage.getItem('token')
  // No user.value.id needed in the URL for /alike/user/records based on provided endpoint
  if (!token || loadingLikes.value) return

  loadingLikes.value = true
  likedArticles.value = [] // Clear previous list
  try {
    // Assuming your backend has an endpoint like /alike/user/records for the authenticated user
    const res = await axios.get('http://127.0.0.1:5000/alike/user/records', {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (res.data.state === 1 && Array.isArray(res.data.data)) {
      // Backend provides article_id, title, content, author_nickname, author_avatar, like_time
      likedArticles.value = res.data.data
      console.log('Fetched liked articles:', likedArticles.value)
    } else if (res.data.state === 1 && !res.data.data) {
      // Backend might return state 1 with empty data if no likes
      likedArticles.value = []
      console.log('Fetched liked articles: No data (empty).')
    } else {
      console.error('Fetched liked articles data is not in expected format:', res.data)
      likedArticles.value = []
    }
  } catch (error) {
    console.error('Error fetching liked articles:', error)
    likedArticles.value = []
    if (isAxiosError(error) && error.response?.status === 401) {
      alert('获取喜欢的文章失败，请重新登录。')
      router.push('/login')
    } else {
      alert(`获取喜欢的文章失败: ${String(error)}`)
    }
  } finally {
    loadingLikes.value = false
  }
}

// Fetch list of articles the current user has collected
async function fetchCollectedArticles() {
  const token = localStorage.getItem('token')
  // Endpoint requires user ID in the URL
  if (!token || loadingCollections.value) return

  loadingCollections.value = true
  collectedArticles.value = [] // Clear previous list
  try {
    // Assuming your backend has an endpoint like /user/favorites/{userId}
    const res = await axios.get(`http://127.0.0.1:5000//favorite/user/records`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    if (res.data.state === 1 && Array.isArray(res.data.data)) {
      // Backend provides article_id, title, content, author_nickname, author_avatar, like_time
      collectedArticles.value = res.data.data
      console.log('Fetched liked articles:', collectedArticles.value)
    } else if (res.data.state === 1 && !res.data.data) {
      // Backend might return state 1 with empty data if no likes
      collectedArticles.value = []
      console.log('Fetched liked articles: No data (empty).')
    } else {
      console.error('Fetched liked articles data is not in expected format:', res.data)
      collectedArticles.value = []
    }
  } catch (error) {
    console.error('Error fetching collected articles:', error)
    collectedArticles.value = []
    if (isAxiosError(error) && error.response?.status === 401) {
      alert('获取收藏的文章失败，请重新登录。')
      router.push('/login')
    } else {
      alert(`获取收藏的文章失败: ${String(error)}`)
    }
  } finally {
    loadingCollections.value = false
  }
}

// --- New Fetch Function for Browse History ---
const fetchBrowseHistory = async () => {
  const token = localStorage.getItem('token')
  if (!token || loadingHistory.value) return
  loadingHistory.value = true
  BrowseHistory.value = [] // Clear previous history
  try {
    const res = await axios.get(`http://127.0.0.1:5000//article/browses`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.data.state === 1 && Array.isArray(res.data.browses)) {
      // Backend provides article_id, title, content, author_nickname, author_avatar, like_time
      BrowseHistory.value = res.data.browses
      console.log('Fetched liked articles:', BrowseHistory.value)
    } else if (res.data.state === 1 && !res.data.browses) {
      // Backend might return state 1 with empty data if no likes
      BrowseHistory.value = []
      console.log('Fetched Browse history: No data (empty).')
    } else {
      console.error('Fetched Browse history data is not in expected format:', res.data)
      BrowseHistory.value = []
    }
  } catch (error) {
    console.error('Error fetching Browse history:', error)
    BrowseHistory.value = []
    if (isAxiosError(error) && error.response?.status === 401) {
      alert('获取浏览历史失败，请重新登录。')
      router.push('/login')
    } else {
      alert(`获取浏览历史失败: ${String(error)}`)
    }
  } finally {
    loadingHistory.value = false
  }
}

// Handle button click action based on current status
async function handleFollowButtonClick(targetUser: UserWithStatus) {
  // Prevent action on self's profile
  if (user.value.id !== null && user.value.id === targetUser.id) {
    console.log('Cannot follow/unfollow self.')
    return
  }

  if (!targetUser.id || targetUser.statusLoading) return

  // Find the user in the respective list to update its state
  const targetUserInList =
    followingList.value.find((u) => u.id === targetUser.id) ||
    followersList.value.find((u) => u.id === targetUser.id)
  if (!targetUserInList) {
    console.error('Clicked user not found in current list.')
    return // Should not happen if called from a list item
  }

  // Set loading state immediately for the clicked item
  targetUserInList.statusLoading = true

  const currentStatusText = getFollowButtonText(targetUserInList)

  if (currentStatusText === '已关注' || currentStatusText === '已互关') {
    // Unfollow action
    await unfollowUser(targetUserInList)
  } else if (currentStatusText === '去回关' || currentStatusText === '关注') {
    // Follow or Follow back action
    await followUser(targetUserInList)
  } else {
    // Should not reach here for expected states
    targetUserInList.statusLoading = false // Reset loading if no action taken
  }
  // Loading state is reset within followUser/unfollowUser finally block
}

// Perform follow action
async function followUser(targetUser: UserWithStatus) {
  const token = localStorage.getItem('token')
  if (!token || !targetUser.id) {
    console.error('Cannot follow: Missing token or target user ID.')
    if (targetUser.statusLoading) targetUser.statusLoading = false
    return
  }
  try {
    // Assuming endpoint is /follow/{targetUserId} and expects POST
    const res = await axios.post(
      `http://127.0.0.1:5000/follow/${targetUser.id}`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    )
    // Assuming success state is 1
    console.log(`Followed user ${targetUser.username}`)

    // Refetch status for the affected user to update button text/class
    const updatedStatus = await fetchFollowStatus(targetUser.id)
    Object.assign(targetUser, updatedStatus) // Update the user object in the list

    // Update main user's following count (optimistically or by refetching)
    if (user.value.id !== null) {
      // Ensure current user ID is available
      const followStatsRes = await axios.get(
        `http://127.0.0.1:5000/follow-count/${user.value.id}`,
        {
          headers: { Authorization: `Bearer ${token}` }, // Assuming follow-count might need auth now
        },
      )
      if (followStatsRes.data) {
        user.value.following_count = followStatsRes.data.following_count
        user.value.follower_count = followStatsRes.data.follower_count
      }
      alert(`关注成功！`)
    }
  } catch (error) {
    console.error(`Error following user ${targetUser.username}:`, error)
    if (isAxiosError(error)) {
      alert(`关注失败: ${error.response?.data?.message || error.message}`)
    } else {
      alert(`关注失败: ${String(error)}`)
    }
  } finally {
    // Ensure loading state is reset even on error
    if (targetUser.statusLoading) targetUser.statusLoading = false
  }
}

// Perform unfollow action
async function unfollowUser(targetUser: UserWithStatus) {
  const token = localStorage.getItem('token')
  if (!token || !targetUser.id) {
    console.error('Cannot unfollow: Missing token or target user ID.')
    if (targetUser.statusLoading) targetUser.statusLoading = false
    return
  }
  try {
    // Assuming endpoint is /unfollow/{targetUserId} and expects DELETE
    const res = await axios.delete(`http://127.0.0.1:5000/unfollow/${targetUser.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })

    // Assuming success state is 1
    console.log(`Unfollowed user ${targetUser.username}`)

    // Refetch status for the affected user to update button text/class
    const updatedStatus = await fetchFollowStatus(targetUser.id)
    Object.assign(targetUser, updatedStatus) // Update the user object in the list

    // Update main user's following count (optimistically or by refetching)
    if (user.value.id !== null) {
      // Ensure current user ID is available
      const followStatsRes = await axios.get(
        `http://127.0.0.1:5000/follow-count/${user.value.id}`,
        {
          headers: { Authorization: `Bearer ${token}` }, // Assuming follow-count might need auth now
        },
      )
      if (followStatsRes.data) {
        user.value.following_count = followStatsRes.data.following_count
        user.value.follower_count = followStatsRes.data.follower_count
      }
    }
    alert(`取消关注成功！`)
  } catch (error) {
    console.error(`Error unfollowing user ${targetUser.username}:`, error)
    if (isAxiosError(error)) {
      alert(`取消关注失败: ${error.response?.data?.message || error.message}`)
    } else {
      alert(`取消关注失败: ${String(error)}`)
    }
  } finally {
    // Ensure loading state is reset even on error
    if (targetUser.statusLoading) targetUser.statusLoading = false
  }
}

// Determine button text based on user's follow status relative to the current user
function getFollowButtonText(targetUser: UserWithStatus): string {
  // Check for null/undefined status properties defensively
  const isFollowing = targetUser.is_following === true
  const isFollowedBy = targetUser.is_followed_by === true
  // Calculate isMutual defensively
  const isMutual = isFollowing && isFollowedBy // Use calculation if is_mutual might not be reliable

  if (isMutual) {
    return '已互关'
  } else if (isFollowing) {
    return '已关注'
  } else if (isFollowedBy) {
    return '去回关'
  } else {
    return '关注' // Default state for users you don't follow and who don't follow you
  }
}

// Determine button class for styling based on state
function getFollowButtonClass(targetUser: UserWithStatus): string[] {
  const classes = ['follow-button']
  const statusText = getFollowButtonText(targetUser)

  if (statusText === '已关注' || statusText === '已互关') {
    classes.push('followed') // Grey style
  } else if (statusText === '去回关') {
    classes.push('follow-back') // Blue style
  } else {
    classes.push('not-following') // Default style (maybe green or primary color)
  }

  if (targetUser.statusLoading) {
    classes.push('loading')
  }

  return classes
}

function goToUserProfile(id: number) {
  // Optional: Check if clicking on self
  if (user.value.id !== null && user.value.id === id) {
    console.log('Clicked on own profile in list.')
    // We are already on the user's profile page, no need to navigate
    // Maybe scroll to the top or refresh relevant sections if needed
    return
  }
  if (!id) {
    console.error('Cannot navigate: Missing user ID.')
    return
  }
  // Navigate to the new component with the user ID parameter
  // Make sure you have a route defined like: { name: 'OtherUserProfile', path: '/profile/:userId' }
  router.push({ name: 'OtherUserProfile', params: { userId: id } })
}

// --- Existing Helper Functions ---

function goToPost(id: number) {
  // Consider adding the current tab to the route query when navigating away?
  // router.push({ path: `/post/${id}`, query: { tab: activeTab.value } });
  router.push(`/post/${id}`)
}

function searchByTag(tag: string) {
  if (!tag) return
  // Navigate to home and set the search query
  router.push({ path: '/', query: { search: tag } })
}

function getExcerpt(content: string): string {
  if (!content) return ''
  // Remove HTML tags
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = content
  const text = tempDiv.textContent || tempDiv.innerText || ''
  // Trim and truncate
  const trimmedText = text.trim()
  return trimmedText.length > 100 ? trimmedText.slice(0, 100) + '...' : trimmedText
}

// Helper to format time strings
function formatTime(timeString: string): string {
  if (!timeString) return ''
  try {
    // Assuming backend provides ISO format or similar recognized by Date
    const date = new Date(timeString)
    // Format as YYYY-MM-DD HH:mm
    const year = date.getFullYear()
    const month = ('0' + (date.getMonth() + 1)).slice(-2) // Months are 0-indexed
    const day = ('0' + date.getDate()).slice(-2)
    const hours = ('0' + date.getHours()).slice(-2)
    const minutes = ('0' + date.getMinutes()).slice(-2)
    return `${year}-${month}-${day} ${hours}:${minutes}`
  } catch (e) {
    console.error('Error formatting time:', timeString, e)
    return timeString // Return original string if formatting fails
  }
}
</script>

<style scoped>
/* --- Existing Styles --- */
.logo-wrapper {
  position: absolute;
  top: 20px;
  left: 30px;
  display: flex;
  align-items: center;
  gap: 12px; /* 文字和按钮间距 */
  z-index: 1000;
}

.logo-absolute {
  font-family: 'Great Vibes', cursive;
  font-size: 42px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
  user-select: none;
}

.home-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.home-btn:hover {
  transform: scale(1.1);
}

.home-btn svg {
  display: block;
  stroke: #0077cc;
  width: 24px;
  height: 24px;
}

.profile-container {
  max-width: 900px;
  margin: 100px auto 0 auto; /* Adjusted top margin, removed bottom margin */
  padding: 20px;
  font-family: 'Helvetica Neue', sans-serif;
  position: relative; /* Needed for edit button positioning */
}

.profile-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  text-align: center;
  position: relative; /* Needed for edit button positioning */
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  object-fit: cover;
  margin-bottom: 20px;
  border: 3px solid #eee;
}

.nickname {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.bio {
  color: #666;
  margin-bottom: 20px;
  font-size: 16px;
  line-height: 1.5;
}

.user-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px 20px;
  font-size: 14px;
  color: #444;
  margin-bottom: 20px; /* Add margin below meta info */
}

.user-meta span {
  margin: 5px;
  background-color: #f0f0f0;
  padding: 5px 10px;
  border-radius: 4px;
}

.clickable-meta {
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.clickable-meta:hover {
  background-color: #e0e0e0;
}

/* --- Edit Profile Button Style --- */
.edit-profile-btn {
  background-color: #0077cc;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-top: 15px; /* Space above the button */
}

.edit-profile-btn:hover {
  background-color: #005bb5;
}

/* --- New Styles for Tabs and Lists --- */
.profile-tabs {
  max-width: 900px;
  margin: 20px auto 0 auto; /* Below profile card, above content */
  display: flex;
  justify-content: center;
  gap: 10px;
  border-bottom: 2px solid #eee;
  padding: 0 20px; /* Match profile card padding */
  overflow-x: auto; /* Allow scrolling on small screens */
  -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
}

.tab-item {
  padding: 10px 15px;
  cursor: pointer;
  font-size: 16px;
  color: #555;
  border-bottom: 3px solid transparent;
  transition:
    color 0.2s ease,
    border-bottom-color 0.2s ease;
  white-space: nowrap; /* Prevent wrapping */
}

.tab-item:hover {
  color: #0077cc;
}

.tab-item.active {
  color: #0077cc;
  border-bottom-color: #0077cc;
  font-weight: bold;
}

.tab-content {
  max-width: 900px;
  margin: 20px auto 40px auto;
  padding: 0 20px; /* Match profile card padding */
}

.post-section,
.follow-section,
.placeholder-section,
.liked-section,
.collected-section,
.Browse-history-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  padding: 20px;
}

.post-section h3,
.follow-section h3,
.placeholder-section h3,
.liked-section h3,
.collected-section h3,
.Browse-history-section h3 {
  text-align: center;
  margin-top: 0;
  margin-bottom: 25px;
  color: #333;
  font-size: 22px;
  font-weight: 600;
}

.post-list {
  display: grid;
  gap: 20px;
}

.post-card {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition:
    transform 0.2s ease-in-out,
    box-shadow 0.2s ease-in-out;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.post-title {
  font-size: 18px;
  font-weight: bold;
  color: #0077cc;
  margin-top: 0;
  margin-bottom: 10px;
}

.post-excerpt {
  font-size: 15px;
  color: #555;
  line-height: 1.6;
  margin-bottom: 10px;
  /* Allow multiline for excerpt */
  white-space: normal;
  overflow: hidden;
  text-overflow: ellipsis;
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
  background-color: #b2ebf2;
}

/* Style for author info in liked articles */
.author-info {
  display: flex;
  align-items: center;
  margin-top: 10px;
  font-size: 14px;
  color: #777;
}

.author-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 12px;
  object-fit: cover;
  margin-right: 8px;
}

.like-time {
  margin-left: auto; /* Push time to the right */
  font-size: 13px;
  color: #999;
}

.history-time {
  margin-left: auto; /* Push time to the right */
  font-size: 13px;
  color: #999;
}

.no-post,
.no-follow,
.no-item,
.placeholder-section p {
  text-align: center;
  color: #777;
  font-size: 16px;
  padding: 30px 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.no-item {
  /* Style for empty liked/collected lists */
}

.follow-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.follow-item {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  gap: 15px; /* Spacing between avatar, info, button */
  cursor: pointer; /* Indicate clickable item */
  transition: background-color 0.2s ease;
}
.follow-item:hover {
  background-color: #f0f0f0;
}

.follow-avatar {
  width: 50px;
  height: 50px;
  border-radius: 25px;
  object-fit: cover;
  flex-shrink: 0; /* Prevent avatar from shrinking */
}

.follow-info {
  flex-grow: 1; /* Allow info to take available space */
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0; /* Allow text ellipsis */
}

.follow-username {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.follow-intro {
  font-size: 13px;
  color: #777;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.follow-button {
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition:
    background-color 0.2s ease,
    opacity 0.2s ease,
    color 0.2s ease,
    border-color 0.2s ease;
  flex-shrink: 0; /* Prevent button from shrinking */
  min-width: 80px; /* Give buttons a consistent minimum width */
  text-align: center;
  border: 1px solid transparent; /* Default transparent border */
}

.follow-button.not-following {
  background-color: #28a745; /* Green for '关注' */
  color: #fff;
  border-color: #28a745;
}
.follow-button.not-following:hover:not(:disabled) {
  background-color: #218838;
}

.follow-button.follow-back {
  background-color: #0077cc;
  color: #fff;
  border-color: #0077cc;
}
.follow-button.follow-back:hover:not(:disabled) {
  background-color: #005bb5;
}

.follow-button.followed,
.follow-button.loading {
  background-color: #eee;
  color: #666;
  border-color: #ddd;
  cursor: default; /* No pointer cursor for grey states or loading */
}
.follow-button.followed:hover:not(:disabled) {
  background-color: #e0e0e0; /* Slightly darker grey on hover */
}

.follow-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* --- Modal Styles --- */
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
  z-index: 2000; /* Higher z-index than logo */
}

.edit-profile-modal {
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%; /* Responsive width */
  max-height: 90vh; /* Max height to prevent overflow */
  overflow-y: auto; /* Scroll if content is too long */
  display: flex;
  flex-direction: column;
  align-items: center;
}

.edit-profile-modal h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 22px;
  text-align: center;
}
.edit-profile-modal h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: #555;
  font-size: 18px;
  text-align: center;
  width: 100%; /* Ensure h4 takes full width */
}

.edit-profile-modal form {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Reuse avatar styles from register page */
.avatar-container {
  width: 100px;
  height: 100px;
  margin-bottom: 20px;
  cursor: pointer;
  position: relative;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.upload-icon {
  width: 30px;
  height: 30px;
}

.form-group {
  width: 100%;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Align labels to the left */
}

.form-group label {
  font-size: 14px;
  color: #555;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
  box-sizing: border-box; /* Include padding and border in element's total width and height */
}

.form-group textarea {
  resize: vertical; /* Allow vertical resizing */
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #0077cc;
  box-shadow: 0 0 0 3px rgba(0, 119, 204, 0.2);
}

.error-message {
  color: #dc3545; /* Red color for errors */
  font-size: 12px;
  margin-top: 5px;
}

.password-divider {
  width: 100%;
  border: 0;
  height: 1px;
  background: #eee;
  margin: 20px 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end; /* Align buttons to the right */
  width: 100%;
  gap: 10px;
  margin-top: 20px;
}

.modal-actions button {
  padding: 10px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.cancel-btn {
  background-color: #ccc;
  color: #333;
  border: none;
}

.cancel-btn:hover {
  background-color: #bbb;
}

.save-btn {
  background-color: #0077cc;
  color: white;
  border: none;
}

.save-btn:hover:not(:disabled) {
  background-color: #005bb5;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Media queries */
@media (max-width: 600px) {
  .profile-container {
    margin-top: 80px;
    padding: 15px;
  }
  .profile-card {
    padding: 15px;
  }
  .avatar {
    width: 80px;
    height: 80px;
    border-radius: 40px;
  }
  .nickname {
    font-size: 20px;
  }
  .bio {
    font-size: 14px;
  }
  .user-meta {
    gap: 5px 10px;
    margin-bottom: 15px;
  }
  .user-meta span {
    font-size: 13px;
    padding: 4px 8px;
  }

  .edit-profile-btn {
    padding: 8px 15px;
    font-size: 14px;
    margin-top: 10px;
  }

  .profile-tabs {
    padding: 0 15px; /* Match profile card padding */
    justify-content: flex-start; /* Align tabs left on small screens */
    gap: 5px;
  }
  .tab-item {
    font-size: 14px;
    padding: 8px 10px;
  }
  .tab-content {
    padding: 0 15px;
    margin-top: 15px;
  }

  .post-section,
  .follow-section,
  .placeholder-section,
  .liked-section,
  .collected-section,
  .Browse-history-section {
    /* <-- 确保这里是 .Browse-history-section */
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    padding: 20px;
  }
  .post-section h3,
  .follow-section h3,
  .placeholder-section h3,
  .liked-section h3,
  .collected-section h3,
  .Browse-history-section h3 {
    font-size: 20px;
    margin-bottom: 20px;
  }
  .post-card {
    padding: 15px;
  }
  .post-title {
    font-size: 16px;
  }
  .post-excerpt {
    font-size: 14px;
  }
  .tag-item {
    font-size: 11px;
    padding: 4px 8px;
  }

  .follow-item {
    flex-direction: column; /* Stack items vertically */
    align-items: flex-start; /* Align text left */
    gap: 10px;
    padding: 10px;
    cursor: auto; /* Remove pointer cursor when stacked */
  }
  .follow-item:hover {
    background-color: #fff; /* Prevent hover effect when stacked */
  }
  .follow-avatar {
    width: 40px;
    height: 40px;
    border-radius: 20px;
  }
  .follow-info {
    width: 100%;
  } /* Allow info to take full width */
  .follow-intro {
    font-size: 12px;
  }
  .follow-button {
    width: 100%; /* Button takes full width */
    min-width: auto;
    padding: 8px;
    font-size: 13px;
    margin-top: 10px; /* Add space above the button */
  }

  /* Modal styles on small screens */
  .edit-profile-modal {
    padding: 20px;
  }
  .edit-profile-modal h3 {
    font-size: 20px;
    margin-bottom: 15px;
  }
  .avatar-container {
    width: 80px;
    height: 80px;
    margin-bottom: 15px;
  }
  .upload-icon {
    width: 24px;
    height: 24px;
  }
  .form-group {
    margin-bottom: 10px;
  }
  .form-group label {
    font-size: 13px;
  }
  .form-group input,
  .form-group textarea,
  .form-group select {
    padding: 8px 10px;
    font-size: 14px;
  }
  .edit-profile-modal h4 {
    font-size: 16px;
    margin-top: 10px;
    margin-bottom: 8px;
  }
  .modal-actions {
    flex-direction: column; /* Stack buttons vertically */
    gap: 8px;
    margin-top: 15px;
  }
  .modal-actions button {
    width: 100%; /* Make buttons full width */
    padding: 10px;
    font-size: 15px;
  }
}
</style>
