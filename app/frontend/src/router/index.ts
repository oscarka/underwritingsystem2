import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import DashboardView from '@/views/DashboardView.vue'
import ChannelView from '@/views/ChannelView.vue'
import CompanyView from '@/views/CompanyView.vue'
import LoginView from '@/views/LoginView.vue'
import { isLoggedIn } from '@/utils/auth'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: LoginView
        },
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '',
                    redirect: '/dashboard'
                },
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: DashboardView
                },
                // 产品管理
                {
                    path: 'product/channels',
                    name: 'channels',
                    component: ChannelView
                },
                {
                    path: 'product/companies',
                    name: 'companies',
                    component: CompanyView
                },
                {
                    path: 'product/config',
                    name: 'product-config',
                    component: () => import('@/views/product/ProductConfigView.vue'),
                    meta: {
                        title: '产品配置',
                        requiresAuth: true
                    }
                },
                // 核保管理
                {
                    path: 'underwriting/rules',
                    name: 'underwriting-rules',
                    component: () => {
                        console.log('[Router] 开始加载核保规则组件')
                        return import('@/views/underwriting/RulesView.vue').then(module => {
                            console.log('[Router] 核保规则组件加载成功')
                            return module
                        }).catch(error => {
                            console.error('[Router] 核保规则组件加载失败:', error)
                            throw error
                        })
                    }
                },
                {
                    path: 'underwriting/rules/:id/detail',
                    name: 'underwriting-rule-detail',
                    component: () => import('@/views/underwriting/RuleDetailView.vue')
                },
                {
                    path: 'underwriting/rules/:id/edit',
                    name: 'underwriting-rule-edit',
                    component: () => import('@/views/underwriting/RuleEditView.vue')
                },
                {
                    path: 'underwriting/ai-parameter',
                    name: 'underwriting-ai-parameter',
                    component: () => import('@/views/underwriting/AIParameterView.vue'),
                    meta: {
                        title: '智核参数管理',
                        requiresAuth: true
                    }
                },
                {
                    path: 'underwriting/ai-parameter/create',
                    component: () => import('@/views/underwriting/AIParameterEditView.vue'),
                    meta: {
                        title: '新增智核参数',
                        requiresAuth: true
                    }
                },
                {
                    path: 'underwriting/ai-parameter/:id',
                    component: () => import('@/views/underwriting/AIParameterDetailView.vue'),
                    meta: {
                        title: '智核参数详情',
                        requiresAuth: true
                    }
                },
                {
                    path: 'underwriting/ai-parameter/:id/edit',
                    component: () => import('@/views/underwriting/AIParameterEditView.vue'),
                    meta: {
                        title: '编辑智核参数',
                        requiresAuth: true
                    }
                }
            ]
        }
    ]
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
    console.log('[Router] 路由导航开始:', {
        to: {
            path: to.path,
            name: to.name,
            params: to.params,
            query: to.query,
            meta: to.meta,
            fullPath: to.fullPath,
            matched: to.matched.map(record => ({
                path: record.path,
                name: record.name,
                components: Object.keys(record.components || {}),
                props: record.props
            }))
        },
        from: {
            path: from.path,
            name: from.name,
            fullPath: from.fullPath
        },
        isLoggedIn: isLoggedIn()
    })

    // 特别记录核保规则相关路由
    if (to.path.includes('underwriting/rules')) {
        console.log('[Router] 访问核保规则页面:', {
            matchedComponents: to.matched.map(record => record.components),
            params: to.params,
            query: to.query
        })
    }

    // 如果用户访问登录页面且已经登录，重定向到首页
    if (to.path === '/login' && isLoggedIn()) {
        console.log('用户已登录，重定向到首页')
        next('/')
        return
    }

    // 如果用户访问需要认证的页面但未登录，重定向到登录页面
    if (to.path !== '/login' && !isLoggedIn()) {
        console.log('用户未登录，重定向到登录页面')
        next('/login')
        return
    }

    console.log('允许导航到:', to.path)
    next()
})

// 全局后置钩子
router.afterEach((to, from) => {
    console.log('[Router] 路由导航完成:', {
        from: from.path,
        to: to.path,
        title: to.meta?.title,
        timestamp: new Date().toISOString()
    })

    // 特别记录核保规则相关路由完成情况
    if (to.path.includes('underwriting/rules')) {
        console.log('[Router] 核保规则页面加载完成:', {
            path: to.path,
            name: to.name,
            timestamp: new Date().toISOString()
        })
    }
})

export default router
