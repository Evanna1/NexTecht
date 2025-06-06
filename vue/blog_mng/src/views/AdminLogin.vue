<template>
  <div class="login-wrapper">
    <div class="login-container">
      <h2>管理员登录</h2>
      <div class="form-group">
        <input
          type="text"
          v-model="account"
          placeholder="账号 / 姓名 / 邮箱 / 电话"
        />
      </div>
      <div class="form-group">
        <input
          type="password"
          v-model="password"
          placeholder="密码"
        />
      </div>
      <button @click="handleLogin">登录</button>
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminLogin',
  data() {
    return {
      account: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async handleLogin() {
      if (!this.account || !this.password) {
        this.errorMessage = '请填写所有字段';
        return;
      }

      try {
        const response = await axios.post('http://localhost:5000/manager/login', {
          m_account: this.account,
          m_password: this.password
        });

        const data = response.data; // axios 自动解析 JSON

        if (data.state === 1) {
          localStorage.setItem('token', data.token);
          this.$router.push('/bashbord'); // 登录成功跳转后台
        } else {
          this.errorMessage = data.message;
        }
      } catch (error) {
        if (error.response && error.response.data && error.response.data.message) {
          this.errorMessage = `登录失败: ${error.response.data.message}`;
        } else {
          this.errorMessage = '登录失败，请稍后再试';
        }
      }
    }
  }
};
</script>

<style scoped>
body, html {
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #e0f2f7 0%, #b2ebf2 50%, #4dd0e1 100%); /* 接近您提供的蓝色系的渐变 */
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.login-wrapper {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  padding: 40px;
  width: 90vw;
  max-width: 420px;
  text-align: center;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.login-container {
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.login-container h2 {
  color: #5ea8da; /* 您提供的蓝色 */
  margin-bottom: 35px;
  font-size: 2.2em;
  font-weight: 500;
}

.form-group {
  margin-bottom: 25px;
}

input {
  width: calc(100% - 24px);
  padding: 14px;
  border: 1px solid #80deea; /* 接近的浅蓝色边框 */
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s, box-shadow 0.3s;
  box-sizing: border-box;
  outline: none;
}

input:focus {
  border-color: #5ea8da; /* 您提供的蓝色作为焦点颜色 */
  box-shadow: 0 0 8px rgba(94, 168, 218, 0.4); /* 蓝色焦点阴影 */
}

button {
  padding: 16px;
  font-size: 18px;
  background-color: #5ea8da; /* 您提供的蓝色作为按钮背景 */
  color: #ffffff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

button:hover {
  background-color: #4c8bb7; /* 稍微深一点的 hover 效果 */
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.1);
}

.error-message {
  color: #f44336;
  margin-top: 25px;
  font-size: 14px;
  text-align: center;
}
</style>