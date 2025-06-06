<template>
  <div class="register-container">
    <div class="register-card">
      <h2 class="title">欢迎注册 <span class="brand-name">NexTecht</span></h2>

      <!-- 头像上传 -->
      <div class="avatar-container" @click="triggerAvatarUpload">
        <div class="avatar-wrapper">
          <img
            :src="avatarUrl || defaultAvatar"
            alt="头像"
            class="avatar-img"
          />
          <div class="avatar-overlay">
            <svg class="upload-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
              <path d="M5 20h14v-2H5v2zm7-14l5 5h-3v4h-4v-4H7l5-5z"/>
            </svg>
          </div>
          <input type="file" ref="avatarInput" @change="handleAvatarChange" hidden />
        </div>
      </div>

      <!-- 表单内容 -->
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <input
            v-model="registerForm.nickname"
            :class="{ 'input-error': errors.nickname }"
            @input="errors.nickname = !registerForm.nickname.trim()"
            placeholder="用户名（必填）"
          />

          <input
            v-model="registerForm.password"
            type="password"
            :class="{ 'input-error': errors.password }"
            @input="errors.password = !registerForm.password.trim()"
            placeholder="密码（必填）"
          />

          <input
            v-model="registerForm.email"
            type="email"
            :class="{ 'input-error': errors.email }"
            @input="errors.email = !registerForm.email.trim()"
            placeholder="邮箱（必填）"
          />


          <!-- 性别下拉选择 -->
          <select v-model="registerForm.gender">
            <option value="" disabled>请选择性别</option>
            <option value="男">男</option>
            <option value="女">女</option>
          </select>

          <input
            v-model="registerForm.phone"
            :class="{ 'input-error': errors.phone }"
            @input="errors.phone = !registerForm.phone.trim()"
            placeholder="手机号（必填）"
          />

          <textarea v-model="registerForm.introduction" placeholder="个人介绍（选填）" rows="4" />
        </div>

        <button type="submit" class="register-button">注册</button>
      </form>

      <div class="footer">
        已有账号？<span class="login-link" @click="goToLogin">去登录</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const registerForm = ref({
  nickname: '',
  password: '',
  email: '',
  gender: '',
  phone: '',
  introduction: '',
  avatar: null as File | null,
})

const errors = reactive({
  nickname: false,
  password: false,
  email: false,
  phone: false, // 添加手机号错误状态
})


const avatarUrl = ref('')
const defaultAvatar = 'https://cdn-icons-png.flaticon.com/512/149/149071.png'


function triggerAvatarUpload() {
  const input = document.querySelector('input[type="file"]') as HTMLInputElement
  input?.click()
}

function handleAvatarChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) {
    registerForm.value.avatar = file
    avatarUrl.value = URL.createObjectURL(file)
  }
}

function validateForm() {
  errors.nickname = !registerForm.value.nickname.trim()
  errors.password = !registerForm.value.password.trim()
  errors.email = !registerForm.value.email.trim()
  errors.phone = !registerForm.value.phone.trim()
  return !errors.nickname && !errors.password && !errors.email && !errors.phone
}

async function handleRegister() {
  if (!validateForm()) return

  const formData = new FormData()
  formData.append('u_nickname', registerForm.value.nickname)
  formData.append('u_password', registerForm.value.password)
  formData.append('u_email', registerForm.value.email)
  formData.append('gender', registerForm.value.gender)
  formData.append('phone', registerForm.value.phone || '')
  formData.append('u_intro', registerForm.value.introduction || '')

  if (registerForm.value.avatar) {
    formData.append('avatar', registerForm.value.avatar)
  } else {
    // 告诉后端使用默认头像路径
    formData.append('use_default_avatar', 'true')
  }

  try {
    const response = await fetch('http://localhost:5000/user/register', {
      method: 'POST',
      body: formData,
    })

    const result = await response.json()
    if (result.state === 1) {
      alert('注册成功！')
      router.push('/login')
    } else {
      alert(result.message)
    }
  } catch (err) {
    console.error('注册失败:', err)
    alert('注册失败，请检查网络连接或联系管理员。')
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
</style>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #e0f7fa, #f1f8e9);
  font-family: 'Roboto', sans-serif;
}

.register-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  width: 360px;
  text-align: center;
}

.title {
  margin-bottom: 20px;
  font-size: 26px;
  color: #333;
}

.brand-name {
  font-family: 'Great Vibes', cursive;
  font-size: 28px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
}

.avatar-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #ddd;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.avatar-wrapper:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  opacity: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s ease;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.upload-icon {
  width: 32px;
  height: 32px;
  fill: white;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

input,
textarea,
select {
  padding: 10px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.5;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.3s;
}

.input-error {
  border-color: red;
}

textarea {
  resize: none;
}

.register-button {
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.footer {
  margin-top: 16px;
  color: #666;
  font-size: 14px;
}

.login-link {
  color: #007bff;
  cursor: pointer;
  margin-left: 5px;
}
</style>
