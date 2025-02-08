<template>
  <div class="base-select">
    <label v-if="label" class="label">{{ label }}</label>
    <div class="select-wrapper" :class="{ 'has-error': error }">
      <select
        :value="modelValue"
        :disabled="disabled"
        class="select"
        @change="handleChange"
      >
        <option value="" disabled>{{ placeholder || '请选择' }}</option>
        <option
          v-for="option in normalizedOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
      <span class="arrow">▼</span>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface SelectOption {
  value: string | number
  label: string
}

interface Props {
  modelValue?: string | number
  options?: SelectOption[]
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  options: () => [],
  label: '',
  placeholder: '请选择',
  disabled: false,
  error: ''
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const normalizedOptions = computed(() => {
  return props.options.map(option => {
    if (typeof option === 'string') {
      return { value: option, label: option }
    }
    return option
  })
})

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
  emit('change', target.value)
}
</script>

<style scoped>
.base-select {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 500;
  padding-left: 2px;
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.select {
  width: 100%;
  height: 36px;
  padding: 0 var(--spacing-xl) 0 var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  appearance: none;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.select:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--color-primary) 80%, transparent);
}

.select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 20%, transparent);
}

.select:disabled {
  background: var(--color-bg-spotlight);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.7;
}

.select option {
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
  padding: var(--spacing-sm) var(--spacing-md);
  min-height: 32px;
}

.select option:hover,
.select option:focus {
  background: var(--color-bg-spotlight);
  color: var(--color-primary);
}

.select option:checked {
  background: color-mix(in srgb, var(--color-primary) 10%, var(--color-bg-elevated));
  color: var(--color-primary);
}

.select option[disabled] {
  color: var(--color-text-disabled);
}

.arrow {
  position: absolute;
  right: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
  pointer-events: none;
  transition: transform var(--transition-normal);
  opacity: 0.8;
}

.select:focus + .arrow {
  transform: translateY(-50%) rotate(180deg);
  color: var(--color-primary);
}

.select-wrapper.has-error .select {
  border-color: var(--color-danger);
  background: color-mix(in srgb, var(--color-danger) 5%, var(--color-bg-elevated));
}

.select-wrapper.has-error .select:focus {
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-danger) 20%, transparent);
}

.error-message {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  padding-left: 2px;
  min-height: 20px;
}
</style> 