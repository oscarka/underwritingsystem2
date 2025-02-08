<template>
  <div class="channel-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>渠道管理</h1>
      <BaseButton type="primary" @click="handleAdd">新增渠道</BaseButton>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <BaseInput 
        v-model="searchQuery.name" 
        placeholder="搜索渠道名称"
        style="width: 300px"
      />
      <BaseSelect
        v-model="searchQuery.status"
        :options="statusOptions"
        placeholder="状态筛选"
        style="width: 200px"
      />
      <BaseButton @click="handleSearch">搜索</BaseButton>
      <BaseButton @click="handleReset">重置</BaseButton>
    </div>

    <!-- 数据表格 -->
    <div class="channel-table">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <div class="skeleton-row" v-for="i in 5" :key="i">
          <div class="skeleton-cell" v-for="j in 6" :key="j"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!channelList.length" class="empty-state">
        <span class="icon">📭</span>
        <p>暂无数据</p>
      </div>

      <!-- 数据表格 -->
      <table v-else>
        <thead>
          <tr>
            <th>渠道编码</th>
            <th>渠道名称</th>
            <th>描述</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in channelList" :key="item.id">
            <td>{{ item.code }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.description || '-' }}</td>
            <td>
              <span :class="['status-badge', item.status]">
                {{ item.status === ChannelStatus.ENABLED ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ item.createTime }}</td>
            <td>{{ item.updateTime || '-' }}</td>
            <td>
              <BaseButton 
                size="small"
                @click="handleEdit(item)"
              >编辑</BaseButton>
              <BaseButton 
                type="danger" 
                size="small"
                @click="handleDelete(item)"
              >删除</BaseButton>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页 -->
      <div class="pagination">
        <BasePagination
          v-model:current="page"
          v-model:pageSize="pageSize"
          :total="total"
          @change="handlePageChange"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <BaseModal
      v-model="showModal"
      :title="modalType === 'add' ? '新增渠道' : '编辑渠道'"
      width="500px"
      @confirm="handleModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>渠道名称</label>
          <BaseInput
            v-model="formData.name"
            placeholder="请输入渠道名称"
            :maxlength="50"
          />
          <div class="form-error" v-if="formErrors.name">
            {{ formErrors.name }}
          </div>
        </div>
        
        <div class="form-item">
          <label>渠道编码</label>
          <BaseInput
            v-model="formData.code"
            placeholder="请输入渠道编码"
            :maxlength="30"
            :disabled="modalType === 'edit'"
          />
          <div class="form-error" v-if="formErrors.code">
            {{ formErrors.code }}
          </div>
        </div>

        <div class="form-item">
          <label>描述</label>
          <BaseInput
            v-model="formData.description"
            type="textarea"
            placeholder="请输入描述信息"
            :rows="3"
          />
        </div>

        <div class="form-item">
          <label>状态</label>
          <BaseSelect
            v-model="formData.status"
            :options="statusOptions"
          />
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { get, post, put, del } from '../utils/request'
import { showToast } from '../utils/toast'
import { getToken, isLoggedIn } from '../utils/auth'
import { useRouter } from 'vue-router'
import BasePagination from '../components/base/BasePagination.vue'
import BaseModal from '../components/base/BaseModal.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseSelect from '../components/base/BaseSelect.vue'

// 渠道状态枚举
enum ChannelStatus {
  ENABLED = 'ENABLED',
  DISABLED = 'DISABLED'
}

// 渠道数据类型
interface Channel {
  id: number
  code: string
  name: string
  description?: string
  status: ChannelStatus
  createTime: string
  updateTime?: string
}

// 查询参数类型
interface ChannelQuery {
  name: string
  status?: ChannelStatus
  page: number
  pageSize: number
}

// 创建渠道参数类型
interface CreateChannelParams {
  name: string
  code: string
  description?: string
  status: ChannelStatus
}

// 分页响应类型
interface PaginatedResponse<T> {
  list: T[]
  pagination: {
    total: number
    page: number
    pageSize: number
  }
}

// 查询参数
const searchQuery = reactive<ChannelQuery>({
  name: '',
  status: undefined,
  page: 1,
  pageSize: 10
})

// 状态选项
const statusOptions = [
  { value: ChannelStatus.ENABLED, label: '启用' },
  { value: ChannelStatus.DISABLED, label: '禁用' }
]

// 分页参数
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 渠道列表
const channelList = ref<Channel[]>([])
const loading = ref(false)

// 弹窗控制
const showModal = ref(false)
const modalType = ref<'add' | 'edit'>('add')
const currentId = ref<number>()
const formData = reactive<Omit<CreateChannelParams, 'id'>>({
  name: '',
  code: '',
  description: '',
  status: ChannelStatus.ENABLED
})
const formErrors = reactive({
  name: '',
  code: ''
})

// 加载数据
async function loadData() {
  console.log('开始加载渠道数据:', {
    page: page.value,
    pageSize: pageSize.value,
    keyword: searchQuery.name,
    status: searchQuery.status
  })
  
  loading.value = true
  try {
    const res = await get<PaginatedResponse<Channel>>('/api/v1/business/channels', {
      params: {
        page: page.value,
        pageSize: pageSize.value,
        name: searchQuery.name || undefined,
        status: searchQuery.status
      }
    })
    
    console.log('渠道数据响应:', res)
    
    if (res.code === 200) {
      channelList.value = res.data.list || []
      total.value = res.data.pagination?.total || 0
      console.log('渠道数据加载成功:', {
        list: channelList.value,
        total: total.value
      })
    } else {
      console.error('加载渠道数据失败:', res.message)
      showToast('error', res.message || '加载失败')
      channelList.value = []
      total.value = 0
    }
    
  } catch (error: any) {
    console.error('加载渠道列表失败:', error)
    showToast('error', error.message || '加载失败')
    channelList.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  page.value = 1
  loadData()
}

// 重置
function handleReset() {
  searchQuery.name = ''
  searchQuery.status = undefined
  page.value = 1
  loadData()
}

// 分页变化
function handlePageChange() {
  loadData()
}

// 表单验证
function validateForm() {
  let valid = true
  formErrors.name = ''
  formErrors.code = ''

  if (!formData.name) {
    formErrors.name = '请输入渠道名称'
    valid = false
  } else if (formData.name.length > 50) {
    formErrors.name = '渠道名称不能超过50个字符'
    valid = false
  }

  if (!formData.code) {
    formErrors.code = '请输入渠道编码'
    valid = false
  } else if (formData.code.length > 30) {
    formErrors.code = '渠道编码不能超过30个字符'
    valid = false
  } else if (!/^[A-Z0-9_]+$/.test(formData.code)) {
    formErrors.code = '渠道编码只能包含大写字母、数字和下划线'
    valid = false
  }

  return valid
}

// 新增
function handleAdd() {
  modalType.value = 'add'
  formData.name = ''
  formData.code = ''
  formData.description = ''
  formData.status = ChannelStatus.ENABLED
  showModal.value = true
}

// 编辑
function handleEdit(item: Channel) {
  modalType.value = 'edit'
  currentId.value = item.id
  formData.name = item.name
  formData.code = item.code
  formData.description = item.description
  formData.status = item.status
  showModal.value = true
}

// 弹窗确认
async function handleModalConfirm() {
  if (!validateForm()) return

  try {
    if (modalType.value === 'add') {
      await handleCreate()
    } else if (currentId.value) {
      await handleUpdate()
    }
  } catch (error) {
    console.error('保存失败:', error)
    showToast('error', '保存失败，请重试')
  }
}

// 创建渠道
async function handleCreate() {
  try {
    const requestData = {
      name: formData.name,
      code: formData.code,
      description: formData.description || '',
      status: formData.status
    }
    console.log('创建渠道请求数据:', requestData)
    const res = await post('/api/v1/business/channels', requestData)
    if (res.code === 200) {
      showToast('success', '创建成功')
      showModal.value = false
      loadData()
    } else {
      showToast('error', res.message || '创建失败')
    }
  } catch (error: any) {
    console.error('创建渠道失败:', error)
    showToast('error', '创建失败，请重试')
  }
}

// 更新渠道
async function handleUpdate() {
  if (!currentId.value) return
  
  try {
    const requestData = {
      config: {
        name: formData.name,
        code: formData.code,
        description: formData.description || '',
        status: formData.status
      }
    }
    console.log('更新渠道请求数据:', requestData)
    const res = await put(`/api/v1/business/channels/${currentId.value}`, requestData)
    if (res.code === 200) {
      showToast('success', '更新成功')
      showModal.value = false
      loadData()
    } else {
      showToast('error', res.message || '更新失败')
    }
  } catch (error: any) {
    console.error('更新渠道失败:', error)
    showToast('error', '更新失败，请重试')
  }
}

// 删除渠道
async function handleDelete(item: Channel) {
  if (!confirm(`确认删除渠道"${item.name}"吗？`)) return
  
  try {
    const res = await del(`/api/v1/business/channels/${item.id}`)
    if (res.code === 200) {
      showToast('success', '删除成功')
      loadData()
    } else {
      showToast('error', res.message || '删除失败')
    }
  } catch (error: any) {
    console.error('删除渠道失败:', error)
    showToast('error', '删除失败，请重试')
  }
}

// 初始化加载数据
onMounted(() => {
  console.log('组件挂载，检查登录状态:', {
    isLoggedIn: isLoggedIn(),
    token: getToken()
  })
  loadData()
})
</script>

<style scoped>
.channel-page {
  padding: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.page-header h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
}

.search-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.channel-table {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.status-badge.ENABLED {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status-badge.DISABLED {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.loading-wrapper {
  padding: var(--spacing-lg);
}

.skeleton-row {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.skeleton-cell {
  height: 24px;
  background: var(--color-bg-spotlight);
  border-radius: var(--border-radius-sm);
  flex: 1;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-xl) 0;
  color: var(--color-text-secondary);
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
}

.pagination {
  margin-top: var(--spacing-lg);
  display: flex;
  justify-content: flex-end;
}

.form {
  padding: var(--spacing-lg) 0;
}

.form-item {
  margin-bottom: var(--spacing-lg);
}

.form-item label {
  display: block;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-secondary);
}

.form-error {
  margin-top: var(--spacing-xs);
  color: var(--color-error);
  font-size: var(--font-size-sm);
}
</style> 