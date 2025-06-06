<template>
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

  <div v-if="targetUser" class="profile-container">
    <div class="profile-card">
      <img :src="targetUser.avatar || defaultAvatar" alt="头像" class="avatar" />
      <div class="user-info">
        <h2 class="nickname">{{ targetUser.username }}</h2>
        <p class="bio">{{ targetUser.intro || '这个人很懒，什么都没有写。' }}</p>
        <div class="user-meta">
          <span v-if="targetUser.email">邮箱：{{ targetUser.email }}</span>
          <span v-if="targetUser.register_time">注册时间：{{ targetUser.register_time }}</span>
          <span>文章：{{ targetUserPosts.length }}</span>
          <span @click="activeTab = 'following'" class="clickable-meta"
            >关注：{{ targetUser.following_count }}</span
          >
          <span @click="activeTab = 'followers'" class="clickable-meta"
            >粉丝：{{ targetUser.follower_count }}</span
          >
        </div>
        <button
          v-if="
            isAuthenticated && currentUserStatus && targetUser.id !== currentAuthenticatedUserId
          "
          :class="getFollowButtonClass(currentUserStatus)"
          @click="handleMainFollowButtonClick()"
          :disabled="currentUserStatus.statusLoading"
          class="main-follow-button"
        >
          <span v-if="currentUserStatus.statusLoading">...</span>
          <span v-else>{{ getFollowButtonText(currentUserStatus) }}</span>
        </button>
        <p v-else-if="!isAuthenticated" class="login-to-follow">登录后即可关注</p>
      </div>
    </div>
  </div>
  <div v-else-if="loadingProfile" class="profile-container">
    <p class="loading-message">加载用户资料...</p>
  </div>
  <div v-else class="profile-container">
    <p class="error-message">未找到用户或加载失败。</p>
  </div>

  <div v-if="targetUser" class="profile-tabs">
    <div class="tab-item" :class="{ active: activeTab === 'posts' }" @click="activeTab = 'posts'">
      文章 ({{ targetUserPosts.length }})
    </div>
    <div
      class="tab-item"
      :class="{ active: activeTab === 'following' }"
      @click="((activeTab = 'following'), fetchTargetUserFollowing())"
    >
      关注 ({{ targetUser.following_count }})
    </div>
    <div
      class="tab-item"
      :class="{ active: activeTab === 'followers' }"
      @click="((activeTab = 'followers'), fetchTargetUserFollowers())"
    >
      粉丝 ({{ targetUser.follower_count }})
    </div>
  </div>

  <div v-if="targetUser" class="tab-content">
    <div v-if="activeTab === 'posts'" class="post-section">
      <h3>{{ targetUser.username }}的文章</h3>
      <p v-if="loadingPosts">加载中...</p>
      <div v-else-if="targetUserPosts.length > 0" class="post-list">
        <div
          v-for="post in targetUserPosts"
          :key="post.id"
          class="post-card"
          @click="goToPost(post.id)"
        >
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
      <p v-else class="no-post">Ta还没有发表过任何文章。</p>
    </div>

    <div v-if="activeTab === 'following'" class="follow-section">
      <h3>{{ targetUser.username }}关注的人</h3>
      <p v-if="loadingFollowing">加载中...</p>
      <p v-else-if="targetUserFollowingList.length === 0" class="no-follow">
        {{ targetUser.username }}还没有关注任何人。
      </p>
      <div v-else class="follow-list">
        <div
          v-for="followedUser in targetUserFollowingList"
          :key="followedUser.id"
          class="follow-item"
          @click="goToUserProfile(followedUser.id)"
        >
          <img :src="followedUser.avatar || defaultAvatar" alt="头像" class="follow-avatar" />
          <div class="follow-info">
            <div class="follow-username">{{ followedUser.username }}</div>
            <div class="follow-intro">{{ followedUser.intro || '这个人很懒，什么都没有写。' }}</div>
          </div>
          <button
            v-if="isAuthenticated && followedUser.id !== currentAuthenticatedUserId"
            :class="getFollowButtonClass(followedUser)"
            @click.stop="handleFollowButtonClickInList(followedUser)"
            :disabled="followedUser.statusLoading"
          >
            <span v-if="followedUser.statusLoading">...</span>
            <span v-else>{{ getFollowButtonText(followedUser) }}</span>
          </button>
          <button
            v-else-if="followedUser.id === currentAuthenticatedUserId"
            disabled
            class="follow-button followed self-button"
          >
            自己
          </button>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'followers'" class="follow-section">
      <h3>{{ targetUser.username }}的粉丝</h3>
      <p v-if="loadingFollowers">加载中...</p>
      <p v-else-if="targetUserFollowersList.length === 0" class="no-follow">
        {{ targetUser.username }}还没有粉丝。
      </p>
      <div v-else class="follow-list">
        <div
          v-for="followerUser in targetUserFollowersList"
          :key="followerUser.id"
          class="follow-item"
          @click="goToUserProfile(followerUser.id)"
        >
          <img :src="followerUser.avatar || defaultAvatar" alt="头像" class="follow-avatar" />
          <div class="follow-info">
            <div class="follow-username">{{ followerUser.username }}</div>
            <div class="follow-intro">{{ followerUser.intro || '这个人很懒，什么都没有写。' }}</div>
          </div>
          <button
            v-if="isAuthenticated && followerUser.id !== currentAuthenticatedUserId"
            :class="getFollowButtonClass(followerUser)"
            @click.stop="handleFollowButtonClickInList(followerUser)"
            :disabled="followerUser.statusLoading"
          >
            <span v-if="followerUser.statusLoading">...</span>
            <span v-else>{{ getFollowButtonText(followerUser) }}</span>
          </button>
          <button
            v-else-if="followerUser.id === currentAuthenticatedUserId"
            disabled
            class="follow-button followed self-button"
          >
            自己
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios, { AxiosError, isAxiosError } from 'axios'
import { useRouter, useRoute } from 'vue-router'
import HeaderBar from '@/components/HeaderBar.vue'
const router = useRouter()
const route = useRoute() // Use useRoute to access route parameters

// Interface for a user object in the follow lists, including follow status
interface UserWithStatus {
  id: number
  username: string
  nickname?: string
  avatar: string
  intro?: string
  // 以下是需要添加的属性
  email?: string // 或者 string 如果它总是存在
  register_time?: string // 或者合适的日期/时间类型
  following_count: number // 根据您的用法，它似乎总是被初始化或赋值为 number
  follower_count: number // 同上
  // Status relative to the currently authenticated user
  is_following?: boolean
  is_followed_by?: boolean
  is_mutual?: boolean
  statusLoading?: boolean
}

// Data for the user whose profile is being viewed
const targetUser = ref<UserWithStatus | null>(null)

interface TargetUserPost {
  id: number
  title: string
  content: string
  tag?: string
  permission: number // Assuming permission is returned here
}

const targetUserPosts = ref<TargetUserPost[]>([])
const targetUserFollowingList = ref<UserWithStatus[]>([])
const targetUserFollowersList = ref<UserWithStatus[]>([])
// Placeholders for future tabs
const targetUserLikedPosts = ref([])
const targetUserCollectedPosts = ref([])

// Status between the CURRENT authenticated user and the TARGET user
const currentUserStatus = ref<{
  is_following?: boolean
  is_followed_by?: boolean
  is_mutual?: boolean
  statusLoading?: boolean
} | null>(null)

const defaultAvatar = '/default-avatar.png' // Make sure this path is correct

// State for tabs
const activeTab = ref<'posts' | 'following' | 'followers' | 'likes' | 'collections'>('posts')

// Loading states
const loadingProfile = ref(false)
const loadingPosts = ref(false)
const loadingFollowing = ref(false)
const loadingFollowers = ref(false)

// Authenticated user's ID (needed for comparing against list users)
const currentAuthenticatedUserId = ref<number | null>(null)
const isAuthenticated = ref(false)

// Watch for changes in the route parameter (userId)
watch(
  () => route.params.userId,
  async (newUserId, oldUserId) => {
    if (newUserId && newUserId !== oldUserId) {
      console.log('Route userId changed, fetching new profile:', newUserId)
      // Reset state and fetch data for the new user
      resetState()
      await fetchDataForUser(Number(newUserId))
    }
  },
)

onMounted(async () => {
  // Check for authentication status immediately
  const token = localStorage.getItem('token')
  if (token) {
    isAuthenticated.value = true
    // Fetch current authenticated user's ID if needed for comparison
    // A dedicated lightweight endpoint for getting authenticated user's ID might be best
    // For now, we'll rely on fetching the current user's profile once to get their ID
    try {
      const profileRes = await axios.get('http://127.0.0.1:5000/user/getProfile', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (profileRes.data.state === 1 && profileRes.data.data && profileRes.data.data.id) {
        currentAuthenticatedUserId.value = profileRes.data.data.id
      }
    } catch (error) {
      console.error("Could not fetch authenticated user's ID:", error)
      isAuthenticated.value = false // Assume not authenticated if we can't get ID
    }
  } else {
    isAuthenticated.value = false
    currentAuthenticatedUserId.value = null
  }

  // Fetch data for the user specified in the initial route
  const userId = Number(route.params.userId)
  if (!isNaN(userId) && userId > 0) {
    await fetchDataForUser(userId)

    // Check for tab in query params on initial load
    const tabFromQuery = route.query.tab as typeof activeTab.value
    if (
      tabFromQuery &&
      ['posts', 'following', 'followers', 'likes', 'collections'].includes(tabFromQuery)
    ) {
      activeTab.value = tabFromQuery
      // Trigger fetch for the list tab if specified
      if (tabFromQuery === 'following') fetchTargetUserFollowing()
      if (tabFromQuery === 'followers') fetchTargetUserFollowers()
      // Add similar logic for likes/collections
    }
  } else {
    console.error('Invalid user ID in route parameters.')
    // Optionally redirect or show an error message
  }
})

// Function to reset component state when changing users
function resetState() {
  targetUser.value = null
  targetUserPosts.value = []
  targetUserFollowingList.value = []
  targetUserFollowersList.value = []
  targetUserLikedPosts.value = [] // Reset placeholders
  targetUserCollectedPosts.value = [] // Reset placeholders
  currentUserStatus.value = null
  activeTab.value = 'posts' // Reset to default tab
  loadingProfile.value = false
  loadingPosts.value = false
  loadingFollowing.value = false
  loadingFollowers.value = false
}

// Main function to fetch all necessary data for the target user
async function fetchDataForUser(userId: number) {
  loadingProfile.value = true
  try {
    // 1. Fetch Target User Profile (Assuming /user/profile/<int:user_id> exists)
    const profileRes = await axios.get(`http://127.0.0.1:5000/user/profile/${userId}`)

    if (profileRes.data) {
      // Assuming success doesn't use { state: 1 } for this endpoint
      targetUser.value = { ...profileRes.data, following_count: 0, follower_count: 0 } // Initialize counts

      // 2. Fetch Follow Counts for Target User
      try {
        const followStatsRes = await axios.get(`http://127.0.0.1:5000/follow-count/${userId}`)
        if (followStatsRes.data && typeof followStatsRes.data.following_count !== 'undefined') {
          if (targetUser.value) {
            // Check again as fetch is async
            targetUser.value.following_count = followStatsRes.data.following_count
            targetUser.value.follower_count = followStatsRes.data.follower_count
          }
        } else {
          console.warn('Failed to fetch follow stats for target user:', followStatsRes.data)
        }
      } catch (statsError) {
        console.error('Error fetching follow stats for target user:', statsError)
      }

      // 3. Fetch Articles for Target User (Assuming /article/list/by-user/<int:user_id> exists and respects permission)
      loadingPosts.value = true
      try {
        const postRes = await axios.get(`http://127.0.0.1:5000/article/list/by-user/${userId}`, {
          headers: isAuthenticated.value
            ? { Authorization: `Bearer ${localStorage.getItem('token')}` }
            : {},
          // Include auth header if user is logged in, backend should handle permission based on auth status
        })
        if (postRes.data && Array.isArray(postRes.data.data)) {
          // Adjust based on your API's success structure
          // Filter public posts or all if authenticated and allowed
          targetUserPosts.value = postRes.data.data
        } else if (Array.isArray(postRes.data)) {
          // Fallback
          targetUserPosts.value = postRes.data
        } else {
          console.error('Fetched target user posts data is not in expected format:', postRes.data)
          targetUserPosts.value = []
        }
      } catch (postError) {
        console.error('Error fetching target user articles:', postError)
        targetUserPosts.value = []
      } finally {
        loadingPosts.value = false
      }

      // 4. Fetch Follow Status between CURRENT user and TARGET user (if authenticated)
      if (
        isAuthenticated.value &&
        currentAuthenticatedUserId.value !== null &&
        targetUser.value?.id
      ) {
        currentUserStatus.value = { statusLoading: true } // Set initial loading state
        try {
          const status = await fetchFollowStatus(targetUser.value.id) // Reusing fetchFollowStatus from MyProfile
          currentUserStatus.value = { ...status, statusLoading: false }
        } catch (statusError) {
          console.error('Error fetching current user follow status vs target user:', statusError)
          currentUserStatus.value = null // Clear status on error
        }
      } else {
        currentUserStatus.value = null // No status if not authenticated
      }
    } else {
      console.error('Failed to fetch target user profile:', profileRes.data)
      targetUser.value = null
    }
  } catch (error) {
    console.error('Error fetching data for user profile:', error)
    targetUser.value = null // Ensure targetUser is null on error
  } finally {
    loadingProfile.value = false
  }
}

// Fetch list of users the TARGET user is following
async function fetchTargetUserFollowing() {
  const token = localStorage.getItem('token')
  // Needs targetUser.id, and optionally current user token if needed for list content permissions
  if (!targetUser.value?.id || loadingFollowing.value) return

  loadingFollowing.value = true
  targetUserFollowingList.value = [] // Clear previous list
  try {
    // Assuming /following/<int:user_id> endpoint exists
    const res = await axios.get(`http://127.0.0.1:5000/following/${targetUser.value.id}`, {
      headers: isAuthenticated.value ? { Authorization: `Bearer ${token}` } : {},
      // Include auth header if user is logged in, backend might need it
    })

    if (Array.isArray(res.data)) {
      const usersWithStatus: UserWithStatus[] = []
      // Fetch follow status for each user in THIS list relative to the *CURRENT authenticated* user
      for (const listedUser of res.data) {
        if (listedUser.id) {
          const status =
            isAuthenticated.value && currentAuthenticatedUserId.value !== null
              ? await fetchFollowStatus(listedUser.id)
              : {} // No status if not authenticated
          usersWithStatus.push({ ...listedUser, ...status, statusLoading: false })
        } else {
          console.warn('User object in following list is missing ID:', listedUser)
          usersWithStatus.push({ ...listedUser, statusLoading: false })
        }
      }
      targetUserFollowingList.value = usersWithStatus
    } else {
      console.error('Fetched target user following data is not an array:', res.data)
      targetUserFollowingList.value = []
    }
  } catch (error) {
    console.error('Error fetching target user following list:', error)
    targetUserFollowingList.value = []
  } finally {
    loadingFollowing.value = false
  }
}

// Fetch list of users who follow the TARGET user
async function fetchTargetUserFollowers() {
  const token = localStorage.getItem('token')
  // Needs targetUser.id, and optionally current user token
  if (!targetUser.value?.id || loadingFollowers.value) return

  loadingFollowers.value = true
  targetUserFollowersList.value = [] // Clear previous list
  try {
    // Assuming /followers/<int:user_id> endpoint exists
    const res = await axios.get(`http://127.0.0.1:5000/followers/${targetUser.value.id}`, {
      headers: isAuthenticated.value ? { Authorization: `Bearer ${token}` } : {},
      // Include auth header if user is logged in
    })

    if (Array.isArray(res.data)) {
      const usersWithStatus: UserWithStatus[] = []
      // Fetch follow status for each user in THIS list relative to the *CURRENT authenticated* user
      for (const listedUser of res.data) {
        if (listedUser.id) {
          const status =
            isAuthenticated.value && currentAuthenticatedUserId.value !== null
              ? await fetchFollowStatus(listedUser.id)
              : {} // No status if not authenticated
          usersWithStatus.push({ ...listedUser, ...status, statusLoading: false })
        } else {
          console.warn('User object in followers list is missing ID:', listedUser)
          usersWithStatus.push({ ...listedUser, statusLoading: false })
        }
      }
      targetUserFollowersList.value = usersWithStatus
    } else {
      console.error('Fetched target user followers data is not an array:', res.data)
      targetUserFollowersList.value = []
    }
  } catch (error) {
    console.error('Error fetching target user followers list:', error)
    targetUserFollowersList.value = []
  } finally {
    loadingFollowers.value = false
  }
}

// Fetch follow status between CURRENT user and a specific targetUserId (from the list)
async function fetchFollowStatus(
  targetUserId: number,
): Promise<{ is_following?: boolean; is_followed_by?: boolean; is_mutual?: boolean }> {
  const token = localStorage.getItem('token')
  // Requires authenticated user and the target user ID
  if (!token || !currentAuthenticatedUserId.value || !targetUserId) {
    // console.warn("Cannot fetch follow status: Not authenticated or missing IDs");
    return {} // Return empty status if not authenticated or missing IDs
  }

  try {
    const res = await axios.get(`http://127.0.0.1:5000/friends/${targetUserId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    // Returns { "is_following": bool, "is_followed_by": bool, "is_mutual": bool }
    return res.data
  } catch (error) {
    console.error(`Error fetching follow status for user ${targetUserId}:`, error)
    // Use type guard for error handling
    if (isAxiosError(error)) {
      // Log specific Axios error details if needed
      console.error('Axios error details:', error.response?.status, error.response?.data)
    }
    return {} // Return empty status on error
  }
}

// --- Follow/Unfollow Logic for the MAIN Target User Button ---
async function handleMainFollowButtonClick() {
  if (
    !targetUser.value?.id ||
    !currentUserStatus.value ||
    !isAuthenticated.value ||
    currentUserStatus.value.statusLoading
  )
    return

  currentUserStatus.value.statusLoading = true // Set loading state for the main button

  const currentStatusText = getFollowButtonText(currentUserStatus.value) // Use currentUserStatus for button text

  if (currentStatusText === '已关注' || currentStatusText === '已互关') {
    // Confirm unfollow
    if (confirm(`确定要取消关注 ${targetUser.value.username} 吗？`)) {
      await unfollowUser(targetUser.value.id, currentUserStatus.value) // Pass target user ID and status ref
    } else {
      currentUserStatus.value.statusLoading = false // Cancel loading if user cancels
    }
  } else if (currentStatusText === '关注' || currentStatusText === '去回关') {
    // Follow or Follow back
    await followUser(targetUser.value.id, currentUserStatus.value) // Pass target user ID and status ref
  } else {
    currentUserStatus.value.statusLoading = false // Reset loading if no action was taken
  }
}

// --- Follow/Unfollow Logic for Users IN the Following/Followers Lists ---
async function handleFollowButtonClickInList(targetUser: UserWithStatus) {
  if (!targetUser.id || !isAuthenticated.value || targetUser.statusLoading) return

  // Find the user in the respective list to update its state
  const listToUpdate =
    activeTab.value === 'following' ? targetUserFollowingList : targetUserFollowersList
  const targetUserInList = listToUpdate.value.find((u) => u.id === targetUser.id)
  if (!targetUserInList) return

  targetUserInList.statusLoading = true // Set loading state for this specific user item

  const currentStatusText = getFollowButtonText(targetUserInList) // Use the list user's status

  if (currentStatusText === '已关注' || currentStatusText === '已互关') {
    // Confirm unfollow
    if (confirm(`确定要取消关注 ${targetUserInList.username} 吗？`)) {
      await unfollowUser(targetUserInList.id, targetUserInList) // Pass list user ID and their status ref
    } else {
      targetUserInList.statusLoading = false // Cancel loading if user cancels
    }
  } else if (currentStatusText === '关注' || currentStatusText === '去回关') {
    // Follow or Follow back
    await followUser(targetUserInList.id, targetUserInList) // Pass list user ID and their status ref
  } else {
    targetUserInList.statusLoading = false // Reset loading if no action was taken
  }
}

// Perform follow action (reusable function, takes target user ID and the status ref to update)
async function followUser(
  targetUserId: number,
  statusRef: {
    is_following?: boolean
    is_followed_by?: boolean
    is_mutual?: boolean
    statusLoading?: boolean
  },
) {
  const token = localStorage.getItem('token')
  if (!token || !currentAuthenticatedUserId.value || !targetUserId || !statusRef) {
    console.error('Cannot follow: Missing token, current user ID, target ID, or status ref.')
    if (statusRef) statusRef.statusLoading = false
    return
  }
  statusRef.statusLoading = true // Ensure loading is set

  try {
    await axios.post(
      `http://127.0.0.1:5000/follow/${targetUserId}`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    )
    console.log(`Followed user ID: ${targetUserId}`)

    // Refetch status for this specific user to update the button state
    const updatedStatus = await fetchFollowStatus(targetUserId)
    Object.assign(statusRef, updatedStatus) // Update the passed status ref

    // Optionally refetch counts for the MAIN target user profile card after CURRENT user follows someone
    if (targetUser.value?.id === targetUserId) {
      // Only update if we followed the person whose page we are on
      const followStatsRes = await axios.get(`http://127.0.0.1:5000/follow-count/${targetUserId}`)
      if (followStatsRes.data && targetUser.value) {
        targetUser.value.following_count = followStatsRes.data.following_count
        // Follower count of the TARGET user might increase if the CURRENT user is a new follower
        targetUser.value.follower_count = followStatsRes.data.follower_count
      }
    }
    // If the user being followed is in the lists being displayed, their status is updated via statusRef already.
    // If the current user follows someone who was a follower, they become mutually following.
    // If the current user follows someone they weren't already following, their 'following' count increases.
    // The target user's 'follower' count increases. These counts are refetched above.
  } catch (error) {
    console.error(`Error following user ID ${targetUserId}:`, error)
    if (isAxiosError(error)) {
      alert(`关注失败: ${error.response?.data?.message || error.message}`)
    } else {
      alert(`关注失败: ${String(error)}`)
    }
    // Refetch status on error to potentially revert optimistic update
    const updatedStatus = await fetchFollowStatus(targetUserId)
    Object.assign(statusRef, updatedStatus)
  } finally {
    statusRef.statusLoading = false
  }
}

// Perform unfollow action (reusable function, takes target user ID and the status ref to update)
async function unfollowUser(
  targetUserId: number,
  statusRef: {
    is_following?: boolean
    is_followed_by?: boolean
    is_mutual?: boolean
    statusLoading?: boolean
  },
) {
  const token = localStorage.getItem('token')
  if (!token || !currentAuthenticatedUserId.value || !targetUserId || !statusRef) {
    console.error('Cannot unfollow: Missing token, current user ID, target ID, or status ref.')
    if (statusRef) statusRef.statusLoading = false
    return
  }
  statusRef.statusLoading = true // Ensure loading is set

  try {
    await axios.delete(`http://127.0.0.1:5000/unfollow/${targetUserId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    console.log(`Unfollowed user ID: ${targetUserId}`)

    // Refetch status for this specific user
    const updatedStatus = await fetchFollowStatus(targetUserId)
    Object.assign(statusRef, updatedStatus) // Update the passed status ref

    // Optionally refetch counts for the MAIN target user profile card
    if (targetUser.value?.id === targetUserId) {
      // Only update if we unfollowed the person whose page we are on
      const followStatsRes = await axios.get(`http://127.0.0.1:5000/follow-count/${targetUserId}`)
      if (followStatsRes.data && targetUser.value) {
        targetUser.value.following_count = followStatsRes.data.following_count
        // Target user's follower count might decrease
        targetUser.value.follower_count = followStatsRes.data.follower_count
      }
    }
    // Update counts on *current user's* profile if needed - this component doesn't show current user's counts,
    // but if you navigate back to MyProfile, the counts would need refetching there.
  } catch (error) {
    console.error(`Error unfollowing user ID ${targetUserId}:`, error)
    if (isAxiosError(error)) {
      alert(`取消关注失败: ${error.response?.data?.message || error.message}`)
    } else {
      alert(`取消关注失败: ${String(error)}`)
    }
    // Refetch status on error to potentially revert optimistic update
    const updatedStatus = await fetchFollowStatus(targetUserId)
    Object.assign(statusRef, updatedStatus)
  } finally {
    statusRef.statusLoading = false
  }
}

// Determine button text based on user's follow status relative to the *CURRENT* user
function getFollowButtonText(status: {
  is_following?: boolean
  is_followed_by?: boolean
  is_mutual?: boolean
}): string {
  const isFollowing = status.is_following === true
  const isFollowedBy = status.is_followed_by === true
  const isMutual = status.is_mutual === true // Or calculate: isFollowing && isFollowedBy

  if (isMutual) {
    return '已互关'
  } else if (isFollowing) {
    return '已关注'
  } else if (isFollowedBy) {
    return '去回关'
  } else {
    return '关注' // Default state when current user doesn't follow and isn't followed by target
  }
}

// Determine button class for styling based on state
function getFollowButtonClass(status: {
  is_following?: boolean
  is_followed_by?: boolean
  is_mutual?: boolean
  statusLoading?: boolean
}): string[] {
  const classes = ['follow-button']
  const statusText = getFollowButtonText(status)

  if (statusText === '已关注' || statusText === '已互关') {
    classes.push('followed') // Grey style
  } else if (statusText === '去回关') {
    classes.push('follow-back') // Blue style
  } else if (statusText === '关注') {
    classes.push('not-following') // Primary/Green style for 'Follow'
  }

  if (status.statusLoading) {
    classes.push('loading')
  }

  return classes
}

// --- Navigation and Helper Functions ---

// Navigate to an article detail page
function goToPost(id: number) {
  router.push(`/post/${id}`)
}

// // Navigate to a user profile page
// function goToUserProfile(id: number) {
//     // Prevent navigating to the same page or if id is missing
//     if (targetUser.value?.id === id || !id) return;
//     // Navigate to the new component with the user ID parameter
//     router.push({ name: 'OtherUserProfile', params: { userId: id } });
//      // Note: The watch on route.params.userId handles fetching data
// }

function goToUserProfile(id: number) {
  if (!id) return

  // Check if the target user ID is the same as the current authenticated user ID
  if (currentAuthenticatedUserId.value !== null && id === currentAuthenticatedUserId.value) {
    console.log('Navigating to My Profile')
    router.push({ name: 'MyProfile' }) // Navigate to the current user's profile route
  } else if (targetUser.value?.id !== id) {
    // Only navigate to OtherUserProfile if it's a different user than the current page's target
    console.log('Navigating to Other User Profile:', id)
    router.push({ name: 'OtherUserProfile', params: { userId: id } })
    // Note: The watch on route.params.userId handles fetching data for the new user
  } else {
    // If the ID is the same as the current page's target user, do nothing
    console.log("Already on this user's profile page:", id)
  }
}

function searchByTag(tag: string) {
  if (!tag) return
  // Navigate to home and set the search query
  router.push({ path: '/', query: { search: tag } })
}

function getExcerpt(content: string): string {
  if (!content) return ''
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = content
  const text = tempDiv.textContent || tempDiv.innerText || ''
  return text.length > 50 ? text.slice(0, 50) + '...' : text
}
</script>

<style scoped>
/* Import or copy shared styles here or use CSS modules */
/* For simplicity in this example, I'll include the styles directly */

/* --- Existing Shared Styles (Copied from MyProfile.vue) --- */
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
  position: relative; /* Needed for absolute positioning of follow button */
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
  margin-bottom: 20px; /* Added margin below meta */
}

.user-meta span {
  margin: 5px; /* Adjusted margin */
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

/* --- Styles for the MAIN Follow Button on Profile Card --- */
.main-follow-button {
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    opacity 0.2s ease;
  border: 1px solid transparent;
  margin-top: 10px; /* Space above button */
}

.main-follow-button.not-following {
  background-color: #28a745; /* Green for follow */
  color: #fff;
  border-color: #28a745;
}
.main-follow-button.not-following:hover:not(:disabled) {
  background-color: #218838;
}

/* Reusing .followed and .follow-back styles from list buttons */
.main-follow-button.followed,
.main-follow-button.loading {
  background-color: #eee;
  color: #666;
  border-color: #ddd;
  cursor: default;
}
.main-follow-button.follow-back {
  background-color: #0077cc;
  color: #fff;
  border-color: #0077cc;
}
.main-follow-button.follow-back:hover:not(:disabled) {
  background-color: #005bb5;
}

.main-follow-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-to-follow {
  font-size: 14px;
  color: #777;
  margin-top: 10px;
}

/* --- Styles for Tabs and Lists (Copied/Adapted) --- */
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
.placeholder-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  padding: 20px;
}

.post-section h3,
.follow-section h3,
.placeholder-section h3 {
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

.no-post,
.no-follow,
.placeholder-section p {
  text-align: center;
  color: #777;
  font-size: 16px;
  padding: 30px 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.loading-message,
.error-message {
  text-align: center;
  font-size: 18px;
  color: #555;
  padding: 40px 20px;
}
.error-message {
  color: #d9534f; /* Red for error */
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
  cursor: pointer; /* Make the whole item clickable to navigate */
  transition: background-color 0.2s ease;
}

.follow-item:hover {
  background-color: #f0f0f0; /* Indicate clickable */
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

/* Styles for buttons WITHIN the follow list items */
.follow-item button {
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition:
    background-color 0.2s ease,
    opacity 0.2s ease;
  flex-shrink: 0; /* Prevent button from shrinking */
  min-width: 80px; /* Give buttons a consistent minimum width */
  text-align: center;
  border: 1px solid transparent; /* Default transparent border */
}

.follow-item button.follow-back {
  background-color: #0077cc;
  color: #fff;
  border-color: #0077cc;
}
.follow-item button.follow-back:hover:not(:disabled) {
  background-color: #005bb5;
}

.follow-item button.followed,
.follow-item button.loading,
.follow-item button.self-button {
  /* Style for "自己" button */
  background-color: #eee;
  color: #666;
  border-color: #ddd;
  cursor: default; /* No pointer cursor */
}

.follow-item button.not-following {
  background-color: #28a745; /* Green for follow */
  color: #fff;
  border-color: #28a745;
}
.follow-item button.not-following:hover:not(:disabled) {
  background-color: #218838;
}

.follow-item button:disabled {
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
  } /* Adjusted margin */

  .profile-tabs {
    padding: 0 15px; /* Match profile card padding */
    justify-content: flex-start; /* Align tabs left on small screens */
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
  .placeholder-section {
    padding: 15px;
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
  .follow-item button {
    /* Style for buttons WITHIN list items */
    width: 100%; /* Button takes full width */
    min-width: auto;
    padding: 8px;
    font-size: 13px;
  }
  .main-follow-button {
    /* Style for the main profile button */
    width: 100%;
    padding: 10px;
    font-size: 14px;
  }
}
</style>
