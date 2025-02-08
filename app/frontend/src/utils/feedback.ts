import { createVNode, render, type Component } from 'vue'
import Toast from '@/components/feedback/Toast.vue'
import Loading from '@/components/feedback/Loading.vue'

// Toast 实例
let toastInstance: any = null

// Loading 实例
let loadingInstance: any = null
let loadingCount = 0

// 创建组件实例
function createInstance(component: Component) {
    const vnode = createVNode(component)
    const container = document.createElement('div')
    render(vnode, container)
    document.body.appendChild(container)
    return vnode.component?.exposed
}

// 消息提示
export const toast = {
    success(message: string) {
        if (!toastInstance) {
            toastInstance = createInstance(Toast)
        }
        toastInstance.success(message)
    },
    error(message: string) {
        if (!toastInstance) {
            toastInstance = createInstance(Toast)
        }
        toastInstance.error(message)
    },
    warning(message: string) {
        if (!toastInstance) {
            toastInstance = createInstance(Toast)
        }
        toastInstance.warning(message)
    },
    info(message: string) {
        if (!toastInstance) {
            toastInstance = createInstance(Toast)
        }
        toastInstance.info(message)
    }
}

// 加载状态
export const loading = {
    show(text = '') {
        if (!loadingInstance) {
            loadingInstance = createInstance(Loading)
        }
        if (loadingCount === 0) {
            loadingInstance.show()
        }
        loadingCount++
    },
    hide() {
        if (loadingCount > 0) {
            loadingCount--
        }
        if (loadingCount === 0 && loadingInstance) {
            loadingInstance.hide()
        }
    }
}

// 在请求拦截器中使用
export function showLoading() {
    loading.show()
}

// 在响应拦截器中使用
export function hideLoading() {
    loading.hide()
}

// 在错误处理中使用
export function showError(message: string) {
    toast.error(message)
} 