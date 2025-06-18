<template>
  <div class="main-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <h2>code 生成</h2>
      </div>
    </el-header>

    <!-- 主体内容区 -->
    <el-main class="content" ref="contentContainer">
      <div class="messages-container" ref="messagesContainer">
        <div v-for="message in messages" :key="message.chatID" class="message-wrapper" :class="message.type">
          <!-- AI消息 -->
          <div v-if="message.type === 'ai'" class="message ai-message">
            <!-- <div class="avatar">
              <el-avatar :size="40" :src="aiAvatarUrl"></el-avatar>
            </div> -->
            <div class="message-content">
              <div v-if="message.isTyping" class="typing-content">{{ message.renderedContent }}<span class="typing-cursor">|</span></div>
              <div v-else class="markdown-content" v-html="message.renderedContent"></div>
            </div>
          </div>

          <!-- 用户消息 -->
          <div v-else class="message user-message">
            <div class="message-content">
              <!-- 文本内容 -->
              <div v-if="message.content" style="text-align: left">{{ message.content }}</div>

              <!-- 文件信息 -->
              <div v-if="message.file" class="file-info">
                <!-- PDF文件图标 -->
                <el-icon v-if="message.file.name.toLowerCase().endsWith('.pdf')" class="file-icon pdf-icon">
                  <svg t="1749903285303" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="918" width="1em" height="1em">
                    <path d="M704 0H192c-35.328 0-64 28.672-64 64v320h576c35.328 0 64 28.672 64 64v415.744c0 35.328-28.672 64-64 64H128v31.744c0 35.328 28.672 64 64 64h768c35.328 0 64-28.672 64-64v-640L704 0z" fill="#EAEAEA" p-id="919"></path>
                    <path d="M704 0v256c0 35.328 28.672 64 64 64h256L704 0z" fill="#434854" p-id="920"></path>
                    <path d="M768 320l256 256V320z" opacity=".1" p-id="921"></path>
                    <path d="M704 832c0 17.92-14.336 31.744-31.744 31.744H31.744C13.824 863.744 0 849.408 0 832V480.256c0-17.92 14.336-31.744 31.744-31.744h640c17.92 0 31.744 14.336 31.744 31.744V832z" fill="#CD4050" p-id="922"></path>
                    <path
                      d="M192 544.256h-48.128c-8.704 0-15.872 7.168-15.872 15.872v192c0 8.704 7.168 15.872 15.872 15.872s15.872-7.168 15.872-15.872v-79.872h31.744c35.328 0 64-28.672 64-64s-28.16-64-63.488-64z m158.72 0c34.816 0 62.976 27.648 64 62.464v97.792c0 34.816-27.648 62.976-62.464 64h-49.664c-8.704 0-15.36-6.656-15.872-14.848V560.64c0-8.704 6.656-15.36 14.848-15.872h49.152z m227.328 0c8.704 0 15.872 7.168 15.872 15.872S586.752 576 578.048 576h-80.384v64h48.128c8.704 0 15.872 7.168 15.872 15.872s-7.168 15.872-15.872 15.872h-48.128v79.872c0 8.704-7.168 15.872-15.872 15.872s-15.872-7.168-15.872-15.872v-192c0-8.704 7.168-15.872 15.872-15.872h96.256zM350.72 576h-31.744v159.744h31.744c17.408 0 31.232-13.824 31.744-30.72v-97.28C382.976 590.336 368.64 576 350.72 576zM192 576c17.92 0 31.744 14.336 31.744 31.744S209.92 640 192 640h-31.744v-64H192z"
                      fill="#FFFFFF"
                      p-id="923"
                    ></path>
                  </svg>
                </el-icon>

                <!-- Word文件图标 -->
                <el-icon v-else-if="message.file.name.toLowerCase().endsWith('.doc') || message.file.name.toLowerCase().endsWith('.docx')" class="file-icon word-icon">
                  <svg t="1749904882056" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1069" width="200" height="200">
                    <path
                      d="M535.119473 0h69.599248v95.247413C729.226717 96.331138 853.614299 93.92286 977.881468 96.331138a40.459078 40.459078 0 0 1 44.914393 45.516463c2.047037 234.566322 0 469.614299 1.204139 703.819379-1.204139 24.082785 2.287865 50.694262-11.318909 72.248354-16.978363 12.041392-38.893697 10.837253-58.761994 12.041392h-349.200376V1023.518344h-72.248354C354.980245 990.886171 177.490122 960.541863 0 928.752587V95.488241C178.33302 63.578551 356.786453 32.511759 535.119473 0z"
                      fill="#2A5699"
                      p-id="1070"
                    ></path>
                    <path
                      d="M604.718721 131.010348H988.598307v761.979304H604.718721v-95.247413h302.479774v-48.165569H604.718721v-59.002822h302.479774v-48.16557H604.718721v-59.002822h302.479774v-48.165569H604.718721v-60.206961h302.479774V428.673565H604.718721v-60.206961h302.479774v-46.96143H604.718721v-59.604892h302.479774V214.336783H604.718721zM240.827846 341.373471c22.156162-1.324553 44.19191-2.287865 66.348071-3.492003 15.533396 80.4365 31.30762 160.632173 48.165569 240.827845 13.125118-82.724365 27.695202-165.087488 41.783632-247.571025 23.239887-0.842897 46.479774-2.167451 69.719661-3.612418-26.370649 115.356538-49.369708 231.796802-78.148636 346.430856-19.386642 10.355597-48.165569 0-71.52587 1.204139C301.034807 596.169332 283.093133 517.779868 269.245532 438.667921c-13.606773 76.944497-31.30762 153.16651-46.841016 229.508937-22.39699-1.204139-44.793979-2.528692-67.311383-4.094073-19.266228-104.760113-42.024459-208.918156-60.206962-313.919097 19.868297-0.963311 39.857008-1.806209 60.206962-2.528693 12.041392 75.860771 25.648166 151.360301 36.124177 227.341487 16.135466-77.907808 32.873001-155.695202 49.610536-233.603011z"
                      fill="#FFFFFF"
                      p-id="1071"
                    ></path>
                  </svg>
                </el-icon>

                <!-- Json文件图标 -->
                <el-icon v-else-if="message.file.name.toLowerCase().endsWith('.json')" class="file-icon word-icon">
                  <svg t="1750133134363" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4389" width="200" height="200">
                    <path d="M707.2 79.9H238.6c-11.6 0-21 9.4-21 21V923c0 11.6 9.4 21 21 21h704.9V316.3L707.2 79.9" fill="#FFFFFF" p-id="4390"></path>
                    <path d="M943.6 960h-705c-20.4 0-37-16.6-37-37V100.9c0-20.4 16.6-37 37-37h468.6c4.2 0 8.3 1.7 11.3 4.7L954.9 305c3 3 4.7 7.1 4.7 11.3V944c0 8.9-7.2 16-16 16z m-705-864.1c-2.7 0-5 2.2-5 5V923c0 2.7 2.2 5 5 5h689V323l-227-227h-462z" fill="#00365B" p-id="4391"></path>
                    <path d="M943.6 316.3H707.2V79.9z" fill="#FFFFFF" p-id="4392"></path>
                    <path d="M943.6 332.3H707.2c-8.8 0-16-7.2-16-16V79.9c0-6.5 3.9-12.3 9.9-14.8s12.9-1.1 17.4 3.5L954.9 305c4.6 4.6 5.9 11.5 3.5 17.4-2.5 6-8.3 9.9-14.8 9.9z m-220.4-32H905L723.2 118.6v181.7z" fill="#00365B" p-id="4393"></path>
                    <path d="M104.7 414.2h698.8c22.4 0 40.6 19.8 40.6 44.3v301.4c0 24.5-18.2 44.3-40.6 44.3H104.7c-22.4 0-40.6-19.8-40.6-44.3V458.5c-0.1-24.5 18.1-44.3 40.6-44.3z" fill="#E89870" p-id="4394"></path>
                    <path
                      d="M164.4 722.3c7.3 0 14-0.9 19.9-2.6s10.9-4.5 15-8.4c4.1-3.9 7.2-9 9.3-15.4 2.1-6.4 3.2-14.2 3.2-23.4V515.8c0-4.1-1.5-7.7-4.6-11-3.1-3.3-8.2-4.9-15.3-4.9-7.1 0-12.2 1.7-15.3 5.2-3.1 3.5-4.6 7-4.6 10.7V655c0 6.1-0.1 11.3-0.2 15.4-0.1 4.2-0.6 7.5-1.4 9.9-0.8 2.4-2.1 4.2-3.8 5.4s-4.2 1.7-7.5 1.7c-4.1 0-7.6-1.3-10.7-3.8-3.1-2.5-6-4.9-8.9-7.2-2.7-2-5.3-3.1-7.8-3.2-2.5-0.1-4.9 0.3-7.2 1.1-2.2 0.8-4.2 1.9-5.8 3.4-1.6 1.4-2.8 2.7-3.4 3.7-2 3.3-2.8 6.5-2.3 9.8s1.8 6.3 3.8 9.2c2 2.9 4.5 5.5 7.3 8 2.9 2.4 5.7 4.5 8.6 6.1 4.7 2.9 9.5 4.9 14.4 6.1 5.1 1.1 10.8 1.7 17.3 1.7z m115.8-4.8c8.1 2.5 16.7 3.6 25.8 3.2 25.1-0.8 43.7-7.4 56-19.7 12.2-12.3 18.6-28.6 19-48.8 0.2-7.5-0.7-14.3-2.6-20.2s-5.1-11.2-9.5-15.9c-4.4-4.7-9.9-9.1-16.7-13.2-6.7-4.1-14.7-8.2-23.9-12.2-3.7-1.6-7.8-3.4-12.4-5.2-4.6-1.8-9-4.1-13.2-6.7s-7.7-5.7-10.6-9.2c-2.9-3.5-4.3-7.5-4.3-12.2 0-2.9 0.6-5.8 1.8-8.7 1.2-3 2.9-5.6 5-8 2.1-2.3 4.7-4.3 7.8-5.8 3.1-1.5 6.5-2.3 10.4-2.3 3.5 0 6.9 0.5 10.2 1.5 3.4 1 6.5 2.2 9.5 3.7 3 1.4 5.8 3 8.4 4.7 2.7 1.7 5 3.3 7 4.7 1.4 1.2 3.3 2 5.5 2.4 2.2 0.4 4.5 0.4 6.9-0.2 2.3-0.5 4.6-1.4 6.7-2.8 2.1-1.3 3.9-3.1 5.4-5.4 2.7-4.5 3-9.2 1.1-14.2s-5.6-9.6-11-13.9c-5.4-4.3-12.2-7.9-20.3-10.7-8.2-2.9-17-4.4-26.6-4.6-8.6-0.2-17 0.9-25.2 3.4-8.3 2.4-15.7 6.1-22.2 11s-11.8 11.1-15.8 18.5-6 16.1-6 25.8c0 9.2 1.6 17.1 4.9 23.9 3.3 6.7 7.6 12.5 13.2 17.4 5.5 4.9 12 9.1 19.4 12.7 7.4 3.6 15.4 6.9 24 9.9 3.1 1 6.5 2.4 10.2 4.3 3.8 1.8 7.2 4.1 10.4 6.9 3.2 2.8 5.9 6 8.1 9.6 2.2 3.7 3.4 8 3.4 12.8 0 5.1-0.9 9.6-2.8 13.6-1.8 4-4.3 7.3-7.3 9.9-3.1 2.7-6.6 4.7-10.6 6.1-4 1.4-8 2.1-12.1 2.1-4.9 0-9.4-0.6-13.6-1.8-4.2-1.2-8.2-2.8-11.9-4.7-3.8-1.9-7.3-4.1-10.7-6.4-3.4-2.3-6.6-4.5-9.6-6.6-3.5-2.2-7.2-3.1-11.2-2.6-4 0.5-7.4 3-10.2 7.5-1.6 2.2-2.5 5-2.6 8.3-0.1 3.3 0.6 6.6 2 10.1s3.7 6.9 6.9 10.2c3.2 3.4 7.4 6.4 12.7 9 6.1 3.5 13.1 6.3 21.2 8.8z m216.7 4.8c16.5 0 30.8-2.9 43-8.7 12.1-5.8 22.2-13.8 30.1-23.9 8-10.1 13.9-22 17.7-35.8 3.9-13.8 5.8-28.6 5.8-44.5 0-15.9-1.9-30.7-5.8-44.4s-9.8-25.5-17.7-35.6c-8-10.1-18-18-30.1-23.9-12.1-5.8-26.5-8.7-43-8.7-17.1 0-31.8 2.9-43.9 8.7s-22.1 13.8-30 23.9c-7.9 10.1-13.6 22-17.3 35.8-3.7 13.8-5.5 28.5-5.5 44.2 0 16.3 2 31.4 6.1 45.3s10.2 25.8 18.4 35.8c8.2 10 18.3 17.8 30.3 23.4 12 5.6 26 8.4 41.9 8.4z m0-34.9c-10.8 0-19.8-2.2-27.1-6.7-7.2-4.5-13.1-10.4-17.6-17.7-4.5-7.3-7.6-15.7-9.5-25.1-1.8-9.4-2.8-18.9-2.8-28.4 0-10.6 1-20.6 3.1-30 2-9.4 5.3-17.6 9.8-24.6 4.5-7 10.3-12.6 17.6-16.8 7.2-4.2 16.1-6.3 26.5-6.3s19.2 2 26.5 6.1 13.1 9.7 17.6 16.8 7.7 15.5 9.8 25.1c2 9.6 3.1 19.8 3.1 30.6s-0.9 20.9-2.8 30.3c-1.8 9.4-5 17.5-9.5 24.5-4.5 6.9-10.3 12.4-17.6 16.4-7.3 3.8-16.3 5.8-27.1 5.8z m281.4 31.8c7.1 0 11.7-1.4 13.8-4.3 2-2.9 3.1-6 3.1-9.5V515.8c0-4.1-1.5-7.7-4.6-11-3.1-3.3-8.2-4.9-15.3-4.9-7.1 0-12.2 1.7-15.3 5.2-3.1 3.5-4.6 7-4.6 10.7v125.1l-96.7-130c-1.8-2.4-4-4.9-6.6-7.3-2.5-2.4-5.9-3.7-9.9-3.7-7.3 0-12 1.5-14.1 4.4-2 3-3.1 6.3-3.1 9.9v189c0 3.7 1.5 7.2 4.6 10.7 3.1 3.5 8.2 5.2 15.3 5.2 7.1 0 12.2-1.6 15.3-4.9s4.6-6.9 4.6-11V582.5l96.4 125.7c1.8 2.4 4.1 4.9 6.9 7.3 2.7 2.5 6.1 3.7 10.2 3.7z"
                      fill="#FFFFFF"
                      p-id="4395"
                    ></path>
                  </svg>
                </el-icon>

                <!-- 其他文件图标 -->
                <el-icon v-else class="file-icon">
                  <svg t="1749904946815" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2191" width="200" height="200">
                    <path d="M170.2 246.4h342.1s44.2-77.8 89.1-77.8h254.9c20.7 0 37.7 19.8 37.7 44l1.1 598.1c0 24.2-19.8 44-44 44h-681c-24.2 0-44-19.8-44-44V290.4c0.1-24.2 19.9-44 44.1-44z" fill="#694B4B" p-id="2192"></path>
                    <path d="M862.9 671.5l-688 38.3-22.2-406.4 688.1-59.3z" fill="#593F3F" p-id="2193"></path>
                    <path d="M870.8 671.8L242.2 707l-21.1-388 634.6-35.2z" fill="#593F3F" p-id="2194"></path>
                    <path d="M840.7 673.7L218.1 725l-21.9-383.4 623.4-55.9z" fill="#FFFFFF" p-id="2195"></path>
                    <path d="M807.9 715.1L178.6 750l-22.2-406.3 629.7-48.1z" fill="#F2F2F1" p-id="2196"></path>
                    <path d="M796 713.5l-619 36.3-22.1-406.3 618.8-40.1z" fill="#FFFFFF" p-id="2197"></path>
                    <path d="M895.2 425.1H509.1s-44.2-71.4-89.1-71.4H125.1c-20.7 0-38.9 16.3-38.9 36l40 429.2c0 19.7 19.8 35.8 44 35.8h685c24.2 0 44-16.1 44-35.8l40-358c0-19.7-19.8-35.8-44-35.8z" fill="#00B5FC" p-id="2198"></path>
                  </svg>
                </el-icon>

                <span>{{ message.file.name }}</span>
              </div>
            </div>
            <div class="avatar">
              <el-avatar :size="40" icon="el-icon-user" :src="aiAvatarUrl"></el-avatar>
            </div>
          </div>
        </div>
      </div>
    </el-main>

    <!-- 底部输入区域 -->
    <el-footer class="footer">
      <div class="button-area">
        <el-button class="model-btn" plain circle large v-if="showScrollToBottomBtn" @click="scrollToBottom">
          <el-icon><arrow-down /></el-icon>
        </el-button>
      </div>

      <Input @send="sendMessage" :disabled="isSending"></Input>
    </el-footer>
  </div>
</template>

<script setup>
import Input from '../components/Input.vue'
import { ref, nextTick, onMounted, reactive, onUnmounted } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import axios from '../utils/service'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 配置 marked
const renderer = new marked.Renderer()
renderer.code = function (codeObject) {
  let lang = codeObject.lang
  let code = codeObject.text
  // console.log('codeObject:', codeObject) // 输出 code 内容
  // console.log('Code:', code) // 输出 code 内容
  // console.log('Lang:', lang) // 输出 lang 内容
  if (typeof code !== 'string') {
    // 非字符串类型转换为字符串
    code = code ? String(code) : ''
  }
  const language = lang || 'text'
  const validLang = hljs.getLanguage(language) ? language : 'text'

  try {
    // 添加try-catch防止意外错误
    const highlighted = hljs.highlight(code, { language: validLang }).value
    return `<pre data-lang="${language}"><code class="hljs language-${validLang}">${highlighted}</code></pre>`
  } catch (e) {
    console.error('代码高亮失败:', e)
    // 出错时返回原始代码
    return `<pre><code>${code}</code></pre>`
  }
}

marked.setOptions({
  renderer: renderer,
  breaks: true,
  gfm: true,
  pedantic: false,
  smartLists: true,
  smartypants: false
})

const messages = ref([])
// const inputText = ref('')
// const selectedFile = ref(null)
const messagesContainer = ref(null)
const contentContainer = ref(null)
const fileInput = ref(null)
const aiAvatarUrl = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')
const isSending = ref(false)
// 处理文件选择
const handleFileSelect = event => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}
// 移除选中的文件
const removeFile = () => {
  selectedFile.value = null
  fileInput.value.value = ''
}
// 控制滚动按钮的显示
const showScrollToBottomBtn = ref(false)
// 滚动到底部（增强版）
const scrollToBottom = () => {
  nextTick(() => {
    if (!contentContainer.value) {
      console.warn('滚动容器未初始化')
      return
    }
    const container = contentContainer.value?.$el || contentContainer.value
    // 确保容器存在
    if (!container) {
      console.warn('滚动容器未找到')
      return
    }

    // 确保滚动高度有效
    if (container.scrollHeight <= 0) {
      console.warn('无效的滚动高度')
      return
    }

    if (typeof container.scrollTo === 'function') {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      })
    } else {
      // 直接设置scrollTop（无平滑效果）
      container.scrollTop = container.scrollHeight
    }

    // 滚动完成后隐藏按钮
    setTimeout(() => {
      showScrollToBottomBtn.value = false
    }, 500)
  })
}
// 监听滚动事件，检查是否在底部
const checkScrollPosition = () => {
  nextTick(() => {
    const container = contentContainer.value?.$el || contentContainer.value
    if (!container) return

    // 计算是否在底部（留50px缓冲）
    const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight <= 50

    // 如果不在底部，显示滚动按钮
    showScrollToBottomBtn.value = !isAtBottom
  })
}

// 打字机效果
const typeWriter = (message, text, speed = 30) => {
  return new Promise(resolve => {
    if (!text) {
      return Promise.resolve()
    }
    // console.log('text:', text)
    let i = 0
    message.displayContent = message.displayContent ? message.displayContent : ''
    message.isTyping = false

    // 节流相关变量
    let lastRenderTime = 0
    const renderInterval = 100 // 最小渲染间隔100ms
    let lastContent = ''

    // const renderContent = () => {
    //   const now = Date.now()

    //   // 节流检查：如果内容有变化且超过最小间隔时间才渲染
    //   if (message.displayContent !== lastContent && now - lastRenderTime >= renderInterval) {
    //     try {
    //       message.renderedContent = marked(message.displayContent)
    //     } catch (e) {
    //       console.error('Markdown渲染错误:', e)
    //       message.renderedContent = message.displayContent
    //     }
    //     lastContent = message.displayContent
    //     lastRenderTime = now
    //   }
    // }
    const timer = setInterval(() => {
      if (i < text.length) {
        message.displayContent += text.charAt(i)
        i++
        // 调用节流渲染
        // renderContent()
        // 实时渲染Markdown格式
        try {
          message.renderedContent = marked(message.displayContent)
        } catch (e) {
          console.error('Markdown渲染错误:', e)
          message.renderedContent = message.displayContent
        }
        // 定期滚动到最新内容
        if (i % 10 === 0) scrollToBottom()
        //scrollToBottom()
      } else {
        clearInterval(timer)
        message.isTyping = false
        //console.log('marked ', text)
        // message.renderedContent = marked(text)
        // 确保最终内容被渲染
        try {
          message.renderedContent = marked(message.displayContent)
        } catch (e) {
          console.error('Markdown渲染错误:', e)
          message.renderedContent = message.content
        }
        scrollToBottom() // 完成时滚动一次
        resolve()
      }
    }, speed)
  })
}
const sleep = seconds => {
  return new Promise(resolve => setTimeout(resolve, seconds))
}
const generateRandomFolderName = (length = 8, prefix = 'agent_') => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let result = ''

  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }

  return `${prefix + result}`
}
// 生成唯一 chatID 的函数
const generateUniqueChatID = (length = 8, prefix = 'agent_') => {
  const existingIDs = new Set(messages.value.map(msg => msg.chatID))
  let newID

  do {
    newID = generateRandomFolderName(length, prefix)
  } while (existingIDs.has(newID))

  return newID
}

// 发送文件的辅助函数
const sendFile = (file, baseData) => {
  return new Promise(resolve => {
    const reader = new FileReader()

    reader.onload = () => {
      // 将文件内容转换为Base64
      const base64Data = reader.result.split(',')[1]
      const extension = file.name.split('.').pop()
      // 构建完整消息
      const fileData = {
        ...baseData,
        fileSize: file.size,
        fileType: file.type,
        fileExtension: extension,
        fileOriginName: file.name,
        fileData: base64Data
      }

      // 通过WebSocket发送
      ws.value.send(JSON.stringify(fileData))
      resolve()
    }

    reader.onerror = error => {
      ElMessage({ type: 'error', message: `文件读取失败: ${error}` })
      resolve()
    }

    // 读取文件内容
    reader.readAsDataURL(file)
  })
}

// 发送消息
const sendMessage = async (inputText, selectedFile) => {
  if (!inputText.trim() && !selectedFile) {
    ElMessage({
      type: 'warning',
      message: '请输入内容或选择文件'
    })
    return
  }
  if (!ws.value) {
    ElMessage({
      type: 'error',
      message: '未能与服务器取得连接'
    })
    return
  }
  console.log('发送消息:', inputText)
  console.log('发送文件:', selectedFile)

  isSending.value = true // 设置发送状态
  // 添加用户消息
  const userMessage = reactive({
    type: 'user',
    content: inputText,
    file: selectedFile ? { name: selectedFile.name } : null,
    timestamp: new Date(),
    chatID: Date.now().toLocaleString()
  })
  messages.value.push(userMessage)
  const chatID = generateUniqueChatID()
  // const chatID = 'agentfiles'
  const fileName = generateRandomFolderName(8, chatID)
  let sendData = {
    sessionID,
    chatID
  }
  if (inputText.trim() && selectedFile) {
    sendData.type = 'all'
    sendData.text = inputText
    sendData.fileName = fileName
    await sendFile(selectedFile, sendData)
  } else if (inputText.trim()) {
    sendData.type = 'text'
    sendData.text = inputText
    ws.value.send(JSON.stringify(sendData))
  } else {
    // 只有文件
    sendData.type = 'file'
    sendData.fileName = fileName
    await sendFile(selectedFile, sendData)
  }
  scrollToBottom()
}
const judgeLang = extension => {
  const langMap = {
    py: 'python',
    js: 'javascript',
    java: 'java',
    go: 'go',
    cpp: 'cpp'
    // 添加更多映射...
  }
  return langMap[extension] || extension
}

// Websocket通知处理
const callReceiveNotice = async data => {
  console.log('callReceiveNotice', data)
  const existingNoticeIndex = messages.value.findIndex(msg => msg.notice === true && msg.chatID === 'notice' + data.chatID)
  if (existingNoticeIndex !== -1) {
    console.log('更新通知前：', messages.value[existingNoticeIndex])
    messages.value[existingNoticeIndex].content = messages.value[existingNoticeIndex].content + '完成！\n' + data.message
    await typeWriter(messages.value[existingNoticeIndex], '完成！\n' + data.message)
    scrollToBottom()
    console.log('更新通知后：', messages.value[existingNoticeIndex])
  } else {
    const noticeMsg = reactive({
      type: 'ai',
      notice: true,
      chatID: 'notice' + data.chatID,
      fileList: [],
      content: data.message,
      displayContent: '',
      renderedContent: '',
      isTyping: true,
      timestamp: new Date()
    })
    messages.value.push(noticeMsg)
    await typeWriter(noticeMsg, noticeMsg.content)
    scrollToBottom()
  }
}
const removeNotice = async chatID => {
  const existingNoticeIndex = messages.value.findIndex(msg => msg.notice === true && msg.chatID === 'notice' + chatID)
  if (existingNoticeIndex !== -1) {
    // console.log('移除通知前：', messages.value[existingNoticeIndex])
    messages.value[existingNoticeIndex].content = messages.value[existingNoticeIndex].content + '完成！\n'
    await typeWriter(messages.value[existingNoticeIndex], '完成！\n')
    scrollToBottom()
    await sleep(800)
    // console.log('移除通知后：', messages.value[existingNoticeIndex])
  }
  messages.value = messages.value.filter(msg => !msg.notice)
}
// Websocket消息处理
const callReceiveText = async data => {
  console.log('callReceiveText messages:', messages.value)
  isSending.value = true
  let content = data.content,
    lang = judgeLang(data.extension),
    fileName = data.name,
    fileIndex = data.index,
    chatID = data.chatID,
    fileSum = data.fileSum
  if (data.extension != 'md') {
    content = `  **\`${fileName}\`** 文件如下:
\`\`\`${lang}
${content}
\`\`\`
    `
  }
  if (fileSum == 1) {
    // 只有一个文件
    removeNotice(chatID)
    const aiMessage = reactive({
      type: 'ai',
      notice: false,
      fileList: [
        {
          extension: data.extension,
          content: content,
          fileName,
          fileIndex,
          fileSum
        }
      ], // [{extension:'md',content:'# 123'}] --> md文件一定要第一个渲染
      displayContent: '',
      renderedContent: '',
      isTyping: true,
      timestamp: new Date(),
      chatID
    })
    messages.value.push(aiMessage)
    await typeWriter(aiMessage, aiMessage.fileList[0].content)
    scrollToBottom()
    isSending.value = false
  } else if (fileIndex == 0) {
    // 第一个文件
    // 添加 AI 消息占位符
    removeNotice(chatID)
    console.log('第一个文件')
    const aiMessage = reactive({
      type: 'ai',
      notice: false,
      fileList: [
        {
          extension: data.extension,
          content: content
        }
      ],
      displayContent: '',
      renderedContent: '',
      isTyping: true,
      timestamp: new Date(),
      chatID
    })
    messages.value.push(aiMessage)
  } else if (fileIndex != fileSum - 1) {
    // 中间文件
    console.log('中间文件')
    const aiMsg = messages.value.find(item => item.chatID === chatID)
    aiMsg.fileList.push({
      extension: data.extension,
      content: content
    })
  } else {
    console.log('最后一个文件')
    const aiMsg = messages.value.find(item => item.chatID === chatID)
    aiMsg.fileList.push({
      extension: data.extension,
      content: content
    })
    // console.log('排序前', aiMsg.fileList)
    // 创建排序后的文件列表
    const sortedFiles = []
    // 先添加 md 文件
    aiMsg.fileList.forEach(file => {
      if (file.extension.toLowerCase() === 'md') {
        sortedFiles.push(file)
      }
    })
    // 再添加其他文件
    aiMsg.fileList.forEach(file => {
      if (file.extension.toLowerCase() !== 'md') {
        sortedFiles.push(file)
      }
    })
    aiMsg.fileList = sortedFiles
    // console.log('排序后', aiMsg.fileList)

    let newContent = ''
    aiMsg.fileList.forEach(file => {
      if (file.extension != 'md') {
        newContent = newContent + '\n' + file.content
      } else {
        newContent += file.content
      }
    })
    await typeWriter(aiMsg, newContent)
    scrollToBottom()
    isSending.value = false
  }
}
// Websocket 连接
const ws = ref(null)
const sessionID = generateRandomFolderName() // 'agent'
const wsConnectRegister = () => {
  ws.value = new WebSocket(`ws://localhost:8080/ws`)
  ws.value.onopen = () => {
    //连接过程
    ws.value.send(
      JSON.stringify({
        sessionID
      })
    )
  }
  // 接收Websocket消息
  ws.value.onmessage = e => {
    let data = JSON.parse(e.data)
    if (data.type == 'data') {
      callReceiveText(data)
    } else if (data.type == 'notice') {
      callReceiveNotice(data)
    } else if (data.type == 'file_ack') {
      ElMessage({
        type: 'success',
        message: data.fileOriginName + '上传成功'
      })
    } else if (data.type == 'error') {
      console.log('Received error:', data.message)
      ElMessage({
        type: 'error',
        message: data.message
      })
    }
    // console.log('Received ', data)
  }
  ws.value.onerror = error => {
    console.error('WebSocket error:', error)
    ElMessage({
      type: 'error',
      message: 'WebSocket 连接失败，请检查服务器地址和端口是否正确'
    })
  }
}

// 组件挂载时的初始化
onMounted(async () => {
  // Websocket连接
  wsConnectRegister()
  // 添加欢迎消息
  const welcomeMessage = reactive({
    type: 'ai',
    content: '您好！我是您的 AI 助手，输入您的策略，我会帮您生成代码', // 确保content有值
    displayContent: '',
    renderedContent: '',
    isTyping: true,
    timestamp: new Date()
  })
  messages.value.push(welcomeMessage)

  // 确保DOM更新后再开始打字机效果

  await typeWriter(welcomeMessage, welcomeMessage.content) // 使用welcomeMessage.content作为打字机文本

  const container = contentContainer.value?.$el || contentContainer.value
  if (container) {
    container.addEventListener('scroll', checkScrollPosition)
    console.log('绑定')
    // 初始检查滚动位置
    checkScrollPosition()
  }
})

// 组件卸载时移除监听
onUnmounted(() => {
  const container = contentContainer.value?.$el || contentContainer.value
  if (container) {
    container.removeEventListener('scroll', checkScrollPosition)
  }
})
</script>

<style lang="less" scoped>
.main-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  width: 100vw;
  height: 100vh;
  display: flex; /* 新增：设置为flex容器 */
  flex-direction: column; /* 新增：子元素垂直排列 */
  .header {
    background-color: #ffffff;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    padding: 0 60px;
    display: flex;
    align-items: center;
    height: 60px;
    z-index: 10;

    .header-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;

      h2 {
        margin: 0;
        color: #333;
        font-weight: 500;
      }
    }
  }
  .content {
    flex: 1;
    display: flex;
    align-items: center;
    display: flex;
    flex-direction: column;
    z-index: 999;
    padding-bottom: 0;
    overflow-y: auto;
    .messages-container {
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding-bottom: 20px;
      max-width: 1200px;
      width: 100%;
      overflow-y: visible;
      max-height: none;
      padding: 20px 15px 100px 15px;
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
      .message-wrapper {
        display: flex;
        width: 100%;

        &.ai {
          justify-content: flex-start;
        }

        &.user {
          justify-content: flex-end;
        }

        .message {
          width: 100%;
          display: flex;
          align-items: flex-start;

          .avatar {
            margin: 0 10px;
          }

          .message-content {
            padding: 12px 16px;
            border-radius: 8px;
            word-break: break-word;
          }
        }

        .ai-message {
          .message-content {
            background-color: #ffffff;
            color: #333;
            text-align: left;
            .markdown-content {
              :deep(pre) {
                position: relative;
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                padding: 16px;
                padding-top: 40px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 12px 0;

                &::before {
                  content: attr(data-lang);
                  position: absolute;
                  top: 0;
                  left: 0;
                  right: 0;
                  background-color: #f6f8fa;
                  border-bottom: 1px solid #e1e4e8;
                  padding: 8px 16px;
                  font-size: 12px;
                  font-weight: 600;
                  color: #586069;
                  border-radius: 8px 8px 0 0;
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                }

                code {
                  color: #24292e;
                  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                  font-size: 14px;
                  line-height: 1.45;
                }
              }

              :deep(code) {
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: 'Courier New', Courier, monospace;
              }

              :deep(p) {
                margin: 8px 0;
              }

              :deep(ul),
              :deep(ol) {
                padding-left: 20px;
              }

              :deep(h1),
              :deep(h2),
              :deep(h3),
              :deep(h4),
              :deep(h5),
              :deep(h6) {
                margin-top: 16px;
                margin-bottom: 8px;
              }

              :deep(table) {
                border-collapse: collapse;
                width: 100%;

                th,
                td {
                  border: 1px solid #ddd;
                  padding: 8px;
                }

                th {
                  background-color: #f2f2f2;
                }
              }
            }
          }
        }

        .user-message {
          flex-direction: row;
          display: flex;
          justify-content: flex-end;
          .message-content {
            order: 1; /* 消息内容在左侧 */
            background-color: #ecf5ff;
            color: #333;

            .file-info {
              display: flex;
              align-items: center;
              margin-top: 8px;
              color: #606266;
              font-size: 14px;
              padding: 6px 10px;
              background-color: #f5f7fa;
              border-radius: 4px;

              .el-icon {
                margin-right: 8px;
                font-size: 18px;
              }

              .file-icon {
                &.pdf-icon {
                  color: #e74c3c; /* PDF图标红色 */
                }

                &.word-icon {
                  color: #3498db; /* Word图标蓝色 */
                }
              }

              span {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 200px;
              }
            }
          }
          .avatar {
            order: 2; /* 头像在右侧 */
            margin: 0 10px;
          }
        }
      }
    }
    /* 添加滚动条样式 */
    &::-webkit-scrollbar {
      width: 3px; /* 减小滚动条宽度 */
      height: 3px; /* 水平滚动条高度 */
    }

    &::-webkit-scrollbar-track {
      background: transparent; /* 透明轨道 */
    }

    &::-webkit-scrollbar-thumb {
      background-color: #c1c1c1; /* 浅灰色 */
      border-radius: 3px; /* 圆角 */
      opacity: 0.3; /* 半透明效果 */
      transition: background-color 0.3s; /* 平滑过渡 */

      &:hover {
        background-color: #a8a8a8; /* 鼠标悬停时稍深 */
      }
    }

    /* Firefox 兼容样式 */
    scrollbar-width: thin;
    scrollbar-color: #c1c1c1 transparent;
  }
  .footer {
    position: relative;
    background-color: #ffffff;
    padding: 5vh 60px;
    height: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 0;
    .button-area {
      position: absolute;
      width: 100%;
      bottom: calc(100% + 10px);
      display: flex;
      justify-content: center;
      z-index: 9999999;
      .model-btn {
        font-size: 18px;
        display: flex;
        align-items: center;
        border-color: #e4e7ed;
        background-color: var(--el-color-primary) !important;
        color: white !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        &:hover {
          background-color: #ecf5ff;
          border-color: #c6e2ff;
          color: #409eff;
          transform: translateY(-3px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }
        .el-icon {
          margin: 0 2px;
          font-size: 20px;
        }
      }
    }
  }
  /* 移除Element UI按钮的焦点轮廓 */
  .el-button:focus,
  .el-button:focus-visible {
    outline: none;
  }
}
.typing-cursor {
  box-sizing: border-box; /* 确保盒子模型正确 */
  display: inline-block;
  width: 1px;
  animation: blink 1s infinite;
  margin-left: 2px;
  border: 0;
}

@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}
</style>
