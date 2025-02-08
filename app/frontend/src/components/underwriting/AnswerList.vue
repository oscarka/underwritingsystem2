# 答案列表组件
<template>
  <div class="answer-list">
    <BaseTable :columns="columns" :data="data" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseTable from '@/components/base/BaseTable.vue'
import type { Answer } from '@/types/underwriting'

defineProps<{
  data: Answer[]
}>()

const columns = computed(() => [
  { key: 'code', title: '编码' },
  { key: 'content', title: '答案内容' },
  { key: 'questionCode', title: '所属问题编码' },
  { 
    key: 'medicalDecision', 
    title: '医疗险结论',
    render: (value: string) => value || '-'
  },
  { 
    key: 'finalDecision', 
    title: '重疾险结论',
    render: (value: string) => value || '-'
  },
  { 
    key: 'remark', 
    title: '备注',
    render: (value: string) => value || '-'
  },
  { key: 'updatedAt', title: '更新时间' }
])
</script>

<style scoped>
.answer-list {
  width: 100%;
}
</style> 