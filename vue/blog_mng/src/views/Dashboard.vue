<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <Sidebar 
        @show-profile="showSection('profile')" 
        @show-managers="showSection('managers')" 
        @show-users="showSection('users')" 
        @show-articles="showSection('articles')" 
        @show-comments="showSection('comments')"
      />
      
      <div class="dashboard-content">
        <Profile 
          v-if="currentView === 'profile'"
          :profile="profile" 
          :isLoading="isLoading" 
          @profile-updated="loadProfile"
        />
        <UserTable 
          v-if="currentView === 'users'" 
          :users="users" 
          :isLoading="isLoading" 
          @refresh-users="loadUsers"
          @show-userPublishedArticles="showUserPublishedArticles"
          @show-userComments="showUserComments"
          @show-userLikedArticles="showUserLikedArticles"
          @show-followers="showFollowers"
          @show-following="showFollowing"
          @show-user-info="showUserInfo"
        />
        <UserComments 
          v-if="currentView === 'userComments'" 
          :userId="currentCommentUserId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-comment-review="showCommentReview"
          @show-comment-like-users="showCommentLikeUsers"
          @show-comment-replies="showCommentReplies"
          @show-comment-detail="showCommentDeatail"
          @show-user-info="showUserInfo"
          @show-articleDetail="showArticleDetail"
        />
        <UserLikedArticles 
          v-if="currentView === 'userLikedArticles'" 
          :userId="currentLikedArticleUserId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-articleDetail="showArticleDetail"
        />
        <UserPublishedArticles 
          v-if="currentView === 'userPublishedArticles'" 
          :userId="currentPublishedArticleUserId"
          :isLoading="isLoading"
          @show-articleDetail="showArticleDetail"
          @show-articleBrowsers="showArticleBrowsers"
          @show-articleLikeUsers="showArticleLikeUsers"
          @show-articleFavorites="showArticleFavorites"
          @show-articleCommentUsers="showArticleCommentUsers"
          @back-to-list="handleBackToList"
        />
        <div v-if="currentView === 'managers' && isAdmin">
          <ManagerTable 
            :managers="managers" 
            :isLoading="isLoading" 
            @delete-manager="deleteManager" 
            @add-manager="addManager"
            @refresh-managers="loadManagers" 
          />
        </div>
        <div v-if="currentView === 'managers' && !isAdmin">
          <p>权限不足，无法查看管理员列表</p>
        </div>
        <ArticleTable 
          v-if="currentView === 'articles'" 
          :articles="articles" 
          :isLoading="isLoading" 
          :loadArticles="loadArticles"
          @show-articleDetail="showArticleDetail"
          @change-permission="changeArticlePermission"
          @show-articleBrowsers="showArticleBrowsers"
          @show-articleLikeUsers="showArticleLikeUsers"
          @show-articleFavorites="showArticleFavorites"
          @show-articleCommentUsers="showArticleCommentUsers"
          @show-user-info="showUserInfo"
        />
        <ArticleDetail 
          v-if="currentView === 'articleDetail'" 
          :articleId="currentArticleId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-user-info="showUserInfo"
        />
        <ArticleFavorites 
          v-if="currentView === 'articleFavorites'" 
          :articleId="currentFavoritesArticleId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-user-info="showUserInfo"
        />
        <ArticleCommentUsers 
          v-if="currentView === 'articleCommentUsers'" 
          :articleId="currentCommentArticleId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-user-info="showUserInfo"
          @show-comment-detail="showCommentDeatail"
        />
        <ArticleLikeUsers 
          v-if="currentView === 'articleLikeUsers'" 
          :articleId="currentLikeArticleId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-user-info="showUserInfo"
        />
        <ArticleBrowsers 
          v-if="currentView === 'articleBrowsers'" 
          :articleId="currentBrowseArticleId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-user-info="showUserInfo"
        />
        <CommentTable 
          v-if="currentView === 'comments'" 
          :comments="comments" 
          :isLoading="isLoading"
          @load-comments="loadComments"
          @show-comment-review="showCommentReview"
          @show-comment-like-users="showCommentLikeUsers"
          @show-comment-replies="showCommentReplies"
          @show-comment-detail="showCommentDeatail"
          @show-user-info="showUserInfo"
          @show-articleDetail="showArticleDetail"
        />
        <CommentReview 
          v-if="currentView === 'commentReview'" 
          :commentId="currentCommentId"
          :isLoading="isLoading"
          @show-comments="showSection('comments')"
          @show-comment-review="showCommentReview"
          @back-to-list="handleBackToList"
        />
        <CommentLikeUsers 
          v-if="currentView === 'commentLikeUsers'" 
          :commentId="currentCommentId"
          :isLoading="isLoading"
          @back-to-list="handleBackToList"
          @show-user-info="showUserInfo"
        />
        <CommentReplies 
          v-if="currentView === 'commentReplies'" 
          :commentId="currentCommentId"
          :isLoading="isLoading"
          @show-comment-review="showCommentReview"
          @show-comment-like-users="showCommentLikeUsers"
          @show-comment-replies="showCommentReplies"
          @show-comment-detail="showCommentDeatail"
          @show-user-info="showUserInfo"
          @back-to-list="handleBackToList"
        />
        <CommentDeatail 
          v-if="currentView === 'CommentDeatail'" 
          :parentId="currentCommentId_dataild"
          :isLoading="isLoading"
          @show-comment-like-users="showCommentLikeUsers"
          @show-comment-replies="showCommentReplies"
          @show-comment-detail="showCommentDeatail"
          @show-user-info="showUserInfo"
          @back-to-list="handleBackToList"
        />
        <!-- 粉丝列表 -->
        <UserFollowList 
          v-if="currentView === 'followers'" 
          :userId="currentUserId"
          :isFollowers="true"
          :ownerUsername="currentUser.username"
          :ownerId="currentUserId"
           @back-to-list="handleBackToList"
           @show-user-info="showUserInfo"
        />
        <!-- 关注列表 -->
        <UserFollowList 
          v-if="currentView === 'following'" 
          :userId="currentUserId"
          :isFollowers="false"
          :ownerUsername="currentUser.username"
          :ownerId="currentUserId"
           @back-to-list="handleBackToList"
           @show-user-info="showUserInfo"
        />
        <UserInfo 
          v-if="currentView === 'userInfo'" 
          :userId="currentUserId"
          :isLoading="isLoading"
          @show-userPublishedArticles="showUserPublishedArticles"
          @show-userComments="showUserComments"
          @show-userLikedArticles="showUserLikedArticles"
          @show-followers="showFollowers"
          @show-following="showFollowing"
          @back-to-list="handleBackToList"
        />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Sidebar from '../components/Sidebar.vue';
import Profile from '../components/Profile.vue';
import UserTable from '../components/UserTable.vue';
import ManagerTable from '../components/ManagerTable.vue';
import ArticleTable from '../components/ArticleTable.vue';
import UserFollowList from '../components/UserFollowList.vue';
import ArticleDetail from '../components/ArticleDetail.vue';
import ArticleFavorites from '../components/ArticleFavorites.vue';
import ArticleCommentUsers from '../components/ArticleCommentUsers.vue';
import ArticleLikeUsers from '../components/ArticleLikeUsers.vue';
import ArticleBrowsers from '../components/ArticleBrowsers.vue';
import UserComments from '../components/UserComments.vue';
import UserLikedArticles from '../components/UserLikedArticles.vue';
import UserPublishedArticles from '../components/UserPublishedArticles.vue';
import CommentTable from '../components/CommentTable.vue';
import CommentReview from '../components/CommentReview.vue';
import CommentLikeUsers from '../components/CommentLikeUsers.vue';
import CommentReplies from '../components/CommentReplies.vue';
import CommentDeatail from '../components/CommentDetail.vue';
import UserInfo from '../components/UserInfo.vue';

export default {
  components: {
    Sidebar,
    Profile,
    UserTable,
    ManagerTable,
    ArticleTable,
    UserFollowList,
    ArticleDetail,
    ArticleFavorites,
    ArticleCommentUsers,
    ArticleLikeUsers,
    ArticleBrowsers,
    UserComments,
    UserLikedArticles,
    UserPublishedArticles,
    CommentTable,
    CommentReview,
    CommentLikeUsers,
    CommentReplies,
    CommentDeatail,
    UserInfo
  },
  data() {
    return {
      isLoading: false,
      currentView: 'profile',
      profile: {},
      users: [],
      managers: [],
      articles: [],
      comments: [], // 用于存储评论数据
      isAdmin: false,
      currentUserId: null,
      currentUser: {},
      currentArticleId: null,
      currentFavoritesArticleId: null,
      currentCommentArticleId: null,
      currentLikeArticleId: null,
      currentBrowseArticleId: null,
      currentCommentUserId: null,
      currentLikedArticleUserId: null,
      currentPublishedArticleUserId: null,
      currentCommentId: null, // 用于存储当前审核的评论 ID
      currentCommentId_dataild: null, // 用于存储当前查看的评论 ID
      currentUserId: null, // 用于存储当前查看的用户 ID
      previousView: null // 用于记录来源页面
    };
  },
  created() {
    this.loadProfile();
    this.checkAdminStatus();
  },
  methods: {
    showSection(section) {
      if (section === 'managers' && !this.isAdmin) {
        alert('权限不足，无法查看管理员列表');
        return;
      }
      this.currentView = section;
      this.loadDataForSection(section);
    },
    checkAdminStatus() {
      const currentMngId = localStorage.getItem('currentMngId');
      if (currentMngId) {
        this.isAdmin = currentMngId === '1';
      } else if (this.profile && this.profile.mng_id) {
        this.isAdmin = this.profile.mng_id === 1;
      } else {
        this.isAdmin = false;
      }
    },
    loadDataForSection(section) {
      switch(section) {
        case 'profile':
          this.loadProfile();
          break;
        case 'managers':
          if (this.isAdmin) {
            this.loadManagers();
          } else {
            alert('权限不足，无法查看管理员列表');
          }
          break;
        case 'users':
          this.loadUsers();
          break;
        case 'articles':
          this.loadArticles();
          break;
        case 'comments':
          this.loadComments();
          break;
      }
    },
    async loadProfile() {
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/profile', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        if (data.state === 1) {
          this.profile = data.profile;
          if (this.isAdmin === false && this.profile.mng_id) {
            this.isAdmin = this.profile.mng_id === 1;
          }
        } else {
          console.error('获取管理员信息失败:', data.message);
        }
      } catch (error) {
        console.error('请求管理员信息接口失败:', error);
      }
    },
    async loadManagers() {
      if (!this.isAdmin) {
        alert('权限不足，无法查看管理员列表');
        return;
      }
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/manager_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        if (data.state === 1) {
          this.managers = data.managers;
        } else {
          console.error('获取管理员列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求管理员列表接口失败:', error);
      }
    },
    async loadUsers() {
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/user_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        console.log(data);
        if (data.state === 1) {
          this.users = data.users;
        } else {
          console.error('获取用户列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求用户列表接口失败:', error);
      }
    },
    async loadArticles() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get('http://localhost:5000/manager/article_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        console.log(data);
        if (data.state === 1) {
          this.articles = data.articles;
        } else {
          console.error('获取文章列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求文章列表接口失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async loadComments() {
      this.isLoading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5000/manager/comment_list', {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        if (data.state === 1) {
          this.comments = data.comments_list; // 假设后端返回的评论数据在 comments_list 字段中
        } else {
          console.error('获取评论列表失败:', data.message);
        }
      } catch (error) {
        console.error('请求评论列表接口失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async getCurrentUser(userId) {
      try {
        const token = localStorage.getItem('token'); 
        const response = await axios.get(`http://localhost:5000/manager/user/${userId}`, {
          headers: {
            'Authorization': 'Bearer ' + token
          }
        });
        const data = response.data;
        console.log("名字");
        console.log(data.user);
        if (data.state === 1) {
          this.currentUser = data.user;
        } else {
          console.error('获取用户信息失败:', data.message);
        }
      } catch (error) {
        console.error('请求用户信息接口失败:', error);
      }
    },
    async changeArticlePermission() {
      this.currentArticle.permission = this.permissionForm.new_permission;
    },
    showFollowers(userId) {
      this.currentUserId = userId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'followers';
      this.getCurrentUser(userId);
    },
    showFollowing(userId) {
      this.currentUserId = userId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'following';
      this.getCurrentUser(userId);
    },
    showArticleDetail(articleId) {
      this.currentArticleId = articleId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'articleDetail';
    },
    showArticleFavorites(articleId) {
      this.currentFavoritesArticleId = articleId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'articleFavorites';
    },
    showArticleCommentUsers(articleId) {
      this.currentCommentArticleId = articleId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'articleCommentUsers';
    },
    showArticleLikeUsers(articleId) {
      this.currentLikeArticleId = articleId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'articleLikeUsers';
    },
    showArticleBrowsers(articleId) {
      this.currentBrowseArticleId = articleId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'articleBrowsers';
    },
    showUserComments(userId) {
      this.currentCommentUserId = userId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'userComments';
    },
    showUserLikedArticles(userId) {
      this.currentLikedArticleUserId = userId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'userLikedArticles';
    },
    showUserPublishedArticles(userId) {
      this.currentPublishedArticleUserId = userId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'userPublishedArticles';
    },
    showCommentReview(commentId) {
      this.currentCommentId = commentId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'commentReview';
    },
    showCommentLikeUsers(commentId) {
      this.currentCommentId = commentId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'commentLikeUsers';
    },
    showCommentReplies(commentId) {
      this.currentCommentId = commentId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'commentReplies';
    },
    showCommentDeatail(commentId) {
      this.currentCommentId_dataild = commentId;
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'CommentDeatail';
    },
    showUserInfo(userId) {
      this.currentUserId = userId;
      console.log('Received userId:', userId); // 确认 userId 是否正确传递
      this.previousView = this.currentView; // 记录来源页面
      this.currentView = 'userInfo';
    },
    handleBackToList() {
      if (this.previousView) {
        this.currentView = this.previousView;
        this.previousView = null;
      } else {
        // 如果没有记录来源页面，默认返回到首页或其他页面
        this.currentView = 'profile';
      }
    }
  }
}
</script>

<style scoped>
.dashboard-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #e0e7ef;
  display: flex;
  justify-content: flex-start;
  align-items: stretch;
  padding-left: 0;
}

.dashboard-container {
  display: flex;
  width: 100%;
  height: 100%;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(219, 11, 11, 0.1);
  background-color: #fff;
}

/* Sidebar 左侧栏 */
.sidebar {
  width: 260px;
  background-color: #2c3e50;
  color: white;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 内容区域 */
.dashboard-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: #f9fbfd;
  height: 100%;
}
</style>