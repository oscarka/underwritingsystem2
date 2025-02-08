# 问题配置页面
<template>
  <div class="question-config-page">
    <BaseTabs v-model="activeTab" :tabs="tabs">
      <template v-if="activeTab === 'categories'">
        <div class="content-section">
          <DiseaseCategories :data="diseaseCategories" />
        </div>
      </template>

      <template v-if="activeTab === 'diseases'">
        <div class="content-section">
          <DiseaseList 
            :data="diseases" 
            :get-category-name="getDiseaseCategory" 
          />
        </div>
      </template>

      <template v-if="activeTab === 'questions'">
        <div class="content-section">
          <QuestionList :data="questions" />
        </div>
      </template>

      <template v-if="activeTab === 'answers'">
        <div class="content-section">
          <AnswerList :data="answers" />
        </div>
      </template>
    </BaseTabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseTabs from '@/components/base/BaseTabs.vue'
import DiseaseCategories from '@/components/underwriting/DiseaseCategories.vue'
import DiseaseList from '@/components/underwriting/DiseaseList.vue'
import QuestionList from '@/components/underwriting/QuestionList.vue'
import AnswerList from '@/components/underwriting/AnswerList.vue'
import type { DiseaseCategory, Disease, Question, Answer } from '@/types/underwriting'

// 标签页配置
const tabs = [
  { key: 'categories', label: '疾病大类' },
  { key: 'diseases', label: '疾病' },
  { key: 'questions', label: '问题' },
  { key: 'answers', label: '答案' }
]

const activeTab = ref('categories')

// 疾病大类数据
const diseaseCategories = ref<DiseaseCategory[]>([
  {
    code: '1CDFGHJ',
    name: '胃肠肝胆疾病',
    displayOrder: 1,
    updatedAt: '2024-01-20 17:35'
  },
  {
    code: '2CDFGHJ',
    name: '心血管与内分泌疾病',
    displayOrder: 2,
    updatedAt: '2024-01-20 17:35'
  },
  {
    code: '3CDFGHJ',
    name: '眼、耳、口、鼻',
    displayOrder: 3,
    updatedAt: '2024-01-20 17:35'
  }
])

// 疾病列表数据
const diseases = ref<Disease[]>([
  {
    code: 'D001',
    name: '胃炎',
    categoryCode: '1CDFGHJ',
    isCommon: true,
    updatedAt: '2024-01-20 17:35'
  },
  {
    code: 'D002',
    name: '高血压',
    categoryCode: '2CDFGHJ',
    isCommon: true,
    updatedAt: '2024-01-20 17:35'
  }
])

// 问题列表数据
const questions = ref<Question[]>([
  {
    code: 'Q001',
    content: '最近一年是否因胃炎住院？',
    questionType: '单选题',
    updatedAt: '2024-01-20 17:35'
  },
  {
    code: 'Q002',
    content: '是否为慢性胃病？',
    questionType: '单选题',
    updatedAt: '2024-01-20 17:35'
  }
])

// 答案列表数据
const answers = ref<Answer[]>([
  {
    code: 'ASSGG',
    content: '未手术或等级，BI-RADS分级2级',
    questionCode: 'ASSGG1',
    medicalDecision: '20（加费）',
    finalDecision: '通过',
    remark: '',
    updatedAt: '2024-01-20 17:35'
  },
  {
    code: 'ASSGG1',
    content: '肝功能不高于正常上限2倍、近一年...',
    questionCode: 'ASSGG2',
    medicalDecision: '通过',
    finalDecision: '',
    remark: '',
    updatedAt: '2024-01-20 17:35'
  },
  {
    code: 'ASSGG2',
    content: '病理结果非良性',
    questionCode: 'ASSGG3',
    medicalDecision: '拒保',
    finalDecision: '',
    remark: '',
    updatedAt: '2024-01-20 17:35'
  }
])

// 获取疾病大类名称
const getDiseaseCategory = (categoryCode: string) => {
  const category = diseaseCategories.value.find(item => item.code === categoryCode)
  return category ? category.name : '-'
}
</script>

<style scoped>
.question-config-page {
  padding: var(--spacing-lg);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-section {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  flex: 1;
}
</style> 