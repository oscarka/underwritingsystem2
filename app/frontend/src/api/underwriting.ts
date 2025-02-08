import { get, post, put, del } from '@/utils/request'
import type { ApiResponse, PaginationQuery, PaginationData, RequestConfig } from '@/types/api'
import type { Rule, DiseaseCategory, Disease, Question, Answer, RuleSearchParams } from '@/types/underwriting'
import request from '@/utils/request'
import type { Parameter, ParameterType } from '@/types/underwriting'
import type { AxiosResponse } from 'axios'

const ruleApi = {
    // 获取规则列表
    getRules: async (params: RuleSearchParams): Promise<ApiResponse<PaginationData<Rule>>> => {
        console.log('[API] 开始获取规则列表, 参数:', params);
        try {
            const res = await get<PaginationData<Rule>>('/api/v1/underwriting/rules', { params });
            console.log('[API] 获取规则列表成功:', {
                code: res.code,
                message: res.message,
                dataLength: res.data?.list?.length,
                total: res.data?.total
            });
            return res;
        } catch (error) {
            console.error('[API] 获取规则列表失败:', error);
            throw error;
        }
    },

    // 获取规则详情
    getRuleDetail: async (id: string): Promise<ApiResponse<Rule>> => {
        console.log('[API] 开始获取规则详情, ID:', id);
        try {
            const res = await get<Rule>(`/api/v1/underwriting/rules/${id}`);
            console.log('[API] 获取规则详情成功:', {
                code: res.code,
                message: res.message,
                ruleId: res.data?.id,
                ruleName: res.data?.name
            });
            return res;
        } catch (error) {
            console.error('[API] 获取规则详情失败:', error);
            throw error;
        }
    },

    // 创建规则
    createRule: (data: Partial<Rule>): Promise<ApiResponse<Rule>> => {
        return post('/api/v1/underwriting/rules', data, {
            loading: true,
            toast: true
        } as RequestConfig)
    },

    // 更新规则
    updateRule: (id: string, data: Partial<Rule>): Promise<ApiResponse<Rule>> => {
        return put(`/api/v1/underwriting/rules/${id}`, data, {
            loading: true,
            toast: true
        } as RequestConfig)
    },

    // 删除规则
    deleteRule: (id: string): Promise<ApiResponse<void>> => {
        return del(`/api/v1/underwriting/rules/${id}`, {
            loading: true,
            toast: true
        } as RequestConfig)
    },

    // 导入规则数据
    importRuleData: (ruleId: string, file: File): Promise<ApiResponse<void>> => {
        console.log('[API] 开始导入规则数据:', {
            ruleId,
            fileName: file.name,
            fileSize: file.size
        });
        const formData = new FormData()
        formData.append('file', file)
        return post(`/api/v1/underwriting/rules/${ruleId}/import`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            loading: true,
            toast: true
        } as RequestConfig)
    },

    // 导出规则数据
    exportRuleData: (id: string): Promise<ApiResponse<Blob>> => {
        return get(`/api/v1/underwriting/rules/${id}/export`, {
            responseType: 'blob',
            loading: true,
            toast: true
        } as RequestConfig)
    },

    // 获取规则关联的疾病大类列表
    getDiseaseCategories: async (ruleId: string): Promise<ApiResponse<DiseaseCategory[]>> => {
        console.log('[API] 开始获取规则关联的疾病大类, ruleId:', ruleId)
        try {
            const res = await get<DiseaseCategory[]>(`/api/v1/underwriting/rules/${ruleId}/disease-categories`)
            console.log('[API] 获取规则关联的疾病大类成功:', {
                code: res.code,
                message: res.message,
                categoriesCount: res.data?.length
            })
            return res
        } catch (error) {
            console.error('[API] 获取规则关联的疾病大类失败:', error)
            throw error
        }
    },

    // 获取规则关联的疾病列表
    getDiseases: async (ruleId: string): Promise<ApiResponse<Disease[]>> => {
        console.log('[API] 开始获取规则关联的疾病列表, ruleId:', ruleId)
        try {
            const res = await get<Disease[]>(`/api/v1/underwriting/rules/${ruleId}/diseases`)
            console.log('[API] 获取规则关联的疾病列表成功:', {
                code: res.code,
                message: res.message,
                diseasesCount: res.data?.length
            })
            return res
        } catch (error) {
            console.error('[API] 获取规则关联的疾病列表失败:', error)
            throw error
        }
    },

    // 获取规则相关的问题列表
    getRuleQuestions: (ruleId: string): Promise<ApiResponse<Question[]>> => {
        return get(`/api/v1/underwriting/rules/${ruleId}/questions`, {
            loading: true,
            toast: true
        } as RequestConfig)
    },

    // 获取规则相关的答案列表
    getRuleAnswers: (ruleId: string): Promise<ApiResponse<Answer[]>> => {
        return get(`/api/v1/underwriting/rules/${ruleId}/answers`, {
            loading: true,
            toast: true
        } as RequestConfig)
    }
}

// 智核参数管理
export const getParameterList = async (params: Record<string, any>): Promise<ApiResponse<PaginationData<Parameter>>> => {
    console.log('开始获取参数列表, 参数:', params);
    try {
        const res = await request.get('/api/v1/underwriting/ai-parameter/', {
            params,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        console.log('获取参数列表成功:', res);
        return res.data;
    } catch (error) {
        console.error('获取参数列表失败:', error);
        throw error;
    }
}

export const getParameterTypes = async (): Promise<ApiResponse<ParameterType[]>> => {
    console.log('开始获取参数类型列表');
    try {
        const res = await request.get('/api/v1/underwriting/ai-parameter/types', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        console.log('获取参数类型列表成功:', res);
        return res.data;
    } catch (error) {
        console.error('获取参数类型列表失败:', error);
        throw error;
    }
}

// 获取规则列表（用于下拉选择）
export const getRules = async (): Promise<ApiResponse<{ id: number; name: string }[]>> => {
    try {
        const res = await request.get('/api/v1/underwriting/rules', {
            params: {
                pageSize: 1000
            },
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (res.data?.code === 200 && res.data?.data?.list) {
            return {
                code: 200,
                message: '获取规则列表成功',
                data: res.data.data.list.map((rule: { id: number; name: string }) => ({
                    id: rule.id,
                    name: rule.name
                }))
            };
        }

        return {
            code: res.data?.code || 500,
            message: res.data?.message || '获取规则列表失败',
            data: []
        };
    } catch (error) {
        console.error('获取规则列表失败:', error);
        return {
            code: 500,
            message: error instanceof Error ? error.message : '获取规则列表失败',
            data: []
        };
    }
};

export const getParameter = (id: number): Promise<ApiResponse<Parameter>> => {
    return request.get(`/api/v1/underwriting/ai-parameter/${id}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
}

export const createParameter = (data: Partial<Parameter>): Promise<ApiResponse<Parameter>> => {
    // 确保ID字段为数字类型
    const processedData = {
        ...data,
        parameter_type_id: data.parameter_type_id ? Number(data.parameter_type_id) : undefined,
        rule_id: data.rule_id ? Number(data.rule_id) : undefined,
        status: 'enabled'  // 添加默认状态
    };

    console.log('发起创建参数请求, 数据:', {
        url: '/api/v1/underwriting/ai-parameter/',  // 添加末尾斜杠
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        data: processedData
    });

    return request.post('/api/v1/underwriting/ai-parameter/', processedData, {  // 添加末尾斜杠
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    });
}

export const updateParameter = (id: number, data: Partial<Parameter>): Promise<ApiResponse<Parameter>> => {
    return request.put(`/api/v1/underwriting/ai-parameter/${id}`, data, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
}

export const deleteParameter = (id: number): Promise<ApiResponse<void>> => {
    return request.delete(`/api/v1/underwriting/ai-parameter/${id}`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
}

export default ruleApi
