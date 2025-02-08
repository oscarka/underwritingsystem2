# 问题页面
<template>
  <div class="questions-page">
    <template v-if="loading">
      <van-skeleton title :row="3" />
      <van-skeleton title :row="3" />
    </template>
    
    <template v-else-if="error">
      <van-empty 
        image="error" 
        :description="error"
      >
        <template #bottom>
          <van-button round type="primary" @click="loadQuestions">
            重试
          </van-button>
        </template>
      </van-empty>
    </template>
    
    <template v-else-if="!questions.length">
      <van-empty description="暂无问题需要回答">
        <template #bottom>
          <van-button round type="primary" @click="handleBack">
            返回选择疾病
          </van-button>
        </template>
      </van-empty>
    </template>
    
    <template v-else>
      <van-form @submit="handleSubmit">
        <van-cell-group inset v-for="question in questions" :key="question.id">
          <van-field
            :name="'question_' + question.id"
            :label="question.content"
            :rules="[{ required: question.required, message: '此题为必答题' }]"
          >
            <template #input>
              <!-- 单选题 -->
              <template v-if="question.type === 'single'">
                <van-radio-group v-model="answers[question.id]">
                  <van-radio
                    v-for="option in question.options"
                    :key="option.id"
                    :name="option.value"
                  >
                    {{ option.label }}
                  </van-radio>
                </van-radio-group>
              </template>
              
              <!-- 多选题 -->
              <template v-else-if="question.type === 'multiple'">
                <van-checkbox-group v-model="answers[question.id]">
                  <van-checkbox
                    v-for="option in question.options"
                    :key="option.id"
                    :name="option.value"
                    shape="square"
                  >
                    {{ option.label }}
                  </van-checkbox>
                </van-checkbox-group>
              </template>
              
              <!-- 数字输入 -->
              <template v-else-if="question.type === 'number'">
                <van-stepper v-model="answers[question.id]" />
              </template>
            </template>
          </van-field>
        </van-cell-group>

        <div class="form-actions">
          <van-button 
            round 
            block 
            type="primary" 
            native-type="submit"
            :loading="loading"
          >
            {{ loading ? '提交中...' : '提交' }}
          </van-button>
        </div>
      </van-form>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUnderwritingStore } from '@/stores/underwriting';
import type { Question } from '@/api/types/underwriting';
import { showToast, showDialog } from 'vant';

const router = useRouter();
const store = useUnderwritingStore();

const questions = ref<Question[]>([]);
const answers = ref<Record<number, any>>({});
const loading = ref(false);
const error = ref<string | null>(null);

const loadQuestions = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const result = await store.loadQuestions();
    questions.value = result;
  } catch (e) {
    error.value = '加载问题失败，请重试';
    console.error('加载问题失败:', e);
    showToast({
      type: 'fail',
      message: '加载问题失败',
    });
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  if (loading.value) return;
  
  loading.value = true;
  try {
    const productId = router.currentRoute.value.params.productId;
    const formattedAnswers = Object.entries(answers.value).map(([questionId, answer]) => ({
      questionId: Number(questionId),
      answer: answer
    }));
    await store.submitAnswers(formattedAnswers);
    router.push(`/product/${productId}/result`);
  } catch (e) {
    console.error('提交答案失败:', e);
    showToast({
      type: 'fail',
      message: '提交失败，请重试',
    });
  } finally {
    loading.value = false;
  }
};

const handleBack = () => {
  router.push('/disease');
};

onMounted(() => {
  loadQuestions();
});
</script>

<style scoped>
.questions-page {
  padding: 16px;
}

:deep(.van-cell-group) {
  margin-bottom: 16px;
}

:deep(.van-radio-group),
:deep(.van-checkbox-group) {
  padding: 8px 0;
}

:deep(.van-radio),
:deep(.van-checkbox) {
  margin-bottom: 8px;
}

:deep(.van-radio:last-child),
:deep(.van-checkbox:last-child) {
  margin-bottom: 0;
}

.form-actions {
  margin-top: 24px;
  padding: 16px;
}
</style> 