<template>
  <div class="api-test">
    <h2>接口测试</h2>
    
    <div class="test-section">
      <h3>GET 请求测试</h3>
      <BaseButton @click="testGet">发送 GET 请求</BaseButton>
    </div>

    <div class="test-section">
      <h3>POST 请求测试</h3>
      <BaseInput v-model="postData.name" placeholder="请输入名称" />
      <BaseInput v-model="postData.email" placeholder="请输入邮箱" />
      <BaseButton @click="testPost">发送 POST 请求</BaseButton>
    </div>

    <div class="test-section">
      <h3>错误处理测试</h3>
      <BaseButton type="danger" @click="testError">测试错误处理</BaseButton>
    </div>

    <div class="test-section">
      <h3>并发请求测试</h3>
      <BaseButton @click="testConcurrent">发送并发请求</BaseButton>
    </div>

    <div class="response-section" v-if="response">
      <h3>响应数据</h3>
      <pre>{{ JSON.stringify(response, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { get, post } from '@/utils/request'
import { toast } from '@/utils/feedback'

// POST 请求数据
const postData = reactive({
  name: '',
  email: ''
})

// 响应数据
const response = ref<any>(null)

// GET 请求测试
async function testGet() {
  try {
    const data = await get('/test/get')
    response.value = data
    toast.success('GET 请求成功')
  } catch (error) {
    console.error(error)
  }
}

// POST 请求测试
async function testPost() {
  try {
    const data = await post('/test/post', postData)
    response.value = data
    toast.success('POST 请求成功')
  } catch (error) {
    console.error(error)
  }
}

// 错误处理测试
async function testError() {
  try {
    await get('/test/error')
  } catch (error) {
    console.error(error)
  }
}

// 并发请求测试
async function testConcurrent() {
  try {
    const [data1, data2] = await Promise.all([
      get('/test/get1'),
      get('/test/get2')
    ])
    response.value = { data1, data2 }
    toast.success('并发请求成功')
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
.api-test {
  padding: var(--spacing-lg);
}

.test-section {
  margin-bottom: var(--spacing-xl);
}

.test-section h3 {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
}

.test-section :deep(.base-input),
.test-section :deep(.base-button) {
  margin-bottom: var(--spacing-sm);
}

.response-section {
  padding: var(--spacing-md);
  background: var(--color-bg-container);
  border-radius: var(--radius-md);
}

.response-section h3 {
  margin-bottom: var(--spacing-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
}

.response-section pre {
  margin: 0;
  padding: var(--spacing-md);
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  overflow-x: auto;
}
</style> 