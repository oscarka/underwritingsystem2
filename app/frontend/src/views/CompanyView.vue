# 创建保司管理页面组件
<template>
  <div class="company-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>保司管理</h1>
      <BaseButton type="primary" @click="handleAdd">新增保司</BaseButton>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <BaseInput 
        v-model="searchQuery.name" 
        placeholder="搜索保司名称"
        style="width: 300px"
      />
      <BaseInput 
        v-model="searchQuery.code" 
        placeholder="搜索保司代码"
        style="width: 200px"
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
    <div class="company-table">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <div class="skeleton-row" v-for="i in 5" :key="i">
          <div class="skeleton-cell" v-for="j in 6" :key="j"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!companyList.length" class="empty-state">
        <span class="icon">📭</span>
        <p>暂无数据</p>
      </div>

      <!-- 表格内容 -->
      <table v-else>
        <thead>
          <tr>
            <th>保司名称</th>
            <th>保司代码</th>
            <th>联系人</th>
            <th>联系电话</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in companyList" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.code }}</td>
            <td>{{ item.contact || '-' }}</td>
            <td>{{ item.phone || '-' }}</td>
            <td>
              <span class="status-badge" :class="item.status">
                {{ item.status === 'enabled' ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ item.created_at }}</td>
            <td>
              <BaseButton size="small" @click="handleEdit(item)">编辑</BaseButton>
              <BaseButton 
                size="small" 
                type="danger" 
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
      :title="modalType === 'add' ? '新增保司' : '编辑保司'"
      width="500px"
      @confirm="handleModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>保司名称</label>
          <BaseInput
            v-model="formData.name"
            placeholder="请输入保司名称"
            :maxlength="50"
          />
          <div class="form-error" v-if="formErrors.name">
            {{ formErrors.name }}
          </div>
        </div>
        
        <div class="form-item">
          <label>保司代码</label>
          <BaseInput
            v-model="formData.code"
            placeholder="请输入保司代码"
            :maxlength="30"
            :disabled="modalType === 'edit'"
          />
          <div class="form-error" v-if="formErrors.code">
            {{ formErrors.code }}
          </div>
        </div>

        <div class="form-item">
          <label>联系人</label>
          <BaseInput
            v-model="formData.contact"
            placeholder="请输入联系人姓名"
            :maxlength="32"
          />
          <div class="form-error" v-if="formErrors.contact">
            {{ formErrors.contact }}
          </div>
        </div>

        <div class="form-item">
          <label>联系电话</label>
          <BaseInput
            v-model="formData.phone"
            placeholder="请输入联系电话"
            :maxlength="32"
          />
          <div class="form-error" v-if="formErrors.phone">
            {{ formErrors.phone }}
          </div>
        </div>

        <div class="form-item">
          <label>地址</label>
          <BaseInput
            v-model="formData.address"
            type="textarea"
            placeholder="请输入地址"
            :rows="2"
            :maxlength="256"
          />
        </div>

        <div class="form-item">
          <label>备注</label>
          <BaseInput
            v-model="formData.remark"
            type="textarea"
            placeholder="请输入备注信息"
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

// 保司状态枚举
enum CompanyStatus {
  ENABLED = 'enabled',
  DISABLED = 'disabled'
}

// 保司数据类型
interface Company {
  id: number
  code: string
  name: string
  contact?: string
  phone?: string
  address?: string
  remark?: string
  status: CompanyStatus
  created_at: string
  updated_at?: string
}

// 查询参数类型
interface CompanyQuery {
  name: string
  code: string
  status?: CompanyStatus
  page: number
  pageSize: number
}

// 创建保司参数类型
interface CreateCompanyParams {
  name: string
  code: string
  contact?: string
  phone?: string
  address?: string
  remark?: string
  status: CompanyStatus
}

// 查询参数
const searchQuery = reactive<CompanyQuery>({
  name: '',
  code: '',
  status: undefined,
  page: 1,
  pageSize: 10
})

// 状态选项
const statusOptions = [
  { value: CompanyStatus.ENABLED, label: '启用' },
  { value: CompanyStatus.DISABLED, label: '禁用' }
]

// 分页参数
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 保司列表
const companyList = ref<Company[]>([])
const loading = ref(false)

// 弹窗控制
const showModal = ref(false)
const modalType = ref<'add' | 'edit'>('add')
const currentId = ref<number>()
const formData = reactive<Omit<CreateCompanyParams, 'id'>>({
  name: '',
  code: '',
  contact: '',
  phone: '',
  address: '',
  remark: '',
  status: CompanyStatus.ENABLED
})
const formErrors = reactive({
  name: '',
  code: '',
  contact: '',
  phone: ''
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const params = {
      name: searchQuery.name,
      code: searchQuery.code,
      status: searchQuery.status,
      page: page.value,
      pageSize: pageSize.value
    }
    const res = await get('/api/v1/business/companies', { params })
    if (res.code === 200) {
      companyList.value = res.data.list
      total.value = res.data.total
    } else {
      showToast('error', res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载保司列表失败:', error)
    showToast('error', '加载失败，请重试')
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
  searchQuery.code = ''
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
  formErrors.contact = ''
  formErrors.phone = ''

  if (!formData.name) {
    formErrors.name = '请输入保司名称'
    valid = false
  } else if (formData.name.length > 50) {
    formErrors.name = '保司名称不能超过50个字符'
    valid = false
  }

  if (!formData.code) {
    formErrors.code = '请输入保司代码'
    valid = false
  } else if (formData.code.length > 30) {
    formErrors.code = '保司代码不能超过30个字符'
    valid = false
  } else if (!/^[A-Z0-9_]+$/.test(formData.code)) {
    formErrors.code = '保司代码只能包含大写字母、数字和下划线'
    valid = false
  }

  if (!formData.contact) {
    formErrors.contact = '请输入联系人'
    valid = false
  } else if (formData.contact.length > 32) {
    formErrors.contact = '联系人不能超过32个字符'
    valid = false
  }

  if (!formData.phone) {
    formErrors.phone = '请输入联系电话'
    valid = false
  } else if (formData.phone.length > 32) {
    formErrors.phone = '联系电话不能超过32个字符'
    valid = false
  }

  return valid
}

// 新增
function handleAdd() {
  modalType.value = 'add'
  formData.name = ''
  formData.code = ''
  formData.contact = ''
  formData.phone = ''
  formData.address = ''
  formData.remark = ''
  formData.status = CompanyStatus.ENABLED
  showModal.value = true
}

// 编辑
function handleEdit(item: Company) {
  modalType.value = 'edit'
  currentId.value = item.id
  formData.name = item.name
  formData.code = item.code
  formData.contact = item.contact
  formData.phone = item.phone
  formData.address = item.address
  formData.remark = item.remark
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

// 创建保司
async function handleCreate() {
  try {
    const requestData = {
      name: formData.name,
      code: formData.code,
      contact: formData.contact,
      phone: formData.phone,
      address: formData.address || '',
      remark: formData.remark || '',
      status: formData.status
    }
    console.log('创建保司请求数据:', requestData)
    const res = await post('/api/v1/business/companies', requestData)
    if (res.code === 200) {
      showToast('success', '创建成功')
      showModal.value = false
      loadData()
    } else {
      showToast('error', res.message || '创建失败')
    }
  } catch (error: any) {
    console.error('创建保司失败:', error)
    showToast('error', '创建失败，请重试')
  }
}

// 更新保司
async function handleUpdate() {
  if (!currentId.value) return
  
  try {
    const requestData = {
      name: formData.name,
      code: formData.code,
      contact: formData.contact,
      phone: formData.phone,
      address: formData.address || '',
      remark: formData.remark || '',
      status: formData.status
    }
    console.log('更新保司请求数据:', requestData)
    const res = await put(`/api/v1/business/companies/${currentId.value}`, requestData)
    if (res.code === 200) {
      showToast('success', '更新成功')
      showModal.value = false
      loadData()
    } else {
      showToast('error', res.message || '更新失败')
    }
  } catch (error: any) {
    console.error('更新保司失败:', error)
    showToast('error', '更新失败，请重试')
  }
}

// 删除保司
async function handleDelete(item: Company) {
  if (!confirm(`确认删除保司"${item.name}"吗？`)) return
  
  try {
    const res = await del(`/api/v1/business/companies/${item.id}`)
    if (res.code === 200) {
      showToast('success', '删除成功')
      loadData()
    } else {
      showToast('error', res.message || '删除失败')
    }
  } catch (error: any) {
    console.error('删除保司失败:', error)
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
.company-page {
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

.company-table {
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

.status-badge.enabled {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status-badge.disabled {
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