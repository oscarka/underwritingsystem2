import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// 引入 Vant
import Vant from 'vant';
import 'vant/lib/index.css';

// 创建应用实例
const app = createApp(App);

// 使用插件
app.use(createPinia());
app.use(router);
app.use(Vant);

// 挂载应用
app.mount('#app'); 