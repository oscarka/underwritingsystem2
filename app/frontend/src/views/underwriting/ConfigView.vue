# 核保配置页面
<template>
  <div class="config-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>核保配置</h1>
    </div>

    <!-- 标签页 -->
    <div class="config-tabs">
      <BaseTabs v-model="activeTab">
        <BaseTabPane key="disease-categories" tab="疾病大类">
          <div class="section">
            <div class="section-header">
              <BaseButton type="primary" @click="handleAddCategory">新增疾病大类</BaseButton>
            </div>
            <table>
              <thead>
                <tr>
                  <th>编码</th>
                  <th>疾病大类名称</th>
                  <th>显示顺序</th>
                  <th>修改时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in diseaseCategories" :key="item.code">
                  <td>{{ item.code }}</td>
                  <td>{{ item.name }}</td>
                  <td>{{ item.displayOrder }}</td>
                  <td>{{ item.updatedAt }}</td>
                  <td>
                    <div class="action-buttons">
                      <BaseButton size="small" @click="handleEditCategory(item)">编辑</BaseButton>
                      <BaseButton size="small" type="danger" @click="handleDeleteCategory(item)">删除</BaseButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseTabPane>

        <BaseTabPane key="diseases" tab="疾病列表">
          <div class="section">
            <div class="section-header">
              <BaseButton type="primary" @click="handleAddDisease">新增疾病</BaseButton>
            </div>
            <table>
              <thead>
                <tr>
                  <th>编码</th>
                  <th>疾病名称</th>
                  <th>所属大类</th>
                  <th>是否常见病</th>
                  <th>修改时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in diseases" :key="item.code">
                  <td>{{ item.code }}</td>
                  <td>{{ item.name }}</td>
                  <td>{{ getDiseaseCategory(item.categoryCode) }}</td>
                  <td>{{ item.isCommon ? '是' : '否' }}</td>
                  <td>{{ item.updatedAt }}</td>
                  <td>
                    <div class="action-buttons">
                      <BaseButton size="small" @click="handleEditDisease(item)">编辑</BaseButton>
                      <BaseButton size="small" type="danger" @click="handleDeleteDisease(item)">删除</BaseButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseTabPane>
      </BaseTabs>
    </div>

    <!-- 疾病大类弹窗 -->
    <BaseModal
      v-model="showCategoryModal"
      :title="categoryModalType === 'add' ? '新增疾病大类' : '编辑疾病大类'"
      width="500px"
      @confirm="handleCategoryModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>编码</label>
          <BaseInput
            v-model="categoryForm.code"
            placeholder="请输入编码"
            :maxlength="20"
            :disabled="categoryModalType === 'edit'"
          />
          <div class="form-error" v-if="categoryFormErrors.code">
            {{ categoryFormErrors.code }}
          </div>
        </div>

        <div class="form-item">
          <label>疾病大类名称</label>
          <BaseInput
            v-model="categoryForm.name"
            placeholder="请输入疾病大类名称"
            :maxlength="50"
          />
          <div class="form-error" v-if="categoryFormErrors.name">
            {{ categoryFormErrors.name }}
          </div>
        </div>

        <div class="form-item">
          <label>显示顺序</label>
          <BaseInput
            v-model.number="categoryForm.displayOrder"
            type="number"
            placeholder="请输入显示顺序"
            :min="1"
          />
          <div class="form-error" v-if="categoryFormErrors.displayOrder">
            {{ categoryFormErrors.displayOrder }}
          </div>
        </div>
      </div>
    </BaseModal>

    <!-- 疾病弹窗 -->
    <BaseModal
      v-model="showDiseaseModal"
      :title="diseaseModalType === 'add' ? '新增疾病' : '编辑疾病'"
      width="500px"
      @confirm="handleDiseaseModalConfirm"
    >
      <div class="form">
        <div class="form-item">
          <label>编码</label>
          <BaseInput
            v-model="diseaseForm.code"
            placeholder="请输入编码"
            :maxlength="20"
            :disabled="diseaseModalType === 'edit'"
          />
          <div class="form-error" v-if="diseaseFormErrors.code">
            {{ diseaseFormErrors.code }}
          </div>
        </div>

        <div class="form-item">
          <label>疾病名称</label>
          <BaseInput
            v-model="diseaseForm.name"
            placeholder="请输入疾病名称"
            :maxlength="50"
          />
          <div class="form-error" v-if="diseaseFormErrors.name">
            {{ diseaseFormErrors.name }}
          </div>
        </div>

        <div class="form-item">
          <label>所属大类</label>
          <BaseSelect
            v-model="diseaseForm.categoryCode"
            :options="categoryOptions"
            placeholder="请选择所属大类"
          />
          <div class="form-error" v-if="diseaseFormErrors.categoryCode">
            {{ diseaseFormErrors.categoryCode }}
          </div>
        </div>

        <div class="form-item">
          <label>是否常见病</label>
          <BaseSwitch v-model="diseaseForm.isCommon" />
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { DiseaseCategory, Disease } from '@/types/underwriting'
import { get, post, put, del } from '@/utils/request'
import { showToast, showConfirm } from '@/utils/toast'

// 当前标签页
const activeTab = ref('disease-categories')

// 疾病大类数据
const diseaseCategories = ref<DiseaseCategory[]>([])
const diseases = ref<Disease[]>([])

// 疾病大类选项
const categoryOptions = computed(() => {
  return diseaseCategories.value.map(item => ({
    label: item.name,
    value: item.code
  }))
})

// 获取疾病大类名称
const getDiseaseCategory = (code: string) => {
  const category = diseaseCategories.value.find(item => item.code === code)
  return category?.name || code
}

// 加载疾病大类
const loadDiseaseCategories = async () => {
  try {
    const res = await get('/api/v1/underwriting/disease-categories')
    if (res.code === 200) {
      diseaseCategories.value = res.data
    } else {
      showToast('error', res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载疾病大类失败:', error)
    showToast('error', '加载失败')
  }
}

// 加载疾病列表
const loadDiseases = async () => {
  try {
    const res = await get('/api/v1/underwriting/diseases')
    if (res.code === 200) {
      diseases.value = res.data
    } else {
      showToast('error', res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载疾病列表失败:', error)
    showToast('error', '加载失败')
  }
}

// 疾病大类弹窗
const showCategoryModal = ref(false)
const categoryModalType = ref<'add' | 'edit'>('add')
const categoryForm = reactive({
  code: '',
  name: '',
  displayOrder: 1
})
const categoryFormErrors = reactive({
  code: '',
  name: '',
  displayOrder: ''
})

// 新增疾病大类
const handleAddCategory = () => {
  categoryModalType.value = 'add'
  categoryForm.code = ''
  categoryForm.name = ''
  categoryForm.displayOrder = diseaseCategories.value.length + 1
  showCategoryModal.value = true
}

// 编辑疾病大类
const handleEditCategory = (category: DiseaseCategory) => {
  categoryModalType.value = 'edit'
  categoryForm.code = category.code
  categoryForm.name = category.name
  categoryForm.displayOrder = category.displayOrder
  showCategoryModal.value = true
}

// 删除疾病大类
const handleDeleteCategory = async (category: DiseaseCategory) => {
  const confirmed = await showConfirm({
    title: '删除确认',
    content: `确定要删除疾病大类"${category.name}"吗？`,
    confirmText: '删除',
    confirmType: 'danger'
  })

  if (!confirmed) return

  try {
    const res = await del(`/api/v1/underwriting/disease-categories/${category.code}`)
    if (res.code === 200) {
      showToast('success', '删除成功')
      loadDiseaseCategories()
    } else {
      showToast('error', res.message || '删除失败')
    }
  } catch (error) {
    console.error('删除疾病大类失败:', error)
    showToast('error', '删除失败')
  }
}

// 验证疾病大类表单
const validateCategoryForm = () => {
  let valid = true
  categoryFormErrors.code = ''
  categoryFormErrors.name = ''
  categoryFormErrors.displayOrder = ''

  if (!categoryForm.code) {
    categoryFormErrors.code = '请输入编码'
    valid = false
  }

  if (!categoryForm.name) {
    categoryFormErrors.name = '请输入疾病大类名称'
    valid = false
  }

  if (!categoryForm.displayOrder) {
    categoryFormErrors.displayOrder = '请输入显示顺序'
    valid = false
  }

  return valid
}

// 保存疾病大类
const handleCategoryModalConfirm = async () => {
  if (!validateCategoryForm()) return

  try {
    const data = {
      code: categoryForm.code,
      name: categoryForm.name,
      displayOrder: categoryForm.displayOrder
    }

    let res
    if (categoryModalType.value === 'add') {
      res = await post('/api/v1/underwriting/disease-categories', data)
    } else {
      res = await put(`/api/v1/underwriting/disease-categories/${categoryForm.code}`, data)
    }

    if (res.code === 200) {
      showToast('success', categoryModalType.value === 'add' ? '创建成功' : '更新成功')
      showCategoryModal.value = false
      loadDiseaseCategories()
    } else {
      showToast('error', res.message || (categoryModalType.value === 'add' ? '创建失败' : '更新失败'))
    }
  } catch (error) {
    console.error(categoryModalType.value === 'add' ? '创建疾病大类失败:' : '更新疾病大类失败:', error)
    showToast('error', categoryModalType.value === 'add' ? '创建失败' : '更新失败')
  }
}

// 疾病弹窗
const showDiseaseModal = ref(false)
const diseaseModalType = ref<'add' | 'edit'>('add')
const diseaseForm = reactive({
  code: '',
  name: '',
  categoryCode: '',
  isCommon: false
})
const diseaseFormErrors = reactive({
  code: '',
  name: '',
  categoryCode: ''
})

// 新增疾病
const handleAddDisease = () => {
  diseaseModalType.value = 'add'
  diseaseForm.code = ''
  diseaseForm.name = ''
  diseaseForm.categoryCode = ''
  diseaseForm.isCommon = false
  showDiseaseModal.value = true
}

// 编辑疾病
const handleEditDisease = (disease: Disease) => {
  diseaseModalType.value = 'edit'
  diseaseForm.code = disease.code
  diseaseForm.name = disease.name
  diseaseForm.categoryCode = disease.categoryCode
  diseaseForm.isCommon = disease.isCommon
  showDiseaseModal.value = true
}

// 删除疾病
const handleDeleteDisease = async (disease: Disease) => {
  const confirmed = await showConfirm({
    title: '删除确认',
    content: `确定要删除疾病"${disease.name}"吗？`,
    confirmText: '删除',
    confirmType: 'danger'
  })

  if (!confirmed) return

  try {
    const res = await del(`/api/v1/underwriting/diseases/${disease.code}`)
    if (res.code === 200) {
      showToast('success', '删除成功')
      loadDiseases()
    } else {
      showToast('error', res.message || '删除失败')
    }
  } catch (error) {
    console.error('删除疾病失败:', error)
    showToast('error', '删除失败')
  }
}

// 验证疾病表单
const validateDiseaseForm = () => {
  let valid = true
  diseaseFormErrors.code = ''
  diseaseFormErrors.name = ''
  diseaseFormErrors.categoryCode = ''

  if (!diseaseForm.code) {
    diseaseFormErrors.code = '请输入编码'
    valid = false
  }

  if (!diseaseForm.name) {
    diseaseFormErrors.name = '请输入疾病名称'
    valid = false
  }

  if (!diseaseForm.categoryCode) {
    diseaseFormErrors.categoryCode = '请选择所属大类'
    valid = false
  }

  return valid
}

// 保存疾病
const handleDiseaseModalConfirm = async () => {
  if (!validateDiseaseForm()) return

  try {
    const data = {
      code: diseaseForm.code,
      name: diseaseForm.name,
      categoryCode: diseaseForm.categoryCode,
      isCommon: diseaseForm.isCommon
    }

    let res
    if (diseaseModalType.value === 'add') {
      res = await post('/api/v1/underwriting/diseases', data)
    } else {
      res = await put(`/api/v1/underwriting/diseases/${diseaseForm.code}`, data)
    }

    if (res.code === 200) {
      showToast('success', diseaseModalType.value === 'add' ? '创建成功' : '更新成功')
      showDiseaseModal.value = false
      loadDiseases()
    } else {
      showToast('error', res.message || (diseaseModalType.value === 'add' ? '创建失败' : '更新失败'))
    }
  } catch (error) {
    console.error(diseaseModalType.value === 'add' ? '创建疾病失败:' : '更新疾病失败:', error)
    showToast('error', diseaseModalType.value === 'add' ? '创建失败' : '更新失败')
  }
}

// 初始化
onMounted(() => {
  loadDiseaseCategories()
  loadDiseases()
})
</script>

<style scoped>
.config-page {
  padding: var(--spacing-lg);
}

.page-header {
  margin-bottom: var(--spacing-lg);
}

.page-header h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
}

.config-tabs {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.section {
  margin-bottom: var(--spacing-xl);
}

.section-header {
  margin-bottom: var(--spacing-md);
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
  background: var(--color-bg-spotlight);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
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