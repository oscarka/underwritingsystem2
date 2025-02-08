# 问题列表组件
<template>
  <div class="question-list">
    <BaseTable :columns="columns" :data="data" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseTable from '@/components/base/BaseTable.vue'
import type { Question } from '@/types/underwriting'

defineProps<{
  data: Question[]
}>()

const columns = computed(() => [
  { key: 'code', title: '编码' },
  { key: 'content', title: '问题内容' },
  { key: 'questionType', title: '问题类型' },
  { key: 'updatedAt', title: '修改时间' }
])
</script>

<style scoped>
.question-list {
  width: 100%;
}
</style> 