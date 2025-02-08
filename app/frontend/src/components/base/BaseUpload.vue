<template>
  <div class="base-upload">
    <div 
      class="upload-area"
      :class="{ 'is-dragover': isDragover }"
      @dragover.prevent="handleDragover"
      @dragleave.prevent="handleDragleave"
      @drop.prevent="handleDrop"
      @click="triggerUpload"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        class="file-input"
        @change="handleFileChange"
      >
      <div class="upload-content">
        <i class="upload-icon">📁</i>
        <div class="upload-text">
          <p>{{ placeholder || '点击或拖拽文件到此处上传' }}</p>
          <p class="upload-hint">支持的文件类型: {{ acceptText }}</p>
        </div>
      </div>
    </div>
    
    <!-- 文件列表 -->
    <div v-if="modelValue" class="file-list">
      <div class="file-item">
        <span class="file-name">{{ modelValue.name }}</span>
        <span class="file-size">{{ formatFileSize(modelValue.size) }}</span>
        <button class="remove-btn" @click.stop="removeFile">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: File,
    default: null
  },
  accept: {
    type: String,
    default: '*'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  maxSize: {
    type: Number,
    default: 10 // 默认10MB
  },
  placeholder: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'error'])

const fileInput = ref<HTMLInputElement | null>(null)
const isDragover = ref(false)

// 计算接受的文件类型文本
const acceptText = computed(() => {
  return props.accept.split(',').join('、') || '所有文件'
})

// 触发文件选择
const triggerUpload = () => {
  console.log('[BaseUpload] 触发文件选择')
  fileInput.value?.click()
}

// 处理文件选择
const handleFileChange = (event: Event) => {
  console.log('[BaseUpload] 文件选择事件触发')
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    console.log('[BaseUpload] 选择的文件:', {
      name: input.files[0].name,
      type: input.files[0].type,
      size: input.files[0].size
    })
    validateAndEmitFile(input.files[0])
  } else {
    console.log('[BaseUpload] 没有选择文件')
  }
}

// 处理拖拽进入
const handleDragover = (event: DragEvent) => {
  console.log('[BaseUpload] 文件拖拽进入')
  isDragover.value = true
  event.dataTransfer!.dropEffect = 'copy'
}

// 处理拖拽离开
const handleDragleave = () => {
  console.log('[BaseUpload] 文件拖拽离开')
  isDragover.value = false
}

// 处理文件放下
const handleDrop = (event: DragEvent) => {
  console.log('[BaseUpload] 文件拖放')
  isDragover.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    console.log('[BaseUpload] 拖放的文件:', {
      name: files[0].name,
      type: files[0].type,
      size: files[0].size
    })
    validateAndEmitFile(files[0])
  }
}

// 验证并发送文件
const validateAndEmitFile = (file: File) => {
  console.log('[BaseUpload] 开始验证文件:', {
    name: file.name,
    type: file.type,
    size: file.size,
    acceptTypes: props.accept
  })
  
  // 验证文件类型
  if (props.accept !== '*') {
    const acceptTypes = props.accept.split(',').map(type => type.trim())
    const fileExt = file.name.split('.').pop()?.toLowerCase()
    const isValidType = acceptTypes.some(type => {
      if (type.startsWith('.')) {
        return fileExt === type.substring(1)
      }
      return file.type.includes(type)
    })
    
    if (!isValidType) {
      console.error('[BaseUpload] 文件类型错误:', {
        fileType: file.type,
        acceptTypes
      })
      emit('error', { type: 'type', message: '不支持的文件类型' })
      return
    }
  }
  
  // 验证文件大小
  if (file.size > props.maxSize * 1024 * 1024) {
    console.error('[BaseUpload] 文件大小超限:', {
      fileSize: file.size,
      maxSize: props.maxSize * 1024 * 1024
    })
    emit('error', { type: 'size', message: `文件大小不能超过${props.maxSize}MB` })
    return
  }
  
  console.log('[BaseUpload] 文件验证通过，发送文件')
  emit('update:modelValue', file)
}

// 移除文件
const removeFile = () => {
  console.log('[BaseUpload] 移除文件')
  emit('update:modelValue', null)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 格式化文件大小
const formatFileSize = (size: number) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else {
    return (size / (1024 * 1024)).toFixed(2) + ' MB'
  }
}
</script>

<style scoped>
.base-upload {
  width: 100%;
}

.upload-area {
  position: relative;
  padding: 20px;
  border: 2px dashed var(--color-border);
  border-radius: var(--border-radius-lg);
  background: var(--color-bg-container);
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover,
.upload-area.is-dragover {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.file-input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
}

.upload-content {
  text-align: center;
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.upload-text {
  color: var(--color-text-secondary);
}

.upload-hint {
  font-size: var(--font-size-sm);
  margin-top: 4px;
}

.file-list {
  margin-top: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: var(--color-bg-container);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
}

.file-name {
  flex: 1;
  margin-right: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: var(--color-text-secondary);
  margin-right: 8px;
}

.remove-btn {
  padding: 0 4px;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.3s;
}

.remove-btn:hover {
  color: var(--color-error);
}
</style> 