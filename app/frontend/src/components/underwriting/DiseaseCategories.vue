# 疾病大类列表组件
<template>
  <div class="disease-categories">
    <BaseTable :columns="columns" :data="data" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseTable from '@/components/base/BaseTable.vue'
import type { DiseaseCategory } from '@/types/underwriting'

defineProps<{
  data: DiseaseCategory[]
}>()

const columns = computed(() => [
  { key: 'code', title: '编码' },
  { key: 'name', title: '疾病大类名称' },
  { key: 'displayOrder', title: '显示顺序' },
  { key: 'updatedAt', title: '修改时间' }
])
</script>

<style scoped>
.disease-categories {
  width: 100%;
}
</style> 