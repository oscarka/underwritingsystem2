import { ref } from 'vue';

export function useConfig() {
    // 从环境变量或配置文件获取移动端基础URL
    const mobileBaseUrl = ref(import.meta.env.VITE_MOBILE_BASE_URL || 'http://localhost:3001');

    return {
        mobileBaseUrl
    };
} 