<template>
  <div v-show="isActive" class="tab-pane">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { inject, onMounted, computed, type Ref } from 'vue'

const props = defineProps<{
  tab: string
  key: string
}>()

// 注入父组件提供的注册方法和activeKey
const registerTab = inject('registerTab') as (key: string, tab: string) => void
const activeKey = inject('activeKey') as Ref<string>

// 计算当前标签页是否激活
const isActive = computed(() => activeKey.value === props.key)

// 组件挂载时注册标签页
onMounted(() => {
  registerTab(props.key, props.tab)
})
</script>

<style scoped>
.tab-pane {
  height: 100%;
  overflow: auto;
}
</style> 