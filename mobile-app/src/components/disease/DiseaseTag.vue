<template>
  <div 
    class="disease-tag" 
    :class="{ 'disease-tag--selected': selected }"
    @click="$emit('click')"
  >
    <span class="disease-tag__name">{{ disease.name }}</span>
    <button 
      v-if="closeable" 
      class="disease-tag__close"
      @click.stop="$emit('close')"
    >
      &times;
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Disease } from '@/api/types/underwriting';

defineProps<{
  disease: Disease;
  selected?: boolean;
  closeable?: boolean;
}>();

defineEmits<{
  (e: 'click'): void;
  (e: 'close'): void;
}>();
</script>

<style scoped>
.disease-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background-color: #f5f5f5;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.disease-tag--selected {
  background-color: #007aff;
  color: white;
}

.disease-tag__name {
  white-space: nowrap;
}

.disease-tag__close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  padding: 0;
  border: none;
  background: none;
  color: currentColor;
  font-size: 16px;
  cursor: pointer;
  opacity: 0.7;
}

.disease-tag__close:hover {
  opacity: 1;
}
</style> 