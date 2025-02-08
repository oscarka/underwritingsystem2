import type { AxiosRequestConfig } from 'axios'

// 请求配置
export interface RequestConfig extends AxiosRequestConfig {
    loading?: boolean;  // 是否显示loading
    toast?: boolean;    // 是否显示错误提示
    silent?: boolean;   // 是否静默处理错误(不跳转登录页)
    retry?: number;     // 重试次数
    retryDelay?: number;// 重试延迟
    cache?: boolean;    // 是否缓存
}

// API 响应类型
export interface ApiResponse<T = any> {
    code: number        // 业务状态码
    message: string    // 提示信息
    data: T            // 响应数据
}

// 分页响应类型
export interface PaginatedResponse<T = any> {
    code: number
    message: string
    data: {
        list: T[]
        total: number
        page: number
        pageSize: number
    }
}

// 分页查询参数
export interface PaginationQuery {
    page?: number       // 当前页码
    pageSize?: number   // 每页条数
    keyword?: string    // 关键词搜索
}

// 分页响应数据
export interface PaginationData<T> {
    list: T[]         // 数据列表
    total: number      // 总条数
    page: number        // 当前页码
    pageSize: number    // 每页条数
}

// 排序参数
export interface SortQuery {
    field: string     // 排序字段
    order: 'asc' | 'desc'  // 排序方向
}

// 基础的查询参数
export interface BaseQuery extends Partial<PaginationQuery> {
    keyword?: string  // 关键词搜索
    sort?: SortQuery  // 排序参数
} 