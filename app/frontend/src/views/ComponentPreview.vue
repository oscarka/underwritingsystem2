<template>
  <div class="preview">
    <section class="section">
      <h2>按钮</h2>
      <div class="demo-row">
        <BaseButton>默认按钮</BaseButton>
        <BaseButton type="primary">主要按钮</BaseButton>
        <BaseButton type="danger">危险按钮</BaseButton>
        <BaseButton loading>加载中</BaseButton>
        <BaseButton disabled>禁用按钮</BaseButton>
      </div>
    </section>

    <section class="section">
      <h2>输入框</h2>
      <div class="demo-col">
        <BaseInput v-model="input1" placeholder="基础输入框" />
        <BaseInput v-model="input2" label="带标签" placeholder="请输入" />
        <BaseInput v-model="input3" error="错误提示信息" placeholder="错误状态" />
        <BaseInput v-model="input4" disabled placeholder="禁用状态" />
      </div>
    </section>

    <section class="section">
      <h2>选择框</h2>
      <div class="demo-col">
        <BaseSelect
          v-model="select1"
          :options="selectOptions"
          placeholder="基础选择框"
        />
        <BaseSelect
          v-model="select2"
          :options="selectOptions"
          label="带标签"
        />
        <BaseSelect
          v-model="select3"
          :options="selectOptions"
          error="错误提示信息"
        />
        <BaseSelect
          v-model="select4"
          :options="selectOptions"
          disabled
          placeholder="禁用状态"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// 输入框绑定值
const input1 = ref('')
const input2 = ref('')
const input3 = ref('')
const input4 = ref('')

// 选择框绑定值
const select1 = ref<string | number>('')
const select2 = ref<string | number>('')
const select3 = ref<string | number>('')
const select4 = ref<string | number>('')

// 选择框选项
const selectOptions = [
  { value: '1', label: '选项一' },
  { value: '2', label: '选项二' },
  { value: '3', label: '选项三' }
]
</script>

<style scoped>
.preview {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.section {
  margin-bottom: var(--spacing-xl);
}

.section h2 {
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
}

.demo-row {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.demo-col {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 320px;
}
</style> 