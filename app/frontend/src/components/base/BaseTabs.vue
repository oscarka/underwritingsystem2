# 基础标签页组件
<template>
  <div class="base-tabs">
    <div class="tab-nav">
      <div
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-item', { active: modelValue === tab.key }]"
        @click="$emit('update:modelValue', tab.key)"
      >
        {{ tab.label }}
      </div>
    </div>
    <div class="tab-content">
      <template v-for="tab in tabs" :key="tab.key">
        <div v-show="modelValue === tab.key" class="tab-pane">
          <slot :name="tab.key">
            <slot></slot>
          </slot>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  tabs: Array<{
    key: string
    label: string
  }>
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>

<style scoped>
.base-tabs {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  height: 100%;
}

.tab-nav {
  display: flex;
  gap: 2px;
  background: var(--color-bg-container);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-lg);
}

.tab-item {
  padding: var(--spacing-sm) var(--spacing-lg);
  cursor: pointer;
  background: var(--color-bg-spotlight);
  color: var(--color-text-secondary);
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-normal);
}

.tab-item:hover {
  background: var(--color-bg-hover);
}

.tab-item.active {
  background: var(--color-primary);
  color: white;
}

.tab-content {
  flex: 1;
  min-height: 0;
  position: relative;
}

.tab-pane {
  height: 100%;
}
</style> 