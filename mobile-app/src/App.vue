<template>
  <div class="app">
    <van-nav-bar
      :title="currentTitle"
      left-arrow
      @click-left="handleBack"
      v-if="showBackButton"
    />
    
    <main class="app-content" :class="{ 'has-nav': showBackButton }">
      <router-view v-slot="{ Component }">
        <transition name="van-fade">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const currentTitle = computed(() => (route.meta.title as string) || '核保');
const showBackButton = computed(() => {
  const path = route.path;
  return !path.includes('/basic-info') && path !== '/';
});

const handleBack = () => {
  router.back();
};
</script>

<style>
:root {
  --van-primary-color: #1989fa;
  --van-success-color: #07c160;
  --van-danger-color: #ee0a24;
  --van-warning-color: #ff976a;
  --van-text-color: #323233;
  --van-active-color: #f2f3f5;
  --van-background-color: #f7f8fa;
  --van-background-color-light: #fafafa;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica,
    Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  background-color: var(--van-background-color);
  color: var(--van-text-color);
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  padding: 16px;
}

.app-content.has-nav {
  padding-top: 56px;
}

/* 页面切换动画 */
.van-fade-enter-active,
.van-fade-leave-active {
  transition: opacity 0.3s ease;
}

.van-fade-enter-from,
.van-fade-leave-to {
  opacity: 0;
}

/* 通用样式 */
.page-container {
  background-color: var(--van-background-color-light);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 24px;
  text-align: center;
}

.form-actions {
  margin-top: 24px;
  padding: 16px;
  text-align: center;
}
</style> 