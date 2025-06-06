<template>
  <HeaderBar @search="handleSearch" :initialKeyword="keyword" class="fixed-header-bar" />
  <div class="create-post-container">
    <div class="header-bar">
      <h1 class="page-title">博客创作</h1>
    </div>

    <div class="form-card privacy-toggle-section">
      <label for="isPrivateToggleInput">是否私密</label>
      <label class="switch">
        <input type="checkbox" id="isPrivateToggleInput" v-model="isPrivate" />
        <span class="slider"></span>
      </label>
    </div>
    <div class="form-card">
      <label for="title">标题</label>
      <input
        v-model="title"
        @input="titleError = false"
        :class="['input-field', titleError ? 'error' : '']"
        id="title"
        placeholder="请输入博客标题"
      />
      <p v-if="titleError" class="error-text">标题不能为空</p>
    </div>

    <div class="form-card">
      <label for="tags">标签</label>
      <input
        v-model="tags"
        id="tags"
        placeholder="用逗号分隔，如：前端,Vue,生活"
        class="input-field"
      />
    </div>

    <div class="form-card">
      <label>内容</label>
      <div class="editor-container" :class="{ error: contentError }">
        <Toolbar
          style="border-bottom: 1px solid #ccc"
          :editor="editorRef"
          :defaultConfig="toolbarConfig"
          mode="default"
        />
        <Editor
          style="height: 400px; overflow-y: auto"
          v-model="htmlContent"
          :defaultConfig="editorConfig"
          mode="default"
          @onCreated="handleCreated"
          @onChange="handleContentInput"
        />
      </div>
      <p v-if="contentError" class="error-text">内容不能为空</p>
    </div>

    <div class="button-group">
      <button class="publish-btn" @click="showDialog = true">ai辅助</button>
      <button class="publish-btn" @click="publishPost">发布</button>
    </div>

    <!-- AI 问答弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click.self="showDialog = false">
      <div class="dialog">
        <span class="close-icon" @click.stop="showDialog = false">&times;</span>
        <h2>🧠 AI 辅助创作</h2>

        <label for="question">💬 请输入问题：</label><br />
        <textarea
          v-model="question"
          id="question"
          placeholder="比如：请结合云南旅游写一篇博客"
        ></textarea
        ><br />

        <button @click="askGemini" :disabled="loading">提交问题</button>

        <h3>🤖 AI 的回答：</h3>
        <div id="response" style="white-space: pre-wrap">
          {{ response }}
          <button class="copy-icon-btn" @click="copyResponse" title="复制">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="20"
              height="20"
              fill="currentColor"
            >
              <path
                d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm-1 16H9v-12h9v12z"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, onBeforeUnmount } from 'vue'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import HeaderBar from '@/components/HeaderBar.vue'
const router = useRouter()

const title = ref('')
const tags = ref('')
const htmlContent = ref('')
const coverPreview = ref<string | null>(null)
let coverFile: File | null = null

const titleError = ref(false)
const contentError = ref(false)

const isPrivate = ref(false) // This existing ref will be used by the new toggle

const showDialog = ref(false)
const question = ref('')
const response = ref('')
const loading = ref(false)
const token = localStorage.getItem('token')

async function askGemini() {
  loading.value = true
  response.value = '⏳ 正在请求 AI 回复，请稍候...'
  try {
    // 这里写调用后端接口逻辑，示范：
    const res = await fetch('http://127.0.0.1:5000/article/aichat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ question: question.value }),
    })
    const data = await res.json()
    response.value = data.answer || 'AI 未返回有效内容'
  } catch (error) {
    response.value = '请求出错：' + error.message
  } finally {
    loading.value = false
  }
}

async function copyResponse() {
  const responseText = document.getElementById('response').innerText
  if (navigator.clipboard) {
    navigator.clipboard
      .writeText(responseText)
      .then(() => {
        // 可选：提供复制成功的提示
        alert('回答已复制到剪贴板！')
      })
      .catch((err) => {
        console.error('复制到剪贴板失败:', err)
        alert('复制失败，请手动选择文本进行复制。')
      })
  } else {
    // 如果浏览器不支持 navigator.clipboard，则提供备用方案（例如使用 textarea 选中并让用户手动复制）
    const textArea = document.createElement('textarea')
    textArea.value = responseText
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('回答已复制到剪贴板！')
  }
}

const editorRef = shallowRef()
const toolbarConfig = {}
const editorConfig = {
  placeholder: '请输入内容...',
  MENU_CONF: {
    uploadImage: {
      server: 'http://127.0.0.1:5000/upload/image', // 你的 Flask 上传图片接口
      fieldName: 'image',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
      customInsert(res: any, insertFn: Function) {
        // 后端返回的是 image_path: "/img/xxx.jpg"
        const imageUrl = res.image_path
        insertFn(imageUrl) // 直接插入到光标处
      },
    },
  },
}

function handleCoverUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    coverFile = file
    coverPreview.value = URL.createObjectURL(file)
  }
}

function handleCreated(editor: any) {
  editorRef.value = editor
}

function handleContentInput() {
  const html = editorRef.value?.getHtml() || ''
  if (html && html !== '<p><br></p>') {
    contentError.value = false
  }
}

onBeforeUnmount(() => {
  if (editorRef.value) {
    editorRef.value.destroy()
  }
})

async function publishPost() {
  if (!title.value.trim()) {
    titleError.value = true
    return
  }

  const html = editorRef.value?.getHtml() || ''
  if (!html || html === '<p><br></p>') {
    contentError.value = true
    return
  }

  const token = localStorage.getItem('token')
  if (!token) {
    alert('请先登录')
    router.push('/login')
    return
  }

  const formData = new FormData()
  formData.append('title', title.value)
  formData.append('content', html)
  formData.append('permission', isPrivate.value ? '1' : '0')
  formData.append('tag', tags.value.trim())
  // Append tags if you have a field for it in the backend and want to include it
  // formData.append('tags', tags.value);

  if (coverFile) {
    formData.append('cover', coverFile)
  }

  try {
    const response = await axios.post('http://127.0.0.1:5000/article/create', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        // axios 会自动设置 multipart/form-data 和边界
      },
    })

    alert('发布成功！')
    router.push('/')
  } catch (error: any) {
    if (error.response) {
      alert(error.response.data.message || '发布失败')
    } else {
      alert('网络错误或服务器异常')
    }
  }
}
</script>

<style scoped>
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
.create-post-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 16px;
  font-family: 'Helvetica Neue', sans-serif;
  background-color: #fff; /* Changed to #fff to match form-card background or make it distinct if preferred */
}

.header-bar {
  display: flex;
  justify-content: center; /* 让“博客创作”居中 */
  align-items: center;
  margin-bottom: 24px;
  position: relative;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  color: #333;
}

.form-card {
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* NEW STYLES FOR THE PRIVACY TOGGLE SECTION */
.privacy-toggle-section {
  flex-direction: row; /* Override .form-card's column direction */
  justify-content: space-between; /* "是否私密" label on left, switch on right */
  align-items: center; /* Vertically center items in the row */
}

/* Style for the text label "是否私密" within the new section */
.privacy-toggle-section > label[for='isPrivateToggleInput'] {
  margin-bottom: 0; /* Remove default bottom margin from general label style */
  /* display: block; is default for label, but flex item behavior will manage it */
}

/* Style for the switch component within the new section */
.privacy-toggle-section > .switch {
  margin-top: 0; /* Remove default top margin from general switch style */
}
/* END OF NEW STYLES */

label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: block;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-top: 6px;
  background-color: #f7f7f7;
  box-sizing: border-box;
}

.cover-preview {
  margin-top: 10px;
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.editor-container {
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
  margin-top: 6px;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 50px;
  margin-top: 30px;
}

.publish-btn {
  background: #2f80ed;
  color: #fff;
  padding: 12px 24px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.publish-btn:hover {
  background: #1c63d2;
}

.error {
  border: 1px solid #e74c3c !important;
  box-shadow: 0 0 5px rgba(231, 76, 60, 0.5);
}

.error-text {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 6px;
}

/* 响应式 */
@media (max-width: 600px) {
  .page-title {
    font-size: 22px;
  }
  .form-card {
    padding: 16px;
  }
  .publish-btn {
    width: 100%;
    text-align: center;
  }
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px; /* Adjusted for better visual balance with 28px height */
  height: 28px; /* Adjusted for better visual balance */
  /* margin-top: 8px; Removed as specific section will handle margins */
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 28px; /* Match height */
}
.slider:before {
  position: absolute;
  content: '';
  height: 20px; /* Smaller than slider height */
  width: 20px; /* Smaller than slider height */
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #4caf50; /* Green for checked */
}
input:checked + .slider:before {
  transform: translateX(
    22px
  ); /* (Switch width - knob width - 2*offset) = 50 - 20 - 2*4 = 22, or adjust as needed */
}
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6); /* 更深的半透明背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px); /* 添加模糊效果 */
}

.dialog {
  background-color: #f9f9f9; /* 更柔和的背景色 */
  padding: 30px; /* 增加内边距 */
  border-radius: 12px; /* 更圆润的边角 */
  width: 600px;
  max-width: 90%;
  max-height: 85vh; /* 稍微增加最大高度 */
  overflow-y: auto;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2); /* 更柔和的阴影 */
  animation: fadeIn 0.3s ease-out; /* 添加淡入动画 */
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h2 {
  color: #333; /* 深灰色标题 */
  margin-bottom: 20px;
  text-align: center;
  font-size: 24px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: bold;
}

textarea {
  width: calc(100% - 20px); /* 考虑内边距 */
  height: 100px; /* 稍微增加高度 */
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 16px;
  line-height: 1.5;
  box-sizing: border-box; /* 确保 padding 和 border 不撑大元素 */
}

button {
  padding: 12px 24px;
  cursor: pointer;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

button:disabled {
  background-color: #ddd !important;
  color: #888 !important;
  cursor: not-allowed;
}

button:not(:disabled):hover {
  opacity: 0.9;
}

.dialog > button:first-of-type {
  background-color: #5ea8da;
  color: white;
  padding: 6px 12px;
  margin: 15px auto 0 auto;
  display: block;
  font-size: 14px;
}
h3 {
  color: #333;
  margin-top: 25px;
  margin-bottom: 10px;
  font-size: 18px;
}

#response {
  background-color: #eee;
  border-radius: 6px;
  white-space: pre-wrap;
  font-size: 16px;
  line-height: 1.6;
  overflow-y: auto;
  max-height: 200px;
  position: relative; /* 使其内部元素可以相对于它定位 */
  padding: 15px;
  padding-right: 40px; /* 为图标预留空间 */
}

.close-icon {
  font-size: 24px;
  font-weight: bold;
  color: #888;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 5px;
  border-radius: 4px;
  line-height: 1;
  float: right;
}

.copy-icon-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  outline: none; /* 移除默认的焦点轮廓 */
}

.copy-icon-btn svg {
  fill: #777;
  width: 20px;
  height: 20px;
  transition: fill 0.2s ease;
}

.copy-icon-btn:hover svg {
  fill: #333;
}
</style>
