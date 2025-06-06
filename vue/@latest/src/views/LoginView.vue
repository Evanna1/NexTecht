<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">欢迎登录 <span class="brand-name">NexTecht</span></h2>

      <!-- 登录方式切换 -->
      <div class="login-tabs">
        <span :class="{ active: loginType === 'account' }" @click="loginType = 'account'">
          账号密码登录
        </span>
        <span :class="{ active: loginType === 'email' }" @click="loginType = 'email'">
          邮箱验证码登录
        </span>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleLogin">
        <div class="form-group" v-if="loginType === 'account'">
          <input v-model="loginForm.identifier" placeholder="用户名 / 手机号 / 邮箱" />
          <input v-model="loginForm.password" type="password" placeholder="密码" />
        </div>

        <div class="form-group" v-else>
          <input v-model="loginForm.email" placeholder="邮箱" />
          <div class="code-group">
            <input v-model="loginForm.code" placeholder="验证码" />
            <button type="button" @click="sendCode" :disabled="countdown > 0">
              {{ countdown > 0 ? `${countdown} 秒后重试` : '获取验证码' }}
            </button>

          </div>
        </div>

        <button type="submit" class="login-button">登录</button>
      </form>

      <div class="footer">
        没有账号？
        <span class="register-link" @click="goToRegister">去注册</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loginType = ref<'account' | 'email'>('account')

const loginForm = ref({
  identifier: '',
  password: '',
  email: '',
  code: '',
})

const countdown = ref(0)  // 倒计时秒数
let timer: number | null = null  // 定时器句柄

async function sendCode() {
  if (!loginForm.value.email) {
    alert('请输入邮箱地址')
    return
  }

  if (countdown.value > 0) {
    return  // 倒计时中，不重复发送
  }

  try {
    const response = await fetch('http://localhost:5000/user/sendEmailCode', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ u_email: loginForm.value.email }),
    })

    const result = await response.json()

    if (result.state === 1) {
      alert('验证码已发送，请查收邮箱')
      startCountdown()
    } else {
      alert(result.message)
    }
  } catch (err) {
    console.error('验证码发送失败', err)
    alert('服务器错误，请稍后重试')
  }
}

function startCountdown() {
  countdown.value = 60  // 60 秒
  timer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0 && timer !== null) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function handleLogin() {
  if (loginType.value === 'account') {
    const payload = {
      u_account: loginForm.value.identifier,
      u_password: loginForm.value.password,
    }

    try {
      const response = await fetch('http://localhost:5000/user/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const result = await response.json()

      if (result.state === 1) {
        localStorage.setItem('token', result.token)
        localStorage.setItem('avatar', result.avatar || '/img/default-avatar.png')
        localStorage.setItem('user_id', result.id)
        router.push('/')
      } else {
        alert(result.message)
      }
    } catch (err) {
      console.error('登录失败', err)
      alert('服务器错误，请稍后重试')
    }
  } else {
    const payload = {
      u_email: loginForm.value.email,
      code: loginForm.value.code,
    }

    try {
      const response = await fetch('http://localhost:5000/user/verifyEmailCode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const result = await response.json()

      if (result.state === 1) {
        localStorage.setItem('token', result.token)
        localStorage.setItem('avatar', result.avatar || '/img/default-avatar.png')
        localStorage.setItem('user_id', result.id)
        router.push('/')
      } else {
        alert(result.message)
      }
    } catch (err) {
      console.error('验证码登录失败', err)
      alert('服务器错误，请稍后重试')
    }
  }
}

function goToRegister() {
  router.push('/register')
}
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #e0f7fa, #f1f8e9);
  font-family: 'Roboto', sans-serif;
}

.login-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  width: 360px;
  text-align: center;
}

.title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

.brand-name {
  font-family: 'Great Vibes', cursive;
  font-size: 28px;
  font-weight: bold;
  color: #0077cc;
  text-decoration: none;
}


.login-tabs {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.login-tabs span {
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  color: #666;
}

.login-tabs .active {
  background-color: #007bff;
  color: white;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

input {
  padding: 10px;
  font-size: 14px;
  font-family: inherit;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
}

.code-group {
  display: flex;
  gap: 10px;
}

.code-group input {
  flex: 1;
}

.code-group button {
  padding: 8px 12px;
  font-size: 14px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.login-button {
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

.register-link {
  color: #007bff;
  cursor: pointer;
  margin-left: 5px;
}
</style>
