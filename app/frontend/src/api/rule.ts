import request from '@/utils/request'
import { AxiosError } from 'axios'

interface RuleQueryParams {
    page?: number
    size?: number
    name?: string
    status?: string
    [key: string]: any
}

interface RuleData {
    name: string
    description?: string
    status: string
    [key: string]: any
}

const API_PREFIX = '/api/v1/underwriting'

export const getRuleList = async (params: RuleQueryParams) => {
    const apiUrl = '/api/v1/underwriting/rules'
    console.log('[API] 发起获取规则列表请求:', {
        params,
        url: apiUrl,
        method: 'GET',
        baseURL: request.defaults.baseURL,
        headers: request.defaults.headers
    })

    try {
        const response = await request.get(apiUrl, {
            params,
            headers: {
                'Content-Type': 'application/json'
            }
        })
        console.log('[API] 获取规则列表成功:', {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            data: response.data,
            requestUrl: response.config.url,
            requestMethod: response.config.method
        })
        return response
    } catch (error: unknown) {
        const axiosError = error as AxiosError
        console.error('[API] 获取规则列表失败:', {
            error: axiosError,
            errorMessage: axiosError.message,
            errorResponse: axiosError.response,
            errorRequest: {
                url: axiosError.config?.url,
                method: axiosError.config?.method,
                headers: axiosError.config?.headers,
                params: axiosError.config?.params,
                baseURL: axiosError.config?.baseURL
            }
        })
        throw error
    }
}

export const createRule = async (data: RuleData) => {
    const apiUrl = `${API_PREFIX}/rules`
    console.log('[API] 发起创建规则请求:', {
        data,
        url: apiUrl,
        method: 'POST'
    })

    try {
        const response = await request.post(apiUrl, data)
        console.log('[API] 创建规则成功:', {
            status: response.status,
            statusText: response.statusText,
            data: response.data
        })
        return response
    } catch (error: unknown) {
        const axiosError = error as AxiosError
        console.error('[API] 创建规则失败:', {
            error: axiosError,
            errorMessage: axiosError.message,
            errorResponse: axiosError.response,
            errorRequest: {
                url: axiosError.config?.url,
                method: axiosError.config?.method,
                data: axiosError.config?.data
            }
        })
        throw error
    }
}

export const updateRule = async (id: number, data: RuleData) => {
    const apiUrl = `${API_PREFIX}/rules/${id}`
    console.log('[API] 发起更新规则请求:', {
        id,
        data,
        url: apiUrl,
        method: 'PUT'
    })

    try {
        const response = await request.put(apiUrl, data)
        console.log('[API] 更新规则成功:', {
            status: response.status,
            statusText: response.statusText,
            data: response.data
        })
        return response
    } catch (error: unknown) {
        const axiosError = error as AxiosError
        console.error('[API] 更新规则失败:', {
            error: axiosError,
            errorMessage: axiosError.message,
            errorResponse: axiosError.response,
            errorRequest: {
                url: axiosError.config?.url,
                method: axiosError.config?.method,
                data: axiosError.config?.data
            }
        })
        throw error
    }
}

export const deleteRule = async (id: number) => {
    const apiUrl = `${API_PREFIX}/rules/${id}`
    console.log('[API] 发起删除规则请求:', {
        id,
        url: apiUrl,
        method: 'DELETE'
    })

    try {
        const response = await request.delete(apiUrl)
        console.log('[API] 删除规则成功:', {
            status: response.status,
            statusText: response.statusText,
            data: response.data
        })
        return response
    } catch (error: unknown) {
        const axiosError = error as AxiosError
        console.error('[API] 删除规则失败:', {
            error: axiosError,
            errorMessage: axiosError.message,
            errorResponse: axiosError.response,
            errorRequest: {
                url: axiosError.config?.url,
                method: axiosError.config?.method
            }
        })
        throw error
    }
} 