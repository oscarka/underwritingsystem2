import type { PaginationQuery } from '@/types/api'

// 规则类型
export type RuleType = 'age' | 'occupation' | 'disease' | 'combination'

// 规则状态枚举
export enum RuleStatus {
    DRAFT = '草稿',
    ENABLED = '已启用',
    DISABLED = '已禁用',
    DELETED = '已删除',
    IMPORTED = '已导入'
}

// 疾病类别类型
export type DiseaseCategoryType = 'CARDIOVASCULAR' | 'RESPIRATORY' | 'DIGESTIVE'

// 规则基础信息
export interface BaseRule {
    id: string
    name: string
    version: string
    description?: string
    remark?: string
}

// API响应的规则信息
export interface ApiRule extends BaseRule {
    status: RuleStatus
    has_data?: boolean
    created_at: string
    updated_at: string
    questions?: Question[]
    answers?: Answer[]
}

// 前端展示的规则信息
export interface ViewRule extends BaseRule {
    status: RuleStatus
    hasData?: boolean
    createdAt: string
    updatedAt: string
}

// 规则类型（用于API请求和响应）
export type Rule = ApiRule & Partial<ViewRule>

// 规则权重配置
export interface RuleWeights {
    age: number
    occupation: number
    disease: number
}

// 阈值配置
export interface Thresholds {
    autoPass: number
    manualReview: number
}

// 通知配置
export interface NotificationConfig {
    email: boolean
    sms: boolean
    system: boolean
}

// 智核配置
export interface UnderwritingConfig {
    autoUnderwriting: boolean
    maxWaitTime: number
    concurrency: number
    weights: RuleWeights
    thresholds: Thresholds
    notifications: NotificationConfig
}

// 问题类型
export enum QuestionType {
    SINGLE = 'single',
    MULTIPLE = 'multiple',
    TEXT = 'text'
}

// 问题信息
export interface Question {
    id: string
    code: string
    content: string
    type: QuestionType
    remark?: string
    created_at: string
    updated_at: string
    required: boolean
    options?: string[]
}

// 结论类型
export type ConclusionType = 'STANDARD' | 'SUBSTANDARD' | 'DECLINE' | 'POSTPONE' | 'EXCLUSION'

// 结论对象
export interface Conclusion {
    id: number
    code: string
    name: string
    content: string
    decision: string
    emValue: number
    ruleId: number
    typeId: number
}

// 规则表单
export interface RuleForm {
    name: string
    version: string
    remark?: string
}

// 疾病大类
export interface DiseaseCategory {
    id: string
    code: string
    name: string
    description?: string
    created_at: string
    updated_at: string
}

// 疾病信息
export interface Disease {
    id: string
    category_id: string
    code: string
    name: string
    description?: string
    status: RuleStatus
    created_at: string
    updated_at: string
}

// 答案信息
export interface Answer {
    id: string
    question_id: string
    content: string
    score: number
    created_at: string
    updated_at: string
}

// 规则查询参数
export interface RuleSearchParams extends PaginationQuery {
    name?: string
    status?: RuleStatus
    diseaseCategory?: string
}

export interface Parameter {
    id: number
    name: string
    parameter_type_id: number
    parameter_type_name?: string
    rule_id: number
    rule_name?: string
    value: string
    description?: string
    status: string
    created_at: string
    updated_at: string
}

export interface ParameterType {
    id: number
    code: string
    name: string
    description?: string
    value_type: string
    default_value?: any
    validation_rules?: any
    status: string
    created_at_str: string
    updated_at_str: string
} 