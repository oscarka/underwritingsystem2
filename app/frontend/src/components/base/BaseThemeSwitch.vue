<template>
  <button 
    class="theme-switch"
    :class="{ 'is-dark': theme === 'dark' }"
    @click="toggleTheme"
  >
    <span class="icon">{{ theme === 'dark' ? '🌙' : '☀️' }}</span>
  </button>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-switch {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--color-bg-elevated);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.theme-switch:hover {
  background: var(--color-bg-spotlight);
}

.theme-switch .icon {
  font-size: 20px;
}
</style> 