import { createRouter, createWebHistory } from 'vue-router';
import { useUnderwritingStore } from '@/stores/underwriting';
import { showToast } from 'vant';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/product/1/basic-info'
        },
        {
            path: '/product/:productId',
            children: [
                {
                    path: 'basic-info',
                    name: 'BasicInfo',
                    component: () => import('@/pages/basic-info/index.vue'),
                    meta: { title: '基本信息' }
                },
                {
                    path: 'disease',
                    name: 'Disease',
                    component: () => import('@/pages/disease/index.vue'),
                    meta: { title: '选择疾病' }
                },
                {
                    path: 'questions',
                    name: 'Questions',
                    component: () => import('@/pages/questions/index.vue'),
                    meta: { title: '回答问题' }
                },
                {
                    path: 'result',
                    name: 'Result',
                    component: () => import('@/pages/result/index.vue'),
                    meta: { title: '核保结论' }
                }
            ]
        },
        {
            path: '/:pathMatch(.*)*',
            redirect: to => {
                showToast('无效的链接');
                return '/';
            }
        }
    ]
});

// 路由守卫
router.beforeEach(async (to, from, next) => {
    // 设置页面标题
    document.title = `${to.meta.title || '核保'} - 移动核保系统`;

    // 检查产品ID
    const productId = to.params.productId;
    if (productId) {
        const store = useUnderwritingStore();
        try {
            // 如果store中没有productId或者与路由中的不一致，则重新加载
            if (!store.productId || store.productId.toString() !== productId.toString()) {
                await store.setProductId(Number(productId));
            }
            next();
        } catch (error) {
            console.error('加载产品信息失败:', error);
            showToast('无效的产品链接');
            next('/');
        }
    } else {
        next();
    }
});

export default router; 