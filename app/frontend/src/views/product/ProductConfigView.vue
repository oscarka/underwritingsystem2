# 产品配置页面
<template>
  <div class="product-config-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>产品配置</h1>
      <BaseButton type="primary" @click="handleAdd">新增产品</BaseButton>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <BaseInput 
        v-model="searchQuery.name" 
        placeholder="搜索产品名称"
        style="width: 300px"
      />
      <BaseInput 
        v-model="searchQuery.code" 
        placeholder="搜索产品代码"
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
    <div class="product-table">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <div class="skeleton-row" v-for="i in 5" :key="i">
          <div class="skeleton-cell" v-for="j in 6" :key="j"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!productList.length" class="empty-state">
        <span class="icon">📭</span>
        <p>暂无数据</p>
      </div>

      <!-- 表格内容 -->
      <table v-else>
        <thead>
          <tr>
            <th>产品名称</th>
            <th>产品代码</th>
            <th>所属渠道</th>
            <th>承保公司</th>
            <th>产品类型</th>
            <th>智核参数</th>
            <th>核保规则</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in productList" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.code }}</td>
            <td>{{ item.channel?.name || '-' }}</td>
            <td>{{ item.insuranceCompany?.name || '-' }}</td>
            <td>{{ item.productType?.name || '-' }}</td>
            <td>{{ item.aiParameter?.name || '-' }}</td>
            <td>{{ item.aiParameter?.rule?.name || '-' }}</td>
            <td>
              <span class="status-badge" :class="item.status">
                {{ item.status === 'enabled' ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ item.createdAt }}</td>
            <td class="operation-column">
              <BaseButton size="small" @click="handleEdit(item)">编辑</BaseButton>
              <BaseButton 
                size="small" 
                type="danger" 
                @click="handleDelete(item)"
              >删除</BaseButton>
              <BaseButton 
                size="small" 
                type="primary" 
                @click="handleGenerateLink(item)"
                :disabled="item.status !== 'enabled'"
              >生成链接</BaseButton>
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
      :title="modalType === 'add' ? '新增产品' : '编辑产品'"
      width="500px"
      @confirm="handleModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>产品名称</label>
          <BaseInput
            v-model="formData.name"
            placeholder="请输入产品名称"
            :maxlength="50"
          />
          <div class="form-error" v-if="formErrors.name">
            {{ formErrors.name }}
          </div>
        </div>
        
        <div class="form-item">
          <label>产品代码</label>
          <BaseInput
            v-model="formData.product_code"
            placeholder="请输入产品代码"
            :maxlength="30"
            :disabled="modalType === 'edit'"
          />
          <div class="form-error" v-if="formErrors.product_code">
            {{ formErrors.product_code }}
          </div>
        </div>

        <div class="form-item">
          <label>所属渠道</label>
          <BaseSelect
            v-model="formData.channel_id"
            :options="channelOptions"
            placeholder="请选择所属渠道"
          />
          <div class="form-error" v-if="formErrors.channel_id">
            {{ formErrors.channel_id }}
          </div>
        </div>

        <div class="form-item">
          <label>承保公司</label>
          <BaseSelect
            v-model="formData.insurance_company_id"
            :options="companyOptions"
            placeholder="请选择承保公司"
          />
          <div class="form-error" v-if="formErrors.insurance_company_id">
            {{ formErrors.insurance_company_id }}
          </div>
        </div>

        <div class="form-item">
          <label>产品类型</label>
          <BaseSelect
            v-model="formData.product_type_id"
            :options="productTypeOptions"
            placeholder="请选择产品类型"
          />
          <div class="form-error" v-if="formErrors.product_type_id">
            {{ formErrors.product_type_id }}
          </div>
        </div>

        <div class="form-item">
          <label>智核参数</label>
          <BaseSelect
            v-model="formData.ai_parameter_id"
            :options="aiParameterOptions"
            placeholder="请选择智核参数"
            @change="handleAiParameterChange"
          />
          <div class="form-error" v-if="formErrors.ai_parameter_id">
            {{ formErrors.ai_parameter_id }}
          </div>
        </div>

        <div class="form-item">
          <label>核保规则</label>
          <BaseInput
            v-model="formData.underwriting_rule"
            placeholder="选择智核参数后自动显示"
            disabled
          />
        </div>

        <div class="form-item">
          <label>状态</label>
          <BaseSelect
            v-model="formData.status"
            :options="statusOptions"
            placeholder="请选择状态"
          />
          <div class="form-error" v-if="formErrors.status">
            {{ formErrors.status }}
          </div>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from '@/composables/useMessage'
import type { Product, ProductStatus } from '@/types/product'
import { get, post, put, del } from '../../utils/request'
import type { ApiResponse } from '../../utils/request'
import { useClipboard } from '@vueuse/core'
import { Dialog } from '@/components/base'

// 添加移动端基础URL配置
const mobileBaseUrl = ref(import.meta.env.VITE_MOBILE_BASE_URL || 'http://localhost:3001');

// 添加工具函数
function getToken() {
  return localStorage.getItem('token')
}

function isLoggedIn() {
  return !!getToken()
}

const message = useMessage()

// 添加接口返回类型定义
interface SelectOption {
  value: number
  label: string
}

interface Channel {
  id: number
  name: string
  code: string
}

interface Company {
  id: number
  name: string
  code: string
}

interface ProductType {
  id: number
  name: string
  code: string
}

interface AIParameter {
  id: number
  name: string
  rule?: {
    id: number
    name: string
  }
}

interface PaginationData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

type PaginatedResponse<T> = ApiResponse<PaginationData<T>>

// 选项数据
const channelOptions = ref<SelectOption[]>([])
const companyOptions = ref<SelectOption[]>([])
const productTypeOptions = ref<SelectOption[]>([])
const aiParameterOptions = ref<SelectOption[]>([])

// 加载选项数据
const loadOptions = async () => {
  const token = getToken();
  console.log('[选项加载] ===== 开始加载选项数据 =====');
  console.log('[选项加载] 认证信息:', {
    tokenExists: !!token,
    tokenLength: token?.length || 0
  });

  try {
    // 获取渠道选项
    console.log('准备请求渠道数据');
    const channelRes: PaginatedResponse<Channel> = await get('/api/v1/business/channels')
    const channelData = channelRes.data
    console.log('渠道数据响应:', {
      code: channelRes.code,
      message: channelRes.message,
      dataLength: channelData?.list?.length
    });
    if (channelData?.list && Array.isArray(channelData.list)) {
      channelOptions.value = channelData.list.map((item: Channel) => ({
        value: item.id,
        label: item.name
      }))
    }

    // 获取保险公司选项
    console.log('准备请求保险公司数据');
    const companyRes: PaginatedResponse<Company> = await get('/api/v1/business/companies')
    const companyData = companyRes.data
    console.log('保险公司数据响应:', {
      code: companyRes.code,
      message: companyRes.message,
      dataLength: companyData?.list?.length
    });
    if (companyData?.list && Array.isArray(companyData.list)) {
      companyOptions.value = companyData.list.map((item: Company) => ({
        value: item.id,
        label: item.name
      }))
    }

    // 获取产品类型选项
    console.log('[选项加载] 开始请求产品类型数据');
    const typeRes: PaginatedResponse<ProductType> = await get('/api/v1/business/product-types')
    console.log('[选项加载] 产品类型API响应:', typeRes);
    
    const typeData = typeRes.data
    console.log('[选项加载] 产品类型原始数据:', typeData);
    
    if (typeData?.list && Array.isArray(typeData.list)) {
      productTypeOptions.value = typeData.list.map((item: ProductType) => ({
        value: item.id,
        label: item.name
      }))
    } else if (Array.isArray(typeData)) {
      productTypeOptions.value = typeData.map((item: ProductType) => ({
        value: item.id,
        label: item.name
      }))
    }
    console.log('[选项加载] 处理后的产品类型选项:', productTypeOptions.value);

    // 获取AI参数选项
    console.log('准备请求AI参数数据');
    const paramRes: PaginatedResponse<AIParameter> = await get('/api/v1/underwriting/ai-parameter/')
    const paramData = paramRes.data
    console.log('AI参数数据响应:', {
      code: paramRes.code,
      message: paramRes.message,
      dataLength: paramData?.list?.length
    });
    if (paramData?.list && Array.isArray(paramData.list)) {
      aiParameterOptions.value = paramData.list.map((item: AIParameter) => ({
        value: item.id,
        label: item.name
      }))
    }
  } catch (error: any) {
    console.error('[选项加载] 加载失败:', {
      error,
      name: error.name,
      message: error.message,
      response: {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      },
      request: {
        method: error.config?.method,
        url: error.config?.url,
        headers: error.config?.headers
      }
    });
    message.error(error.message || '加载选项数据失败')
  }
  console.log('[选项加载] ===== 加载选项数据结束 =====');
}

// 查询参数
const searchQuery = reactive({
  name: '',
  code: '',
  status: undefined as ProductStatus | undefined
})

// 状态选项
const statusOptions = [
  { value: 'enabled', label: '启用' },
  { value: 'disabled', label: '禁用' }
]

// 分页参数
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 产品列表
const productList = ref<Product[]>([])
const loading = ref(false)

// 弹窗控制
const showModal = ref(false)
const modalType = ref<'add' | 'edit'>('add')
const currentId = ref<number>()
const formData = reactive({
  name: '',
  product_code: '',
  product_type_id: undefined as number | undefined,
  insurance_company_id: undefined as number | undefined,
  channel_id: undefined as number | undefined,
  ai_parameter_id: undefined as number | undefined,
  underwriting_rule: '' as string,
  status: 'enabled' as ProductStatus
})

const formErrors = reactive({
  name: '',
  product_code: '',
  channel_id: '',
  insurance_company_id: '',
  product_type_id: '',
  ai_parameter_id: '',
  status: ''
})

const { copy } = useClipboard();

// 加载数据
const loadData = async () => {
  const token = getToken();
  console.log('[产品列表] ===== 开始加载产品配置数据 =====');
  console.log('[产品列表] 认证信息:', {
    tokenExists: !!token,
    tokenLength: token?.length || 0
  });

  try {
    loading.value = true
    const params = {
      page: page.value,
      pageSize: pageSize.value,
      name: searchQuery.name || undefined,
      code: searchQuery.code || undefined,
      status: searchQuery.status
    };
    console.log('[产品列表] 请求参数:', params);

    console.log('[产品列表] 发起API请求...');
    const response = await get('/api/v1/business/products', { params });
    console.log('[产品列表] API响应原始数据:', response);

    if (!response) {
      console.error('[产品列表] API响应为空');
      throw new Error('获取数据失败');
    }

    if (response.code !== 200) {
      console.error('[产品列表] API响应状态码异常:', response.code);
      throw new Error(response.message || '获取数据失败');
    }

    const productData = response.data;
    console.log('[产品列表] 解析后的数据:', productData);

    if (!productData) {
      console.error('[产品列表] 响应数据为空');
      productList.value = [];
      total.value = 0;
      return;
    }

    // 检查数据结构
    if (productData.list && Array.isArray(productData.list)) {
      console.log('[产品列表] 数据格式正确，包含list数组');
      productList.value = productData.list;
      total.value = productData.total || 0;
      console.log('[产品列表] 更新后的状态:', {
        listLength: productList.value.length,
        total: total.value,
        firstItem: productList.value[0]
      });
    } else if (Array.isArray(productData)) {
      console.log('[产品列表] 数据直接是数组格式');
      productList.value = productData;
      total.value = productData.length;
      console.log('[产品列表] 更新后的状态:', {
        listLength: productList.value.length,
        total: total.value,
        firstItem: productList.value[0]
      });
    } else {
      console.error('[产品列表] 数据格式异常:', productData);
      productList.value = [];
      total.value = 0;
    }
  } catch (error: any) {
    console.error('[产品列表] 加载失败:', {
      error,
      name: error.name,
      message: error.message,
      response: {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      },
      request: {
        method: error.config?.method,
        url: error.config?.url,
        headers: error.config?.headers,
        params: error.config?.params
      }
    });
    message.error(error.message || '加载数据失败，请重试');
    productList.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
    console.log('[产品列表] ===== 加载产品配置数据结束 =====');
  }
}

// 搜索
function handleSearch() {
  console.log('[产品列表] 执行搜索，搜索条件:', searchQuery);
  page.value = 1;
  loadData();
}

// 重置
function handleReset() {
  console.log('[产品列表] 执行重置');
  searchQuery.name = '';
  searchQuery.code = '';
  searchQuery.status = undefined;
  page.value = 1;
  loadData();
}

// 分页变化
function handlePageChange() {
  loadData()
}

// 表单验证
function validateForm() {
  let valid = true
  formErrors.name = ''
  formErrors.product_code = ''
  formErrors.channel_id = ''
  formErrors.insurance_company_id = ''
  formErrors.product_type_id = ''
  formErrors.ai_parameter_id = ''
  formErrors.status = ''

  if (!formData.name) {
    formErrors.name = '请输入产品名称'
    valid = false
  } else if (formData.name.length > 50) {
    formErrors.name = '产品名称不能超过50个字符'
    valid = false
  }

  if (!formData.product_code) {
    formErrors.product_code = '请输入产品代码'
    valid = false
  } else if (formData.product_code.length > 30) {
    formErrors.product_code = '产品代码不能超过30个字符'
    valid = false
  } else if (!/^[A-Z0-9_]+$/.test(formData.product_code)) {
    formErrors.product_code = '产品代码只能包含大写字母、数字和下划线'
    valid = false
  }

  if (!formData.channel_id) {
    formErrors.channel_id = '请选择所属渠道'
    valid = false
  }

  if (!formData.insurance_company_id) {
    formErrors.insurance_company_id = '请选择承保公司'
    valid = false
  }

  if (!formData.product_type_id) {
    formErrors.product_type_id = '请选择产品类型'
    valid = false
  }

  if (!formData.ai_parameter_id) {
    formErrors.ai_parameter_id = '请选择智核参数'
    valid = false
  }

  if (!formData.status) {
    formErrors.status = '请选择状态'
    valid = false
  }

  return valid
}

// 新增
function handleAdd() {
  modalType.value = 'add'
  formData.name = ''
  formData.product_code = ''
  formData.product_type_id = undefined
  formData.insurance_company_id = undefined
  formData.channel_id = undefined
  formData.ai_parameter_id = undefined
  formData.status = 'enabled'
  showModal.value = true
}

// 编辑
function handleEdit(item: Product) {
  modalType.value = 'edit'
  currentId.value = item.id
  formData.name = item.name
  formData.product_code = item.code
  formData.product_type_id = item.productType?.id
  formData.insurance_company_id = item.insuranceCompany?.id
  formData.channel_id = item.channel?.id
  formData.ai_parameter_id = item.aiParameter?.id
  formData.underwriting_rule = item.aiParameter?.rule?.name || ''
  formData.status = item.status
  showModal.value = true
}

// 弹窗确认
async function handleModalConfirm() {
  if (!validateForm()) return

  try {
    if (modalType.value === 'add') {
      await handleCreate()
    } else {
      await handleUpdate()
    }
  } catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败，请重试')
  }
}

// 创建产品
async function handleCreate() {
  try {
    const res = await post<ApiResponse<any>>('/api/v1/business/products', {
      name: formData.name,
      product_code: formData.product_code,
      product_type_id: formData.product_type_id,
      insurance_company_id: formData.insurance_company_id,
      channel_id: formData.channel_id,
      ai_parameter_id: formData.ai_parameter_id,
      status: formData.status
    })
    
    message.success('创建成功')
    showModal.value = false
    loadData()
  } catch (error: any) {
    console.error('创建产品失败:', error)
    message.error(error.message || '创建失败，请重试')
  }
}

// 更新产品
async function handleUpdate() {
  if (!currentId.value) return
  
  try {
    const res = await put<ApiResponse<any>>(`/api/v1/business/products/${currentId.value}`, {
      name: formData.name,
      product_code: formData.product_code,
      product_type_id: formData.product_type_id,
      insurance_company_id: formData.insurance_company_id,
      channel_id: formData.channel_id,
      ai_parameter_id: formData.ai_parameter_id,
      status: formData.status
    })
    
    message.success('更新成功')
    showModal.value = false
    loadData()
  } catch (error: any) {
    console.error('更新产品失败:', error)
    message.error(error.message || '更新失败，请重试')
  }
}

// 删除产品
async function handleDelete(item: Product) {
  try {
    await message.confirm(`确认删除产品"${item.name}"吗？`)
    const res = await del<ApiResponse<any>>(`/api/v1/business/products/${item.id}`)
    
    message.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error === 'cancel') return
    console.error('删除产品失败:', error)
    message.error(error.message || '删除失败，请重试')
  }
}

// 修改智核参数变更处理函数
async function handleAiParameterChange(value: number | undefined) {
  console.log('[智核参数] 参数变更:', value);
  formData.underwriting_rule = '';  // 清空原有规则
  
  if (!value) {
    return;
  }

  try {
    // 从已加载的AI参数选项中查找对应的规则
    const selectedParam = aiParameterOptions.value.find(option => option.value === value);
    if (selectedParam) {
      const paramData = await get(`/api/v1/underwriting/ai-parameter/${value}`);
      console.log('[智核参数] 获取规则信息:', paramData);
      
      if (paramData.data?.rule?.name) {
        formData.underwriting_rule = paramData.data.rule.name;
      }
    }
  } catch (error) {
    console.error('[智核参数] 获取规则信息失败:', error);
  }
}

// 生成移动核保链接
async function handleGenerateLink(item: Product) {
  try {
    const url = `${mobileBaseUrl.value}/product/${item.id}`;
    await copy(url);
    message.success('链接已复制到剪贴板');
    
    // 显示链接详情
    Dialog.show({
      title: '移动核保链接',
      content: `
        <div style="word-break: break-all;">
          <p>产品名称: ${item.name}</p>
          <p>链接地址: ${url}</p>
          <p style="color: #666; font-size: 14px;">提示: 链接已自动复制到剪贴板</p>
        </div>
      `,
      confirmText: '确定'
    });
  } catch (error) {
    console.error('生成链接失败:', error);
    message.error('生成链接失败');
  }
}

onMounted(async () => {
  console.log('[产品列表] ===== 组件挂载 =====');
  console.log('[产品列表] 初始认证状态:', {
    token: getToken()?.slice(0, 10) + '...',
    isLoggedIn: isLoggedIn()
  });
  
  await loadOptions()
  await loadData()
})
</script>

<style lang="scss" scoped>
.product-config-page {
  padding: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);

  h1 {
    margin: 0;
    font-size: var(--font-size-xl);
    color: var(--color-text-primary);
  }
}

.search-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.product-table {
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
  flex: 1;
  height: 24px;
  background: var(--color-bg-spotlight);
  border-radius: var(--border-radius-sm);
  animation: pulse 1.5s infinite;
}

.empty-state {
  padding: var(--spacing-xl) 0;
  text-align: center;
  color: var(--color-text-secondary);

  .icon {
    font-size: 48px;
    margin-bottom: var(--spacing-md);
  }

  p {
    margin: 0;
  }
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

.operation-column {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;

  :deep(.base-button) {
    min-width: 64px;
  }
}

.form {
  .form-item {
    margin-bottom: var(--spacing-md);

    label {
      display: block;
      margin-bottom: var(--spacing-xs);
      color: var(--color-text-secondary);
    }

    .form-error {
      margin-top: var(--spacing-xs);
      color: var(--color-error);
      font-size: var(--font-size-sm);
    }
  }
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: var(--spacing-md) 0;
  margin-top: var(--spacing-lg);
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}
</style> 