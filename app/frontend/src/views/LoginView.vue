<template>
  <div class="login-page">
    <div class="login-box">
      <h2>登录</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-item">
          <label>用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" />
        </div>
        
        <div class="form-item">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" />
        </div>
        
        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { post } from '@/utils/request'
import { setToken, setUser, TOKEN_KEY, USER_KEY } from '@/utils/auth'
import { showToast } from '@/utils/toast'
import type { ApiResponse } from '@/utils/request'

interface LoginResponse {
  token: string;
  user: {
    id: number;
    username: string;
    is_admin: boolean;
    tenant_id: number;
  };
}

const router = useRouter()
const username = ref('')
const password = ref('')
const isSubmitting = ref(false)

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    showToast('error', '请输入用户名和密码')
    return
  }
  
  console.log('开始登录流程:', { username: username.value })
  
  isSubmitting.value = true
  try {
    console.log('发送登录请求...')
    const res = await post<LoginResponse>('/api/auth/login', {
      username: username.value,
      password: password.value
    })
    
    console.log('登录响应数据:', res)
    
    if (res.code === 200 && res.data) {
      if (!res.data.token || !res.data.user) {
        console.error('登录响应缺少token或user数据')
        showToast('error', '登录响应数据不完整')
        return
      }
      
      console.log('保存用户信息:', {
        token: res.data.token,
        user: res.data.user
      })
      
      setToken(res.data.token)
      setUser(res.data.user)
      
      console.log('用户信息保存完成，验证保存结果:', {
        savedToken: localStorage.getItem(TOKEN_KEY),
        savedUser: localStorage.getItem(USER_KEY)
      })
      
      showToast('success', '登录成功')
      console.log('开始路由跳转到根路径')
      router.push('/')
      console.log('路由跳转命令已发出')
    } else {
      console.error('登录响应错误:', res)
      showToast('error', res.message || '登录失败')
    }
  } catch (error: any) {
    console.error('登录过程出错:', error)
    showToast('error', error.message || '登录失败')
  } finally {
    console.log('登录流程结束')
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  margin: 0 0 24px;
  text-align: center;
  color: #333;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: #666;
}

.form-item input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-item input:focus {
  border-color: #1890ff;
  outline: none;
}

button {
  width: 100%;
  padding: 12px;
  background: #1890ff;
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background: #40a9ff;
}

button:disabled {
  background: #bae7ff;
  cursor: not-allowed;
}
</style> 