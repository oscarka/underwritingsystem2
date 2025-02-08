<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        :class="['loading', { 'loading-fullscreen': fullscreen }]"
      >
        <div class="loading-spinner">
          <svg viewBox="0 0 50 50" class="loading-circular">
            <circle
              class="loading-path"
              cx="25"
              cy="25"
              r="20"
              fill="none"
              stroke="currentColor"
              stroke-width="5"
            />
          </svg>
        </div>
        <div v-if="text" class="loading-text">{{ text }}</div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  fullscreen?: boolean
  text?: string
}

withDefaults(defineProps<Props>(), {
  fullscreen: false,
  text: ''
})

const visible = ref(false)

// 显示加载
function show() {
  visible.value = true
}

// 隐藏加载
function hide() {
  visible.value = false
}

defineExpose({
  show,
  hide
})
</script>

<style scoped>
.loading {
  position: absolute;
  z-index: 9999;
  background-color: var(--color-bg-mask);
  margin: 0;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  transition: opacity 0.3s;
}

.loading-fullscreen {
  position: fixed;
}

.loading-spinner {
  top: 50%;
  margin-top: -25px;
  width: 100%;
  text-align: center;
  position: absolute;
}

.loading-circular {
  height: 50px;
  width: 50px;
  animation: loading-rotate 2s linear infinite;
}

.loading-path {
  animation: loading-dash 1.5s ease-in-out infinite;
  stroke-dasharray: 90, 150;
  stroke-dashoffset: 0;
  stroke-width: 2;
  stroke: var(--color-primary);
  stroke-linecap: round;
}

.loading-text {
  color: var(--color-primary);
  margin: 3px 0;
  font-size: var(--font-size-sm);
  position: absolute;
  width: 100%;
  text-align: center;
  top: 50%;
  margin-top: 35px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes loading-rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes loading-dash {
  0% {
    stroke-dasharray: 1, 200;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -40px;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -120px;
  }
}
</style> 