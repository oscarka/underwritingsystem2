// 渠道状态枚举
export enum ChannelStatus {
    ENABLED = 'enabled',   // 启用
    DISABLED = 'disabled'  // 禁用
}

// 渠道信息
export interface Channel {
    id: number            // 渠道ID
    name: string          // 渠道名称
    code: string          // 渠道编码
    description?: string  // 描述
    status: ChannelStatus // 状态
    config?: any          // 渠道配置
    createTime: string    // 创建时间
    updateTime?: string    // 更新时间
}

// 查询参数
export interface ChannelQuery {
    name?: string         // 渠道名称,模糊匹配
    status?: ChannelStatus// 状态
    page?: number         // 页码,默认1
    pageSize?: number     // 每页条数,默认10
}

// 创建渠道参数
export interface CreateChannelParams {
    name: string         // 渠道名称
    code: string         // 渠道编码
    description?: string // 描述
    config?: any        // 渠道配置
    status?: ChannelStatus// 状态
}

// 更新渠道参数
export interface UpdateChannelParams extends Partial<CreateChannelParams> {
    id: number          // 渠道ID
}

// API响应类型
export interface ApiResponse<T> {
    success: boolean
    message?: string
    data?: T
}

// 分页响应
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
    total: number
    page: number
    pageSize: number
} 