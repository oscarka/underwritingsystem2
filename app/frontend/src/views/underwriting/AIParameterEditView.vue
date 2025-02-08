# 智核参数编辑页面
<template>
  <div class="ai-parameter-edit-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <BaseButton @click="router.back()">返回</BaseButton>
        <h1>{{ isEdit ? '编辑智核参数' : '新增智核参数' }}</h1>
      </div>
      <div class="header-actions">
        <BaseButton @click="handleCancel">取消</BaseButton>
        <BaseButton type="primary" @click="handleSave">保存</BaseButton>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
      <BaseForm ref="form" :model="formData" label-width="120px">
        <BaseFormItem label="参数名称" required>
          <BaseInput
            v-model="formData.name"
            placeholder="请输入参数名称"
            :maxlength="100"
          />
        </BaseFormItem>

        <BaseFormItem label="参数类型" required>
          <BaseSelect
            v-model="formData.parameter_type_id"
            placeholder="请选择参数类型"
          >
            <option value="" disabled>请选择参数类型</option>
            <option
              v-for="type in parameterTypes"
              :key="type.id"
              :value="type.id"
            >
              {{ type.name }}
            </option>
          </BaseSelect>
        </BaseFormItem>

        <BaseFormItem label="核保规则" required>
          <BaseSelect
            v-model="formData.rule_id"
            placeholder="请选择核保规则"
          >
            <option value="" disabled>请选择核保规则</option>
            <option
              v-for="rule in rules"
              :key="rule.id"
              :value="rule.id"
            >
              {{ rule.name }}
            </option>
          </BaseSelect>
        </BaseFormItem>

        <BaseFormItem label="参数值" required>
          <BaseInput
            v-model="formData.value"
            type="textarea"
            placeholder="请输入参数值"
            :maxlength="500"
            :rows="4"
          />
        </BaseFormItem>

        <BaseFormItem label="参数描述">
          <BaseInput
            v-model="formData.description"
            type="textarea"
            placeholder="请输入参数描述"
            :maxlength="500"
            :rows="4"
          />
        </BaseFormItem>
      </BaseForm>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from '@/composables/useMessage'
import {
  getParameter,
  getParameterTypes,
  getRules,
  createParameter,
  updateParameter
} from '@/api/underwriting'
import type { Parameter, ParameterType } from '@/types/underwriting'

const router = useRouter()
const route = useRoute()
const message = useMessage()

// 是否是编辑模式
const isEdit = computed(() => route.params.id !== undefined)

// 表单数据
const formData = ref({
  name: '',
  parameter_type_id: undefined as number | undefined,
  rule_id: undefined as number | undefined,
  value: '',
  description: undefined as string | undefined
})

// 下拉选项数据
const parameterTypes = ref<ParameterType[]>([])
const rules = ref<{ id: number; name: string }[]>([])

// 获取参数类型列表
const loadParameterTypes = async () => {
  try {
    const res = await getParameterTypes()
    parameterTypes.value = res.data
  } catch (error) {
    console.error('获取参数类型失败:', error)
    message.error('获取参数类型失败')
  }
}

// 获取规则列表
const loadRules = async () => {
  try {
    const res = await getRules()
    rules.value = res.data
  } catch (error) {
    console.error('获取规则列表失败:', error)
    message.error('获取规则列表失败')
  }
}

// 加载参数详情
const loadParameterDetail = async () => {
  if (!isEdit.value) return
  try {
    const res = await getParameter(Number(route.params.id))
    const paramData = res.data as Parameter
    formData.value = {
      name: paramData.name,
      parameter_type_id: paramData.parameter_type_id,
      rule_id: paramData.rule_id,
      value: paramData.value,
      description: paramData.description
    }
  } catch (error) {
    console.error('获取参数详情失败:', error)
    message.error('获取参数详情失败')
  }
}

// 表单验证
const validateForm = () => {
  const { name, parameter_type_id, rule_id, value } = formData.value
  const errors = []

  if (!name?.trim()) {
    errors.push('参数名称不能为空')
  } else if (name.length > 100) {
    errors.push('参数名称不能超过100个字符')
  }

  if (!parameter_type_id) {
    errors.push('参数类型不能为空')
  }

  if (!rule_id) {
    errors.push('核保规则不能为空')
  }

  if (!value?.trim()) {
    errors.push('参数值不能为空')
  } else if (value.length > 500) {
    errors.push('参数值不能超过500个字符')
  }

  const description = formData.value.description
  if (description && description.length > 500) {
    errors.push('参数描述不能超过500个字符')
  }

  if (errors.length > 0) {
    errors.forEach(error => message.error(error))
    return false
  }

  // 确保类型正确
  formData.value.parameter_type_id = Number(parameter_type_id)
  formData.value.rule_id = Number(rule_id)
  
  return true
}

// 保存
const handleSave = async () => {
  if (!validateForm()) return

  try {
    console.log('准备保存数据:', formData.value)
    
    // 处理数据类型
    const submitData = {
      ...formData.value,
      parameter_type_id: Number(formData.value.parameter_type_id),
      rule_id: Number(formData.value.rule_id),
      status: 'enabled'  // 设置默认状态
    }
    
    console.log('处理后的提交数据:', submitData)
    
    if (isEdit.value) {
      const res = await updateParameter(Number(route.params.id), submitData)
      if (res.code === 200) {
        message.success('更新成功')
        router.push({
          path: '/underwriting/ai-parameter',
          query: { refresh: Date.now().toString() }
        })
      } else {
        throw new Error(res.message || '更新失败')
      }
    } else {
      const res = await createParameter(submitData)
      if (res.code === 200) {
        message.success('创建成功')
        router.push({
          path: '/underwriting/ai-parameter',
          query: { refresh: Date.now().toString() }
        })
      } else {
        throw new Error(res.message || '创建失败')
      }
    }
  } catch (error: any) {
    console.error('保存失败:', error)
    message.error(error.response?.data?.message || error.message || '保存失败')
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

onMounted(() => {
  loadParameterTypes()
  loadRules()
  loadParameterDetail()
})
</script>

<style lang="scss" scoped>
.ai-parameter-edit-page {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      h1 {
        margin: 0;
        font-size: 24px;
      }
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .form-container {
    padding: 24px;
    background: #fff;
    border-radius: 4px;
  }
}
</style> 