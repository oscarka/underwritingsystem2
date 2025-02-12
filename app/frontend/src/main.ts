import './assets/main.css'
import './styles/theme.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import BaseComponents from './components/base'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

console.log('[main] Creating Vue app...')

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
    console.error('[Vue Error]', {
        error: err,
        component: instance?.$options.name || 'Unknown',
        info,
        timestamp: new Date().toISOString()
    })
}

// 性能监控
if (window.performance) {
    const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            console.log('[Performance]', {
                name: entry.name,
                type: entry.entryType,
                duration: entry.duration,
                timestamp: new Date().toISOString()
            })
        })
    })
    observer.observe({ entryTypes: ['navigation', 'resource', 'paint'] })
}

// 注册路由
app.use(router)
console.log('[main] Router registered')

// 注册基础组件
app.use(BaseComponents)
console.log('[main] Base components registered')

app.use(ElementPlus)

// 挂载应用
app.mount('#app')
console.log('[main] App mounted') 