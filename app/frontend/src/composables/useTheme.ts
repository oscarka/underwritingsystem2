import { ref, onMounted, watch } from 'vue'

// 主题类型
type Theme = 'light' | 'dark'

// 存储键名
const THEME_KEY = 'app-theme'

export function useTheme() {
    // 当前主题
    const theme = ref<Theme>('light')

    // 初始化主题
    onMounted(() => {
        // 优先使用存储的主题
        const savedTheme = localStorage.getItem(THEME_KEY) as Theme
        if (savedTheme) {
            theme.value = savedTheme
        } else {
            // 否则使用系统主题
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
            theme.value = prefersDark ? 'dark' : 'light'
        }
    })

    // 监听主题变化
    watch(theme, (newTheme) => {
        // 更新 DOM
        document.documentElement.dataset.theme = newTheme
        // 持久化存储
        localStorage.setItem(THEME_KEY, newTheme)
    }, { immediate: true })

    // 切换主题
    const toggleTheme = () => {
        theme.value = theme.value === 'light' ? 'dark' : 'light'
    }

    return {
        theme,
        toggleTheme
    }
} 