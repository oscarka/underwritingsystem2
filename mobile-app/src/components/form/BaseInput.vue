<template>
  <div class="base-input">
    <label v-if="label" :for="id" class="base-input__label">{{ label }}</label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="base-input__field"
      @input="handleInput"
      @blur="handleBlur"
    />
    <span v-if="error" class="base-input__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  modelValue: string | number;
  label?: string;
  type?: 'text' | 'number' | 'tel' | 'email';
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  id?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void;
  (e: 'blur', value: string | number): void;
}>();

const id = computed(() => props.id || `input-${Math.random().toString(36).slice(2)}`);

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const value = props.type === 'number' ? Number(target.value) : target.value;
  emit('update:modelValue', value);
};

const handleBlur = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('blur', target.value);
};
</script>

<style scoped>
.base-input {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.base-input__label {
  font-size: 14px;
  color: #333;
}

.base-input__field {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s;
}

.base-input__field:focus {
  border-color: #007aff;
}

.base-input__field:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.base-input__error {
  font-size: 12px;
  color: #ff3b30;
}
</style> 