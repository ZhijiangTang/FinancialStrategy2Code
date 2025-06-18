<template>
  <div class="input-container">
    <div class="input-wrapper">
      <!-- 输入框 -->
      <input type="file" ref="fileInput" style="display: none" @change="handleFileSelect" accept=".pdf,.doc,.docx,.json" />
      <el-input ref="inputRef" :disabled="disabled" v-model="inputText" type="textarea" :rows="2" :autosize="{ minRows: 1, maxRows: 4 }" placeholder="有问题，尽管问，alt+enter换行" @keydown.alt.enter.prevent="handleShiftEnter" @keydown.enter.prevent="handleEnter" class="message-input" />

      <!-- 底部按钮区域 -->
      <div class="bottom-buttons">
        <div class="left-buttons">
          <el-button type="primary" class="model-btn"> Qwen3-30B-A3B </el-button>
        </div>

        <div class="right-buttons">
          <!-- 上传文件按钮 -->
          <el-button circle :disabled="disabled" @click="triggerFileInput">
            <el-icon><upload /></el-icon>
          </el-button>

          <!-- 发送按钮 -->
          <el-button type="primary" circle @click="handleSend" :disabled="disabled || (!inputText.trim() && !selectedFile)">
            <el-icon><position /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
    <div v-if="selectedFile" class="file-preview">
      {{ selectedFile.name }}
      <el-icon @click="removeFile" style="cursor: pointer"><close /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { Search, Picture, Upload, Position, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
const props = defineProps({
  disabled: Boolean // 接收禁用状态
})
const inputText = ref('')
const emit = defineEmits(['send'])

const fileInput = ref(null)
const selectedFile = ref(null)
const inputRef = ref(null) // 新增：输入框引用
// 触发文件选择
const triggerFileInput = () => {
  fileInput.value.click()
}
const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus()
    }
  })
}
// 处理文件选择
const handleFileSelect = event => {
  const file = event.target.files[0]
  const allowedExtensions = ['pdf', 'doc', 'docx', 'json']
  let fileExtension = null
  if (file) {
    // 获取文件扩展名
    const fileName = file.name.toLowerCase()
    fileExtension = fileName.substring(fileName.lastIndexOf('.') + 1)

    // 允许的文件类型

    // 检查文件类型是否在允许的范围内
    if (allowedExtensions.includes(fileExtension)) {
      selectedFile.value = file
      console.log(selectedFile.value)
    } else {
      // 如果文件类型不被允许，显示提示信息并清空选中的文件
      ElMessage({
        message: '只能上传 PDF 、 Word 文件(.doc, .docx) 或 Json 文件(.json)',
        type: 'error',
        plain: true
      })
      selectedFile.value = null
      fileInput.value.value = '' // 清空文件输入框
    }
  }
  if (!file || !allowedExtensions.includes(fileExtension)) {
    event.target.value = '' // 清除无效选择
  }
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus()
    }
  })
}
// 处理Shift+Enter换行
const handleShiftEnter = () => {
  inputText.value += '\n'
  console.log(inputText.value)
}

// 处理Enter发送
const handleEnter = e => {
  if (props.disabled) return // 如果禁用则不发送
  if (!e.altKey && (inputText.value.trim() || selectedFile.value)) {
    sendMessage()
  }
}

// 发送消息
const sendMessage = () => {
  if (inputText.value.trim() || selectedFile.value) {
    emit('send', inputText.value, selectedFile.value)
    console.log('发送消息：', inputText.value)
    inputText.value = ''
    selectedFile.value = null
    // 正确重置文件输入框
    if (fileInput.value) {
      fileInput.value.value = '' // 关键修复：重置文件输入框的值
    }
  }
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus()
    }
  })
}
const handleSend = () => {
  if (props.disabled) return // 如果禁用则不发送
  sendMessage()
}
</script>

<style scoped lang="less">
.input-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  .file-preview {
    display: flex;
    align-items: center;
    padding: 4px 8px;
    background: #f5f7fa;
    border-radius: 4px;
    margin-top: 8px;
  }
}

.input-wrapper {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(123, 121, 121, 0.1);
  padding: 12px 16px;
}

.message-input {
  width: 100%;
  font-size: 16px;
  margin-bottom: 8px;
  &:deep(.el-textarea__inner) {
    &:disabled {
      background-color: #ffffff; /* 保持白色背景 */
      color: #909399; /* 稍微淡化的文字颜色 */
      border-color: transparent; /* 透明边框 */
      border: none;
      box-shadow: none;
      opacity: 0.8; /* 轻微透明效果 */
      cursor: not-allowed; /* 禁用光标 */
    }
  }
}

.message-input :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding: 8px 0;
  font-size: 16px;
  resize: none;
}

.bottom-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.left-buttons {
  display: flex;
  gap: 8px;
  align-items: center;

  .el-button:disabled {
    background-color: #f5f7fa;
    border-color: #e4e7ed;
    color: #c0c4cc;
    opacity: 0.6;
  }
}

.right-buttons {
  display: flex;
  gap: 8px;

  .el-button:disabled {
    background-color: #f5f7fa;
    border-color: #e4e7ed;
    color: #c0c4cc;
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.model-btn {
  background-color: #e6f1fc;
  border-color: #d1e6fa;
  color: #409eff;
}

/* 移除Element UI按钮的焦点轮廓 */
.el-button:focus,
.el-button:focus-visible {
  outline: none;
}
</style>
