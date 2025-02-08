<template>
  <div class="base-input">
    <label v-if="label" class="label">{{ label }}</label>
    <div class="input-wrapper" :class="{ 'has-error': error }">
      <input
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :type="type"
        class="input"
        @input="handleInput"
        @change="handleChange"
      />
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string | number
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  type?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: '',
  disabled: false,
  error: '',
  type: 'text'
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('change', target.value)
}
</script>

<style scoped>
.base-input {
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

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input {
  width: 100%;
  height: 36px;
  padding: 0 var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
}

.input::placeholder {
  color: var(--color-text-disabled);
}

.input:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--color-primary) 80%, transparent);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-primary) 20%, transparent);
}

.input:disabled {
  background: var(--color-bg-spotlight);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.7;
}

.input-wrapper.has-error .input {
  border-color: var(--color-danger);
  background: color-mix(in srgb, var(--color-danger) 5%, var(--color-bg-elevated));
}

.input-wrapper.has-error .input:focus {
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-danger) 20%, transparent);
}

.error-message {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  padding-left: 2px;
  min-height: 20px;
}
</style> 