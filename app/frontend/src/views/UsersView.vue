<template>
  <div class="users">
    <div class="page-header">
      <h1>用户管理</h1>
      <BaseButton type="primary">新增用户</BaseButton>
    </div>

    <div class="search-bar">
      <BaseInput 
        v-model="searchQuery" 
        placeholder="搜索用户名/邮箱"
        style="width: 300px"
      />
      <BaseSelect
        v-model="statusFilter"
        :options="statusOptions"
        placeholder="状态筛选"
        style="width: 200px"
      />
    </div>

    <div class="user-table">
      <table>
        <thead>
          <tr>
            <th>用户名</th>
            <th>邮箱</th>
            <th>状态</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="['status', user.status]">
                {{ user.status === 'active' ? '正常' : '禁用' }}
              </span>
            </td>
            <td>{{ user.createdAt }}</td>
            <td>
              <BaseButton size="small">编辑</BaseButton>
              <BaseButton 
                type="danger" 
                size="small"
              >删除</BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')

// 状态选项
const statusOptions = [
  { value: 'active', label: '正常' },
  { value: 'disabled', label: '禁用' }
]

// 模拟用户数据
const users = [
  {
    id: 1,
    username: '张三',
    email: 'zhangsan@example.com',
    status: 'active',
    createdAt: '2024-01-01'
  },
  {
    id: 2,
    username: '李四',
    email: 'lisi@example.com',
    status: 'disabled',
    createdAt: '2024-01-02'
  }
]
</script>

<style scoped>
.users {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.search-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.user-table {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

th {
  background: #fafafa;
  font-weight: 500;
}

.status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.status.active {
  background: #e6f7ff;
  color: #1890ff;
}

.status.disabled {
  background: #fff1f0;
  color: #ff4d4f;
}
</style> 