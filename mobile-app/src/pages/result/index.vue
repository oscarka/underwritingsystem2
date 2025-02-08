# 核保结论页面
<template>
  <div class="result-page">
    <template v-if="loading">
      <van-skeleton title :row="3" />
    </template>
    
    <template v-else-if="error">
      <van-empty 
        image="error" 
        :description="error"
      >
        <template #bottom>
          <van-button round type="primary" @click="handleRetry">
            重试
          </van-button>
        </template>
      </van-empty>
    </template>
    
    <template v-else>
      <div class="result-card">
        <div class="result-header" :class="result.decision">
          <div class="conclusion-icon">
            <span v-if="result.decision === 'accept'">✅</span>
            <span v-else-if="result.decision === 'reject'">❌</span>
            <span v-else>⚠️</span>
          </div>
          <h2 class="conclusion-text">{{ result.conclusion }}</h2>
        </div>

        <div class="result-content">
          <div class="result-item">
            <label>承保类型</label>
            <span>{{ result.insuranceType }}</span>
          </div>

          <div class="result-item">
            <label>加费比例</label>
            <span>{{ result.additionalFee }}%</span>
          </div>

          <div class="result-item">
            <label>特别说明</label>
            <span>{{ result.specialNotice }}</span>
          </div>
        </div>
      </div>

      <div class="action-bar">
        <van-button 
          round 
          block 
          type="primary" 
          :loading="loading"
          @click="handleConfirm"
        >
          确认投保
        </van-button>
        <van-button 
          round 
          block 
          plain 
          @click="handleRestart"
          style="margin-top: 12px;"
        >
          重新核保
        </van-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUnderwritingStore } from '@/stores/underwriting';
import { showToast } from 'vant';

const router = useRouter();
const store = useUnderwritingStore();

const loading = ref(false);
const error = ref<string | null>(null);

const result = computed(() => store.result || {
  decision: 'manual_review',
  conclusion: '需人工核保',
  additionalFee: 0,
  specialNotice: '暂无特别说明',
  insuranceType: '暂未确定',
  reason: ''
});

// 重试
const handleRetry = async () => {
  error.value = null;
  loading.value = true;
  
  try {
    await store.evaluate();
  } catch (err) {
    error.value = '获取核保结论失败，请重试';
  } finally {
    loading.value = false;
  }
};

// 重新开始
const handleRestart = () => {
  store.reset();
  router.replace('/');
};

// 确认投保
const handleConfirm = async () => {
  if (loading.value) return;
  
  loading.value = true;
  try {
    await store.evaluate();
    showToast({
      type: 'success',
      message: '投保申请已提交'
    });
    
    // 重置状态并返回首页
    store.reset();
    router.replace('/');
  } catch (error) {
    console.error('提交失败:', error);
    showToast({
      type: 'fail',
      message: '提交失败，请重试'
    });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (!store.result) {
    handleRetry();
  }
});
</script>

<style scoped>
.result-page {
  padding: 16px;
  min-height: 100vh;
  background: #f5f5f5;
}

.result-card {
  background-color: #fff;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.result-header {
  padding: 24px;
  text-align: center;
  background-color: #ff976a;
  color: white;
}

.result-header.accept {
  background-color: #07c160;
}

.result-header.reject {
  background-color: #ee0a24;
}

.conclusion-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.conclusion-text {
  font-size: 20px;
  font-weight: 500;
  margin: 0;
}

.result-content {
  padding: 16px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item label {
  color: #666;
  font-size: 14px;
}

.result-item span {
  color: #333;
  font-size: 14px;
}

.action-bar {
  padding: 16px;
}

:deep(.van-button) {
  height: 44px;
}
</style> 