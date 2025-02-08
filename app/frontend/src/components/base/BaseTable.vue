# 基础表格组件
<template>
  <div class="base-table">
    <table class="data-table">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key">{{ column.title }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in data" :key="index">
          <td v-for="column in columns" :key="column.key">
            <template v-if="column.render">
              {{ column.render(item[column.key], item) }}
            </template>
            <template v-else>
              {{ item[column.key] }}
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string
  title: string
  render?: (value: any, record: any) => string
}

defineProps<{
  columns: Column[]
  data: Record<string, any>[]
}>()
</script>

<style scoped>
.base-table {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  text-align: left;
}

.data-table th {
  background: var(--color-bg-container);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.data-table tbody tr:hover {
  background: var(--color-bg-hover);
}
</style> 