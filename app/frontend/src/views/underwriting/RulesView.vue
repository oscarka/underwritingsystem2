<template>
  <div class="rules-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>核保规则管理</h1>
      <div class="header-actions">
        <BaseButton type="primary" @click="handleCreate">新增规则</BaseButton>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <BaseInput 
        v-model="searchQuery.name" 
        placeholder="搜索规则名称"
        style="width: 300px"
      />
      <BaseSelect
        v-model="searchQuery.status"
        :options="statusOptions"
        placeholder="规则状态"
        style="width: 200px"
      />
      <BaseSelect
        v-model="searchQuery.diseaseCategory"
        :options="diseaseCategoryOptions"
        placeholder="疾病类别"
        style="width: 200px"
      />
      <BaseButton @click="handleSearch">搜索</BaseButton>
      <BaseButton @click="handleReset">重置</BaseButton>
    </div>

    <!-- 数据表格 -->
    <div class="rules-table">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <div class="skeleton-row" v-for="i in 5" :key="i">
          <div class="skeleton-cell" v-for="j in 6" :key="j"></div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!rules.length" class="empty-state">
        <span class="icon">📭</span>
        <p>暂无数据</p>
      </div>

      <!-- 数据表格 -->
      <table v-else>
        <thead>
          <tr>
            <th>ID</th>
            <th>核保规则名称</th>
            <th>核保规则版本</th>
            <th>规则状态</th>
            <th>备注</th>
            <th>创建时间</th>
            <th>编辑时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rule in rules" :key="rule.id">
            <td>{{ rule.id }}</td>
            <td>{{ rule.name }}</td>
            <td>{{ rule.version }}</td>
            <td>
              <span :class="['status-badge', getStatusColor(rule.status)]">
                {{ rule.status }}
              </span>
            </td>
            <td>{{ rule.remark || '-' }}</td>
            <td>{{ rule.createdAt }}</td>
            <td>{{ rule.updatedAt }}</td>
            <td>
              <div class="action-buttons">
                <BaseButton size="small" @click="handleView(rule)">查看</BaseButton>
                <BaseButton size="small" @click="handleViewConfig(rule)">查看规则</BaseButton>
                <BaseButton size="small" @click="handleEdit(rule)">编辑</BaseButton>
                <BaseButton size="small" @click="handleImport(rule)">导入</BaseButton>
                <BaseButton v-if="rule.has_data" size="small" @click="handleExport(rule)">导出</BaseButton>
                <BaseButton size="small" type="danger" @click="handleDelete(rule)">删除</BaseButton>
              </div>
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
      :title="modalType === 'add' ? '新增规则' : '编辑规则'"
      width="500px"
      @confirm="handleModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>规则名称</label>
          <BaseInput
            v-model="formData.name"
            placeholder="请输入规则名称"
            :maxlength="50"
          />
          <div class="form-error" v-if="formErrors.name">
            {{ formErrors.name }}
          </div>
        </div>
        
        <div class="form-item">
          <label>版本号</label>
          <BaseInput
            v-model="formData.version"
            placeholder="请输入版本号"
            :maxlength="30"
            :disabled="modalType === 'edit'"
          />
          <div class="form-error" v-if="formErrors.version">
            {{ formErrors.version }}
          </div>
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
      </div>
    </BaseModal>

    <!-- 导入规则弹窗 -->
    <BaseModal
      v-model="showImportModal"
      title="导入规则"
      width="500px"
      @confirm="handleImportConfirm"
      @cancel="handleImportCancel"
      :confirmLoading="importLoading"
    >
      <div class="form">
        <div class="form-item">
          <label>选择文件</label>
          <BaseUpload
            v-model="importFile"
            accept=".xlsx,.xls"
            :maxSize="10"
            placeholder="请选择Excel文件"
            @error="handleUploadError"
          />
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, defineProps } from 'vue'
import { useRouter } from 'vue-router'
import type { Rule, DiseaseCategory, RuleStatus, RuleSearchParams } from '@/types/underwriting'
import type { ApiResponse, PaginationQuery, PaginationData } from '@/types/api'
import ruleApi from '@/api/underwriting'
import { showToast } from '@/utils/toast'

// 路由实例
const router = useRouter()

// 加载状态
const loading = ref(false)

// 弹窗控制
const showModal = ref(false)
const showImportModal = ref(false)
const modalType = ref<'add' | 'edit'>('add')
const importFile = ref<File | null>(null)
const importLoading = ref(false)

// 表单数据
const formData = reactive({
  name: '',
  version: '',
  remark: ''
})

// 表单错误
const formErrors = reactive({
  name: '',
  version: ''
})

// 当前编辑的规则ID
const currentId = ref<string>('')

// 状态选项
const statusOptions = [
  { label: '已导入', value: '已导入' },
  { label: '已启用', value: '已启用' },
  { label: '已禁用', value: '已禁用' }
]

// 疾病类别选项
const diseaseCategoryOptions = ref<{ label: string; value: string }[]>([])

// 查询参数
const searchQuery = reactive<RuleSearchParams>({
  name: '',
  status: undefined,
  diseaseCategory: undefined,
  page: 1,
  pageSize: 10
})

// 分页参数
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 规则列表
const rules = ref<Rule[]>([])

// 定义props
const props = defineProps({
  confirmLoading: {
    type: Boolean,
    default: false
  },
  onNodeUnmounted: {
    type: Function,
    default: () => {}
  }
})

// 显示提示信息
const toast = (options: { type: 'success' | 'error' | 'warning' | 'info', message: string }) => {
  showToast(options.type, options.message)
}

// 获取规则列表
const fetchRules = async () => {
  console.log('开始加载核保规则列表:', searchQuery)
  
  loading.value = true
  try {
    const res = await ruleApi.getRules(searchQuery)
    
    console.log('核保规则响应:', res)
    
    if (res.code === 200) {
      rules.value = res.data.list || []
      total.value = res.data.total || 0
      console.log('核保规则加载成功:', {
        list: rules.value,
        total: total.value
      })
    } else {
      console.error('加载核保规则失败:', res.message)
      toast({ type: 'error', message: res.message || '加载失败' })
      rules.value = []
      total.value = 0
    }
  } catch (error: any) {
    console.error('加载核保规则列表失败:', error)
    toast({ type: 'error', message: error.message || '加载失败' })
    rules.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 获取疾病类别选项
const fetchDiseaseCategories = async () => {
  try {
    const response = await ruleApi.getDiseaseCategories('all')
    if (response.code === 200 && response.data) {
      diseaseCategoryOptions.value = response.data.map((category: DiseaseCategory) => ({
        label: category.name,
        value: category.code
      }))
    } else {
      toast({ type: 'error', message: response.message || '获取疾病类别失败' })
    }
  } catch (error) {
    toast({ type: 'error', message: '获取疾病类别失败' })
  }
}

// 搜索
const handleSearch = () => {
  searchQuery.page = 1
  fetchRules()
}

// 重置
const handleReset = () => {
  searchQuery.name = ''
  searchQuery.status = undefined
  searchQuery.diseaseCategory = undefined
  searchQuery.page = 1
  fetchRules()
}

// 分页变化
const handlePageChange = () => {
  searchQuery.page = page.value
  searchQuery.pageSize = pageSize.value
  fetchRules()
}

// 新增规则
const handleCreate = () => {
  modalType.value = 'add'
  formData.name = ''
  formData.version = ''
  formData.remark = ''
  showModal.value = true
}

// 编辑规则
const handleEdit = (rule: Rule) => {
  modalType.value = 'edit'
  currentId.value = rule.id
  formData.name = rule.name
  formData.version = rule.version
  formData.remark = rule.remark || ''
  showModal.value = true
}

// 查看规则
const handleView = (rule: Rule) => {
  console.log('[RulesView] 点击查看按钮:', {
    id: rule.id,
    name: rule.name,
    version: rule.version
  });
  router.push(`/underwriting/rules/${rule.id}/detail`);
}

// 查看规则配置
const handleViewConfig = (rule: Rule) => {
  console.log('[RulesView] 点击查看规则按钮:', {
    id: rule.id,
    name: rule.name,
    version: rule.version
  });
  router.push(`/underwriting/rules/${rule.id}/detail`);
}

// 导出规则
const handleExport = async (rule: Rule) => {
  try {
    const response = await ruleApi.exportRuleData(rule.id)
    if (response.code === 200 && response.data) {
      const blob = new Blob([response.data], { type: 'application/vnd.ms-excel' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${rule.name}-${rule.version}.xlsx`
      link.click()
      window.URL.revokeObjectURL(url)
      toast({ type: 'success', message: '导出成功' })
    } else {
      toast({ type: 'error', message: response.message || '导出失败' })
    }
  } catch (error) {
    toast({ type: 'error', message: '导出失败' })
  }
}

// 导入规则
const handleImport = (rule: Rule) => {
  console.log('[RulesView] 点击导入按钮:', {
    id: rule.id,
    name: rule.name,
    version: rule.version
  });
  currentId.value = rule.id;
  importFile.value = null; // 重置文件
  showImportModal.value = true;
}

// 确认导入
const handleImportConfirm = async () => {
  console.log('[RulesView] 确认导入:', {
    ruleId: currentId.value,
    hasFile: !!importFile.value,
    fileName: importFile.value?.name
  });

  if (!importFile.value) {
    toast({ type: 'error', message: '请选择要导入的文件' })
    return
  }

  if (!currentId.value) {
    toast({ type: 'error', message: '未找到规则ID' })
    return
  }

  try {
    importLoading.value = true
    console.log('[RulesView] 开始导入规则数据:', {
      ruleId: currentId.value,
      fileName: importFile.value.name,
      fileSize: importFile.value.size,
      fileType: importFile.value.type
    })
    
    const response = await ruleApi.importRuleData(currentId.value, importFile.value)
    console.log('[RulesView] 导入响应:', {
      code: response.code,
      message: response.message
    })

    if (response.code === 200) {
      toast({ type: 'success', message: '导入成功' })
      showImportModal.value = false
      importFile.value = null
      currentId.value = ''
      await fetchRules()
    } else {
      toast({ type: 'error', message: response.message || '导入失败' })
    }
  } catch (error: any) {
    console.error('[RulesView] 导入失败:', error)
    toast({ type: 'error', message: error?.message || '导入失败' })
  } finally {
    importLoading.value = false
  }
}

// 取消导入
const handleImportCancel = () => {
  console.log('[RulesView] 取消导入')
  showImportModal.value = false
  importFile.value = null
  currentId.value = ''
}

// 确认新增/编辑
const handleModalConfirm = async () => {
  // 表单验证
  formErrors.name = !formData.name ? '请输入规则名称' : ''
  formErrors.version = !formData.version ? '请输入版本号' : ''
  if (formErrors.name || formErrors.version) {
    return
  }

  try {
    let response
    if (modalType.value === 'add') {
      response = await ruleApi.createRule(formData)
    } else {
      response = await ruleApi.updateRule(currentId.value, formData)
    }

    if (response.code === 200) {
      toast({ 
        type: 'success', 
        message: modalType.value === 'add' ? '新增成功' : '编辑成功' 
      })
      showModal.value = false
      fetchRules()
    } else {
      toast({ 
        type: 'error', 
        message: response.message || (modalType.value === 'add' ? '新增失败' : '编辑失败')
      })
    }
  } catch (error) {
    toast({ 
      type: 'error', 
      message: modalType.value === 'add' ? '新增失败' : '编辑失败' 
    })
  }
}

// 删除规则
const handleDelete = async (rule: Rule) => {
  try {
    if (!confirm(`确认删除规则"${rule.name}"吗？`)) return;
    
    console.log('[RulesView] 开始删除规则:', {
      id: rule.id,
      name: rule.name
    });
    
    const res = await ruleApi.deleteRule(rule.id);
    if (res.code === 200) {
      toast({
        type: 'success',
        message: '删除成功'
      });
      fetchRules();
    }
  } catch (error) {
    console.error('[RulesView] 删除规则失败:', error);
    toast({
      type: 'error',
      message: '删除失败'
    });
  }
};

// 获取状态对应的样式类
const getStatusColor = (status: string) => {
  switch (status) {
    case '已启用':
      return 'success';
    case '已导入':
      return 'processing';
    case '草稿':
      return 'default';
    case '已禁用':
      return 'error';
    default:
      return 'default';
  }
};

// 处理上传错误
const handleUploadError = (error: { type: string; message: string }) => {
  console.log('[RulesView] 文件上传错误:', error)
  toast({ type: 'error', message: error.message })
}

// 初始化
onMounted(() => {
  fetchRules()
  fetchDiseaseCategories()
})
</script>

<style scoped>
.rules-page {
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

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.search-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.rules-table {
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

.status-badge.已导入 {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.status-badge.启用 {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status-badge.禁用 {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
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