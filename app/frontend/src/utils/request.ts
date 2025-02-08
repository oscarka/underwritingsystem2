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
        console.log('发送请求:', {
            url: config.url,
            method: config.method,
            params: config.params,
            data: config.data,
            headers: config.headers,
            silent: (config as RequestConfig).silent
        })

        const token = getToken()
        if (token && config.headers) {
            config.headers['Authorization'] = `Bearer ${token}`
            console.log('添加认证头:', {
                token,
                authHeader: config.headers['Authorization']
            })
        } else {
            console.warn('未找到token或headers:', { token, headers: config.headers })
        }
        return config
    },
    (error) => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    (response: AxiosResponse) => {
        console.log('收到原始响应:', {
            url: response.config.url,
            method: response.config.method,
            status: response.status,
            headers: response.headers,
            rawData: response.data,
            silent: (response.config as RequestConfig).silent
        })

        const res = response.data as ApiResponse
        if (res.code === 200) {
            console.log('响应成功，数据结构:', {
                code: res.code,
                message: res.message,
                data: res.data
            })
            return {
                ...response,
                data: res
            }
        } else {
            console.log('响应错误:', {
                code: res.code,
                message: res.message
            })
            return Promise.reject(res)
        }
    },
    (error) => {
        console.error('API请求失败:', {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            data: error.response?.data,
            error: error.message,
            silent: (error.config as RequestConfig)?.silent
        })

        if (error.response) {
            const { status } = error.response
            const config = error.config as RequestConfig

            // 只有非静默请求才处理401错误
            if (status === 401 && !config?.silent) {
                console.log('未授权访问，清除登录状态')
                const currentPath = window.location.pathname
                // 避免在登录页重复跳转
                if (currentPath !== '/login') {
                    // 保存当前路径
                    localStorage.setItem('redirect', currentPath)
                    removeToken()
                    removeUser()
                    // 延迟跳转避免频繁刷新
                    setTimeout(() => {
                        window.location.href = '/login'
                    }, 100)
                }
            } else if (status === 403) {
                console.log('禁止访问')
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