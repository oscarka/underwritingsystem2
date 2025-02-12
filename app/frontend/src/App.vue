<template>
  <RouterView />
</template>

<script setup lang="ts">
import { onMounted, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onBeforeMount(() => {
  console.log('[App-Debug] 组件即将挂载:', {
    currentRoute: route.fullPath,
    timestamp: new Date().toISOString()
  })
})

onMounted(() => {
  console.log('[App-Debug] 组件已挂载:', {
    currentRoute: route.fullPath,
    matched: route.matched.length,
    matchedRoutes: route.matched.map(r => r.path),
    timestamp: new Date().toISOString()
  })
})
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--color-bg-base);
  color: var(--color-text-primary);
  transition: background var(--transition-normal), color var(--transition-normal);
}

* {
  box-sizing: border-box;
}
</style> 