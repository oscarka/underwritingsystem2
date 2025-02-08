<template>
  <button 
    class="base-button" 
    :class="[
      type ? `is-${type}` : '',
      { 
        'is-loading': loading,
        'is-disabled': disabled
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="loading-icon">
      <svg viewBox="0 0 1024 1024" class="loading">
        <path d="M512 64c-247.4 0-448 200.6-448 448s200.6 448 448 448 448-200.6 448-448-200.6-448-448zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
      </svg>
    </span>
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
interface Props {
  type?: 'primary' | 'danger'
  loading?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: undefined,
  loading: false,
  disabled: false
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--spacing-lg);
  height: 36px;
  min-width: 88px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
  user-select: none;
}

.base-button:hover:not(.is-disabled):not(.is-loading) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 5%, var(--color-bg-elevated));
}

.base-button.is-primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
}

.base-button.is-primary:hover:not(.is-disabled):not(.is-loading) {
  background: color-mix(in srgb, var(--color-primary) 80%, white);
  border-color: color-mix(in srgb, var(--color-primary) 80%, white);
  box-shadow: 0 2px 4px color-mix(in srgb, var(--color-primary) 25%, transparent);
}

.base-button.is-danger {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: #fff;
}

.base-button.is-danger:hover:not(.is-disabled):not(.is-loading) {
  background: color-mix(in srgb, var(--color-danger) 80%, white);
  border-color: color-mix(in srgb, var(--color-danger) 80%, white);
  box-shadow: 0 2px 4px color-mix(in srgb, var(--color-danger) 25%, transparent);
}

.base-button.is-disabled {
  background: var(--color-bg-spotlight);
  border-color: var(--color-border-light);
  color: var(--color-text-disabled);
  cursor: not-allowed;
  opacity: 0.7;
}

.base-button.is-loading {
  cursor: wait;
  position: relative;
  pointer-events: none;
}

.loading-icon {
  margin-right: var(--spacing-xs);
  width: 18px;
  height: 18px;
  opacity: 0.8;
}

.loading {
  animation: rotate 1s linear infinite;
  fill: currentColor;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 