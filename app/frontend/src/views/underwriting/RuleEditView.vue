# 核保规则编辑页面
<template>
  <div class="rule-edit-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <BaseButton @click="router.back()">返回</BaseButton>
        <h1>{{ isEdit ? '编辑规则' : '新增规则' }}</h1>
      </div>
      <div class="header-actions">
        <BaseButton @click="handleCancel">取消</BaseButton>
        <BaseButton type="primary" @click="handleSave">保存</BaseButton>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
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
          :disabled="isEdit"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Rule, RuleForm } from '@/types/underwriting'
import { get, post, put } from '@/utils/request'
import { showToast } from '@/utils/toast'

const router = useRouter()
const route = useRoute()
const ruleId = route.params.id

// 是否是编辑模式
const isEdit = computed(() => !!ruleId)

// 表单数据
const formData = reactive<RuleForm>({
  name: '',
  version: '',
  remark: ''
})

// 表单错误信息
const formErrors = reactive({
  name: '',
  version: ''
})

// 加载规则详情
const loadRuleDetail = async () => {
  if (!isEdit.value) return

  try {
    const res = await get(`/api/v1/underwriting/rules/${ruleId}`)
    if (res.code === 200) {
      const rule = res.data
      formData.name = rule.name
      formData.version = rule.version
      formData.remark = rule.remark
    } else {
      showToast('error', res.message || '加载失败')
    }
  } catch (error) {
    console.error('加载规则详情失败:', error)
    showToast('error', '加载失败')
  }
}

// 表单验证
const validateForm = () => {
  let valid = true
  formErrors.name = ''
  formErrors.version = ''

  if (!formData.name) {
    formErrors.name = '请输入规则名称'
    valid = false
  }

  if (!formData.version) {
    formErrors.version = '请输入版本号'
    valid = false
  }

  return valid
}

// 保存
const handleSave = async () => {
  if (!validateForm()) return

  try {
    const data = {
      name: formData.name,
      version: formData.version,
      remark: formData.remark
    }

    let res
    if (isEdit.value) {
      res = await put(`/api/v1/underwriting/rules/${ruleId}`, data)
    } else {
      res = await post('/api/v1/underwriting/rules', data)
    }

    if (res.code === 200) {
      showToast('success', isEdit.value ? '更新成功' : '创建成功')
      router.back()
    } else {
      showToast('error', res.message || (isEdit.value ? '更新失败' : '创建失败'))
    }
  } catch (error) {
    console.error(isEdit.value ? '更新规则失败:' : '创建规则失败:', error)
    showToast('error', isEdit.value ? '更新失败' : '创建失败')
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

// 初始化
onMounted(() => {
  loadRuleDetail()
})
</script>

<style scoped>
.rule-edit-page {
  padding: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-left h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.form-container {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  max-width: 600px;
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