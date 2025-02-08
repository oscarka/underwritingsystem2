# 疾病列表组件
<template>
  <div class="disease-list">
    <BaseTable :columns="columns" :data="data" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseTable from '@/components/base/BaseTable.vue'
import type { Disease } from '@/types/underwriting'

const props = defineProps<{
  data: Disease[]
  getCategoryName: (code: string) => string
}>()

const columns = computed(() => [
  { key: 'code', title: '编码' },
  { key: 'name', title: '疾病名称' },
  { 
    key: 'categoryCode', 
    title: '疾病大类',
    render: (value: string) => props.getCategoryName(value)
  },
  { 
    key: 'isCommon', 
    title: '是否常见疾病',
    render: (value: boolean) => value ? '是' : '否'
  },
  { key: 'updatedAt', title: '修改时间' }
])
</script>

<style scoped>
.disease-list {
  width: 100%;
}
</style> 