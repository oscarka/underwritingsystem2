# 核保规则详情页面
<template>
  <div class="rule-detail-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>{{ rule.name }}</h1>
        <span class="version-tag">{{ rule.version }}</span>
        <span :class="['status-badge', rule.status]">{{ rule.status }}</span>
      </div>
      <div class="header-actions">
        <BaseButton @click="handleEdit">编辑规则</BaseButton>
        <BaseButton @click="$router.back()">返回</BaseButton>
      </div>
    </div>

    <!-- 基本信息卡片 -->
    <div class="info-card">
      <div class="info-grid">
        <div class="info-item">
          <label>创建时间</label>
          <span>{{ rule.created_at }}</span>
        </div>
        <div class="info-item">
          <label>更新时间</label>
          <span>{{ rule.updated_at }}</span>
        </div>
        <div class="info-item">
          <label>备注</label>
          <span>{{ rule.remark || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- 规则内容标签页 -->
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
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseTabs from '@/components/base/BaseTabs.vue'
import DiseaseCategories from '@/components/underwriting/DiseaseCategories.vue'
import DiseaseList from '@/components/underwriting/DiseaseList.vue'
import QuestionList from '@/components/underwriting/QuestionList.vue'
import AnswerList from '@/components/underwriting/AnswerList.vue'
import type { Rule, DiseaseCategory, Disease, Question, Answer } from '@/types/underwriting'
import { RuleStatus } from '@/types/underwriting'
import ruleApi from '@/api/underwriting'
import { showError } from '@/utils/feedback'

const router = useRouter()
const route = useRoute()
const activeTab = ref('categories')

// 标签页配置
const tabs = [
  { key: 'categories', label: '疾病大类' },
  { key: 'diseases', label: '疾病' },
  { key: 'questions', label: '问题' },
  { key: 'answers', label: '答案' }
]

// 数据状态
const rule = ref<Rule>({
  id: '',
  name: '',
  version: '',
  status: RuleStatus.DRAFT,
  created_at: '',
  updated_at: '',
  remark: '',
  description: ''
})

const diseaseCategories = ref<DiseaseCategory[]>([])
const diseases = ref<Disease[]>([])
const questions = ref<Question[]>([])
const answers = ref<Answer[]>([])

// 获取规则详情
const fetchRuleDetail = async () => {
  try {
    const ruleId = route.params.id as string
    console.log('[RuleDetailView] 开始获取规则详情:', ruleId)
    
    const res = await ruleApi.getRuleDetail(ruleId)
    if (res.code === 200 && res.data) {
      const { created_at, updated_at, ...rest } = res.data
      rule.value = {
        ...rest,
        status: rest.status || RuleStatus.DRAFT,
        created_at: created_at || '',
        updated_at: updated_at || ''
      }
      console.log('[RuleDetailView] 获取规则详情成功:', rule.value)
    }
  } catch (error) {
    console.error('[RuleDetailView] 获取规则详情失败:', error)
    showError('获取规则详情失败')
  }
}

// 获取疾病类别
const fetchDiseaseCategories = async () => {
  try {
    const ruleId = route.params.id as string
    const res = await ruleApi.getDiseaseCategories(ruleId)
    if (res.code === 200 && res.data) {
      diseaseCategories.value = res.data
    }
  } catch (error) {
    console.error('[RuleDetailView] 获取疾病类别失败:', error)
    showError('获取疾病类别失败')
  }
}

// 获取疾病列表
const fetchDiseases = async () => {
  try {
    const ruleId = route.params.id as string
    const res = await ruleApi.getDiseases(ruleId)
    if (res.code === 200 && res.data) {
      diseases.value = res.data
    }
  } catch (error) {
    console.error('[RuleDetailView] 获取疾病列表失败:', error)
    showError('获取疾病列表失败')
  }
}

// 获取问题列表
const fetchQuestions = async () => {
  try {
    const ruleId = route.params.id as string
    const res = await ruleApi.getRuleQuestions(ruleId)
    if (res.code === 200 && res.data) {
      questions.value = res.data
    }
  } catch (error) {
    console.error('[RuleDetailView] 获取问题列表失败:', error)
    showError('获取问题列表失败')
  }
}

// 获取答案列表
const fetchAnswers = async () => {
  try {
    const ruleId = route.params.id as string
    const res = await ruleApi.getRuleAnswers(ruleId)
    if (res.code === 200 && res.data) {
      answers.value = res.data
    }
  } catch (error) {
    console.error('[RuleDetailView] 获取答案列表失败:', error)
    showError('获取答案列表失败')
  }
}

// 获取疾病类别名称
const getDiseaseCategory = (categoryId: string): string => {
  const category = diseaseCategories.value.find(c => c.id === categoryId)
  return category ? category.name : '-'
}

// 编辑规则
const handleEdit = () => {
  const ruleId = route.params.id as string
  router.push(`/underwriting/rules/${ruleId}/edit`)
}

// 监听标签页切换
watch(activeTab, async (newTab) => {
  switch (newTab) {
    case 'categories':
      if (diseaseCategories.value.length === 0) {
        await fetchDiseaseCategories()
      }
      break
    case 'diseases':
      if (diseases.value.length === 0) {
        await fetchDiseases()
      }
      break
    case 'questions':
      if (questions.value.length === 0) {
        await fetchQuestions()
      }
      break
    case 'answers':
      if (answers.value.length === 0) {
        await fetchAnswers()
      }
      break
  }
})

// 初始化
onMounted(async () => {
  await fetchRuleDetail()
  await fetchDiseaseCategories()
})
</script>

<style scoped>
.rule-detail-page {
  padding: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-left h1 {
  margin: 0;
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
}

.version-tag {
  padding: 2px 8px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--border-radius-sm);
  font-size: 14px;
}

.status-badge {
  padding: 2px 8px;
  border-radius: var(--border-radius-sm);
  font-size: 14px;
}

.status-badge.enabled {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-badge.disabled {
  background: var(--color-error-light);
  color: var(--color-error);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.info-card {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.info-item label {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.content-section {
  background: var(--color-bg-container);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  min-height: 400px;
}
</style> 