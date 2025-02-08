# 智核参数管理页面
<template>
  <div class="ai-parameter-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>智核参数管理</h1>
      <BaseButton type="primary" @click="handleAdd">新增参数</BaseButton>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <BaseInput 
        v-model="searchQuery.name" 
        placeholder="搜索参数名称"
        style="width: 300px"
      />
      <BaseSelect
        v-model="searchQuery.parameter_type_id"
        :options="parameterTypeOptions"
        placeholder="参数类型"
        style="width: 200px"
      />
      <BaseSelect
        v-model="searchQuery.rule_id"
        :options="ruleOptions"
        placeholder="核保规则"
        style="width: 200px"
      />
      <BaseButton @click="handleSearch">搜索</BaseButton>
      <BaseButton @click="handleReset">重置</BaseButton>
    </div>

    <!-- 数据表格 -->
    <div class="parameter-table">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <div class="skeleton-row" v-for="i in 5" :key="i">
          <div class="skeleton-cell" v-for="j in 6" :key="j"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!tableData.length" class="empty-state">
        <span class="icon">📭</span>
        <p>暂无数据</p>
      </div>

      <!-- 数据表格 -->
      <table v-else>
        <thead>
          <tr>
            <th>参数名称</th>
            <th>参数类型</th>
            <th>核保规则</th>
            <th>参数值</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in tableData" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.parameter_type_name }}</td>
            <td>{{ item.rule_name }}</td>
            <td>{{ item.value }}</td>
            <td>
              <span :class="['status-badge', item.status === 'enabled' ? 'ENABLED' : 'DISABLED']">
                {{ item.status === 'enabled' ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ item.created_at }}</td>
            <td>{{ item.updated_at }}</td>
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
      :title="modalType === 'add' ? '新增参数' : '编辑参数'"
      width="500px"
      @confirm="handleModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>参数名称</label>
          <BaseInput
            v-model="formData.name"
            placeholder="请输入参数名称"
            :maxlength="100"
          />
          <div class="form-error" v-if="formErrors.name">
            {{ formErrors.name }}
          </div>
        </div>
        
        <div class="form-item">
          <label>参数类型</label>
          <BaseSelect
            v-model="formData.parameter_type_id"
            :options="parameterTypeOptions"
            placeholder="请选择参数类型"
          />
          <div class="form-error" v-if="formErrors.parameter_type_id">
            {{ formErrors.parameter_type_id }}
          </div>
        </div>

        <div class="form-item">
          <label>核保规则</label>
          <BaseSelect
            v-model="formData.rule_id"
            :options="ruleOptions"
            placeholder="请选择核保规则"
          />
          <div class="form-error" v-if="formErrors.rule_id">
            {{ formErrors.rule_id }}
          </div>
        </div>

        <div class="form-item">
          <label>参数值</label>
          <BaseInput
            v-model="formData.value"
            type="textarea"
            placeholder="请输入参数值"
            :maxlength="500"
            :rows="4"
          />
          <div class="form-error" v-if="formErrors.value">
            {{ formErrors.value }}
          </div>
        </div>

        <div class="form-item">
          <label>参数描述</label>
          <BaseInput
            v-model="formData.description"
            type="textarea"
            placeholder="请输入参数描述"
            :maxlength="500"
            :rows="4"
          />
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from '@/composables/useMessage'
import type { ApiResponse } from '@/types/api'
import type { Parameter, ParameterType } from '@/types/underwriting'
import {
  getParameterList,
  getParameterTypes,
  getRules,
  deleteParameter,
  createParameter,
  updateParameter
} from '@/api/underwriting'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BasePagination from '@/components/base/BasePagination.vue'
import BaseModal from '@/components/base/BaseModal.vue'

// 状态枚举
enum ParameterStatus {
  ENABLED = 'enabled',
  DISABLED = 'disabled'
}

// 查询参数类型
interface ParameterQuery {
  name: string
  parameter_type_id?: number
  rule_id?: number
  page: number
  pageSize: number
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

const router = useRouter()
const route = useRoute()
const message = useMessage()

// 查询参数
const searchQuery = ref<ParameterQuery>({
  name: '',
  parameter_type_id: undefined,
  rule_id: undefined,
  page: 1,
  pageSize: 10
})

// 状态选项
const statusOptions = [
  { value: ParameterStatus.ENABLED, label: '启用' },
  { value: ParameterStatus.DISABLED, label: '禁用' }
]

// 分页参数
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 表格数据
const tableData = ref<Parameter[]>([])
const loading = ref(false)

// 下拉选项数据
const parameterTypes = ref<ParameterType[]>([])
const rules = ref<{ id: number; name: string }[]>([])

// 下拉选项
const parameterTypeOptions = computed(() => 
  parameterTypes.value.map(type => ({
    label: type.name,
    value: type.id
  }))
)

const ruleOptions = computed(() => 
  rules.value.map(rule => ({
    label: rule.name,
    value: rule.id
  }))
)

// 加载表格数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getParameterList({
      page: page.value,
      pageSize: pageSize.value,
      name: searchQuery.value.name || undefined,
      parameter_type_id: searchQuery.value.parameter_type_id,
      rule_id: searchQuery.value.rule_id
    })
    
    if (res.code === 200) {
      tableData.value = res.data.list || []
      total.value = res.data.total || 0
    } else {
      message.error(res.message || '加载失败')
      tableData.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('加载参数列表失败:', error)
    message.error(error.message || '加载失败')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 加载参数类型列表
const loadParameterTypes = async () => {
  try {
    const res = await getParameterTypes()
    if (res.code === 200) {
      parameterTypes.value = res.data
    } else {
      message.error(res.message || '获取参数类型失败')
    }
  } catch (error: any) {
    console.error('获取参数类型失败:', error)
    message.error(error.message || '获取参数类型失败')
  }
}

// 加载规则列表
const loadRules = async () => {
  try {
    const res = await getRules()
    if (res.code === 200) {
      rules.value = res.data
    } else {
      message.error(res.message || '获取规则列表失败')
    }
  } catch (error: any) {
    console.error('获取规则列表失败:', error)
    message.error(error.message || '获取规则列表失败')
  }
}

// 搜索
const handleSearch = () => {
  page.value = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchQuery.value.name = ''
  searchQuery.value.parameter_type_id = undefined
  searchQuery.value.rule_id = undefined
  page.value = 1
  loadData()
}

// 分页变化
const handlePageChange = () => {
  loadData()
}

// 弹窗控制
const showModal = ref(false)
const modalType = ref<'add' | 'edit'>('add')
const currentId = ref<number>()

// 表单数据
const formData = reactive({
  name: '',
  parameter_type_id: undefined as number | undefined,
  rule_id: undefined as number | undefined,
  value: '',
  description: undefined as string | undefined,
  status: ParameterStatus.ENABLED
})

// 表单错误
const formErrors = reactive({
  name: '',
  parameter_type_id: '',
  rule_id: '',
  value: ''
})

// 表单验证
const validateForm = () => {
  let valid = true
  formErrors.name = ''
  formErrors.parameter_type_id = ''
  formErrors.rule_id = ''
  formErrors.value = ''

  if (!formData.name) {
    formErrors.name = '请输入参数名称'
    valid = false
  }

  if (!formData.parameter_type_id) {
    formErrors.parameter_type_id = '请选择参数类型'
    valid = false
  }

  if (!formData.rule_id) {
    formErrors.rule_id = '请选择核保规则'
    valid = false
  }

  if (!formData.value) {
    formErrors.value = '请输入参数值'
    valid = false
  }

  return valid
}

// 新增
const handleAdd = () => {
  modalType.value = 'add'
  currentId.value = undefined
  formData.name = ''
  formData.parameter_type_id = undefined
  formData.rule_id = undefined
  formData.value = ''
  formData.description = undefined
  formData.status = ParameterStatus.ENABLED
  showModal.value = true
}

// 编辑
const handleEdit = (item: Parameter) => {
  modalType.value = 'edit'
  currentId.value = item.id
  formData.name = item.name
  formData.parameter_type_id = item.parameter_type_id
  formData.rule_id = item.rule_id
  formData.value = item.value
  formData.description = item.description
  formData.status = item.status as ParameterStatus
  showModal.value = true
}

// 删除
const handleDelete = async (item: Parameter) => {
  try {
    await message.confirm(`确定要删除参数"${item.name}"吗？`)
    const res = await deleteParameter(item.id)
    if (res.code === 200) {
      message.success('删除成功')
      loadData()
    } else {
      message.error(res.message || '删除失败')
    }
  } catch (error: any) {
    console.error('删除失败:', error)
    message.error(error.message || '删除失败')
  }
}

// 弹窗确认
const handleModalConfirm = async () => {
  if (!validateForm()) return

  try {
    const requestData = {
      name: formData.name,
      parameter_type_id: formData.parameter_type_id,
      rule_id: formData.rule_id,
      value: formData.value,
      description: formData.description || '',
      status: formData.status
    }

    if (modalType.value === 'add') {
      const res = await createParameter(requestData)
      if (res.code === 200) {
        message.success('创建成功')
        showModal.value = false
        loadData()
      } else {
        message.error(res.message || '创建失败')
      }
    } else if (currentId.value) {
      const res = await updateParameter(currentId.value, requestData)
      if (res.code === 200) {
        message.success('更新成功')
        showModal.value = false
        loadData()
      } else {
        message.error(res.message || '更新失败')
      }
    }
  } catch (error: any) {
    console.error('保存失败:', error)
    message.error(error.message || '保存失败')
  }
}

// 监听路由参数变化
watch(
  () => route.query.refresh,
  () => {
    if (route.query.refresh) {
      loadData()
    }
  }
)

onMounted(() => {
  loadParameterTypes()
  loadRules()
  loadData()
})
</script>

<style lang="scss" scoped>
.ai-parameter-page {
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

.parameter-table {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
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

.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
  
  :deep(.base-button) {
    min-width: 60px;
  }
}

.status-text {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 2px;
  font-size: 12px;
  
  &.status-enabled {
    color: var(--color-success);
    background: color-mix(in srgb, var(--color-success) 10%, transparent);
  }
  
  &.status-disabled {
    color: var(--color-error);
    background: color-mix(in srgb, var(--color-error) 10%, transparent);
  }
}

// 修改弹窗表单样式
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
</style> 