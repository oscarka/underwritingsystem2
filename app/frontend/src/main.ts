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