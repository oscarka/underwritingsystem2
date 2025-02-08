<template>
  <div class="pagination">
    <button 
      class="page-btn"
      :disabled="current <= 1"
      @click="handlePrev"
    >
      上一页
    </button>
    <span class="page-info">
      {{ current }}/{{ totalPages }}
    </span>
    <button 
      class="page-btn"
      :disabled="current >= totalPages"
      @click="handleNext"
    >
      下一页
    </button>
    <span class="total-info">
      共 {{ total }} 条
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  current: number
  pageSize: number
  total: number
}>(), {
  current: 1,
  pageSize: 10,
  total: 0
})

const emit = defineEmits<{
  'update:current': [value: number]
  'update:pageSize': [value: number]
  'change': []
}>()

const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

function handlePrev() {
  if (props.current > 1) {
    emit('update:current', props.current - 1)
    emit('change')
  }
}

function handleNext() {
  if (props.current < totalPages.value) {
    emit('update:current', props.current + 1)
    emit('change')
  }
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.page-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  background: var(--color-bg-container);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info, .total-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
</style> 