<template>
  <RouterView />
</template>

<script setup lang="ts">
// 使用 setup 语法糖
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