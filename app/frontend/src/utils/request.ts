import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { getToken } from './auth'
import { showToast } from './toast'
import { removeToken, removeUser } from './auth'
import { useRouter } from 'vue-router'

// API响应数据类型
export interface ApiResponse<T = any> {
    code: number
    message: string
    data: T
}

// 扩展请求配置类型
export interface RequestConfig extends AxiosRequestConfig {
    loading?: boolean;  // 是否显示loading
    toast?: boolean;    // 是否显示错误提示
    silent?: boolean;   // 是否静默处理错误(不跳转登录页)
}

// 创建axios实例
const request = axios.create({
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器
request.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const requestId = Math.random().toString(36).substring(7);
        console.log(`[请求开始] [${requestId}] 发送请求:`, {
            url: config.url,
            method: config.method,
            params: config.params,
            data: config.data,
            headers: config.headers,
            silent: (config as RequestConfig).silent,
            timestamp: new Date().toISOString()
        })

        const token = getToken()
        if (token && config.headers) {
            config.headers['Authorization'] = `Bearer ${token}`
            console.log(`[Token验证] [${requestId}] 添加认证头:`, {
                tokenExists: !!token,
                tokenLength: token.length,
                authHeader: config.headers['Authorization'],
                timestamp: new Date().toISOString()
            })
        } else {
            console.warn(`[Token警告] [${requestId}] 未找到token或headers:`, {
                tokenExists: !!token,
                headersExist: !!config.headers,
                timestamp: new Date().toISOString()
            })
        }
        return config
    },
    (error) => {
        console.error('[请求错误]', {
            error: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString()
        })
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    (response: AxiosResponse) => {
        const requestId = Math.random().toString(36).substring(7);
        console.log(`[响应成功] [${requestId}] 收到响应:`, {
            url: response.config.url,
            method: response.config.method,
            status: response.status,
            headers: response.headers,
            data: response.data,
            silent: (response.config as RequestConfig).silent,
            timestamp: new Date().toISOString()
        })

        const res = response.data as ApiResponse
        if (res.code === 200) {
            console.log(`[响应处理] [${requestId}] 响应成功:`, {
                code: res.code,
                message: res.message,
                hasData: !!res.data,
                timestamp: new Date().toISOString()
            })
            return {
                ...response,
                data: res
            }
        } else {
            console.warn(`[响应异常] [${requestId}] 响应错误:`, {
                code: res.code,
                message: res.message,
                timestamp: new Date().toISOString()
            })
            return Promise.reject(res)
        }
    },
    (error) => {
        const requestId = Math.random().toString(36).substring(7);
        console.error(`[请求失败] [${requestId}] API请求失败:`, {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            error: error.message,
            stack: error.stack,
            silent: (error.config as RequestConfig)?.silent,
            timestamp: new Date().toISOString()
        })

        if (error.response) {
            const { status } = error.response
            const config = error.config as RequestConfig

            // 只有非静默请求才处理401错误
            if (status === 401 && !config?.silent) {
                console.log(`[认证失败] [${requestId}] 未授权访问:`, {
                    currentPath: window.location.pathname,
                    timestamp: new Date().toISOString()
                })
                const currentPath = window.location.pathname
                // 避免在登录页重复跳转
                if (currentPath !== '/login') {
                    console.log(`[重定向] [${requestId}] 准备跳转到登录页:`, {
                        from: currentPath,
                        timestamp: new Date().toISOString()
                    })
                    // 保存当前路径用于登录后重定向
                    localStorage.setItem('redirect', currentPath)
                    removeToken()
                    removeUser()
                    // 立即跳转到登录页
                    window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
                }
            } else if (status === 403) {
                console.warn(`[权限拒绝] [${requestId}] 禁止访问:`, {
                    url: error.config?.url,
                    timestamp: new Date().toISOString()
                })
                showToast('error', '无权限访问')
            }
        }
        return Promise.reject(error)
    }
)

// 封装GET请求
export function get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return request.get(url, config).then(response => response.data)
}

// 封装POST请求
export function post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    console.log('POST请求数据:', data)
    return request.post(url, data, config).then(response => response.data)
}

// 封装PUT请求
export function put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    console.log('PUT请求数据:', data)
    return request.put(url, data, config).then(response => response.data)
}

// 封装DELETE请求
export function del<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return request.delete(url, config).then(response => response.data)
}

// 静默GET请求
export function silentGet<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return get(url, { ...config, silent: true })
}

// 静默POST请求
export function silentPost<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return post(url, data, { ...config, silent: true })
}

// 静默PUT请求
export function silentPut<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return put(url, data, { ...config, silent: true })
}

// 静默DELETE请求
export function silentDel<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return del(url, { ...config, silent: true })
}

export default request 