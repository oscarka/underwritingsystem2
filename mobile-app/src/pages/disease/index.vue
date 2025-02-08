# 疾病选择页面
<template>
  <div class="disease-page">
    <van-search
      v-model="searchKeyword"
      placeholder="搜索疾病名称"
      @update:model-value="handleSearch"
    />

    <div class="disease-content">
      <template v-if="loading">
        <van-skeleton title :row="3" />
        <van-skeleton title :row="3" />
      </template>
      
      <template v-else-if="diseases.length === 0">
        <van-empty description="暂无疾病数据" />
      </template>
      
      <template v-else>
        <div 
          v-for="category in groupedDiseases" 
          :key="category.name"
          class="disease-category"
        >
          <van-cell :title="category.name" />
          <div class="disease-tags">
            <van-tag
              v-for="disease in category.diseases"
              :key="disease.id"
              :type="isSelected(disease) ? 'primary' : 'default'"
              size="medium"
              @click="toggleDisease(disease)"
              class="disease-tag"
            >
              {{ disease.name }}
            </van-tag>
          </div>
        </div>
      </template>

      <div v-if="selectedDiseases.length > 0" class="selected-diseases">
        <van-cell title="已选择的疾病" />
        <div class="disease-tags">
          <van-tag
            v-for="disease in selectedDiseases"
            :key="disease.id"
            type="primary"
            size="medium"
            closeable
            @close="removeDisease(disease)"
            class="disease-tag"
          >
            {{ disease.name }}
          </van-tag>
        </div>
      </div>
    </div>

    <div class="submit-bar">
      <van-submit-bar
        :button-text="loading ? '加载中...' : '下一步'"
        :loading="loading"
        :disabled="!canProceed"
        @submit="handleNext"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUnderwritingStore } from '@/stores/underwriting';
import type { Disease } from '@/api/types/underwriting';
import { api } from '@/api';
import { showToast } from 'vant';

const router = useRouter();
const route = useRoute();
const store = useUnderwritingStore();

const diseases = ref<Disease[]>([]);
const loading = ref(false);
const searchKeyword = ref('');

// 获取所有疾病
const loadDiseases = async () => {
  loading.value = true;
  try {
    diseases.value = await api.getDiseases();
  } catch (error) {
    console.error('加载疾病列表失败:', error);
    showToast({
      type: 'fail',
      message: '加载疾病列表失败',
    });
  } finally {
    loading.value = false;
  }
};

// 搜索疾病
const handleSearch = async () => {
  if (!searchKeyword.value) {
    await loadDiseases();
    return;
  }

  loading.value = true;
  try {
    diseases.value = await api.searchDiseases(searchKeyword.value);
  } catch (error) {
    console.error('搜索疾病失败:', error);
    showToast({
      type: 'fail',
      message: '搜索疾病失败',
    });
  } finally {
    loading.value = false;
  }
};

// 按类别分组疾病
const groupedDiseases = computed(() => {
  const groups: { [key: string]: Disease[] } = {};
  diseases.value.forEach(disease => {
    if (!groups[disease.category]) {
      groups[disease.category] = [];
    }
    groups[disease.category].push(disease);
  });

  return Object.entries(groups).map(([name, diseases]) => ({
    name,
    diseases
  }));
});

// 已选择的疾病
const selectedDiseases = computed(() => store.selectedDiseases);

// 检查疾病是否已选择
const isSelected = (disease: Disease) => 
  selectedDiseases.value.some(d => d.id === disease.id);

// 切换疾病选择状态
const toggleDisease = (disease: Disease) => {
  if (isSelected(disease)) {
    store.removeDisease(disease.id);
  } else {
    store.addDisease(disease);
  }
};

// 移除已选择的疾病
const removeDisease = (disease: Disease) => {
  store.removeDisease(disease.id);
};

// 是否可以进入下一步
const canProceed = computed(() => selectedDiseases.value.length > 0);

// 进入下一步
const handleNext = () => {
  if (canProceed.value) {
    const productId = route.params.productId;
    router.push(`/product/${productId}/questions`);
  }
};

onMounted(() => {
  loadDiseases();
});
</script>

<style scoped>
.disease-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.disease-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 50px;
}

.disease-category {
  margin-bottom: 16px;
}

.disease-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
}

.disease-tag {
  cursor: pointer;
}

.selected-diseases {
  margin-top: 24px;
  padding: 16px;
  background-color: var(--van-background-color-light);
  border-radius: 8px;
}

.submit-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

:deep(.van-submit-bar) {
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.van-submit-bar__button) {
  border-radius: 20px;
}
</style> 