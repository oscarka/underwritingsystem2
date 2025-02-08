import type { Product, AIParameter } from './types/product';
import type { Disease, Question, Answer, UnderwritingResult } from './types/underwriting';
import type { UserInfo } from './types/user';
import type { CreateOrderRequest, Order } from './types/order';

const BASE_URL = '/api/v1';

// API请求工具函数
async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

// 模拟数据
const mockDiseases = [
    {
        id: 1,
        name: '高血压',
        code: 'HBP',
        category: '心血管疾病',
        description: '血压持续高于140/90mmHg'
    },
    {
        id: 2,
        name: '糖尿病',
        code: 'DIABETES',
        category: '内分泌疾病',
        description: '血糖水平持续升高'
    },
    {
        id: 3,
        name: '冠心病',
        code: 'CHD',
        category: '心血管疾病',
        description: '冠状动脉血管发生动脉粥样硬化'
    }
];

// 模拟问题数据
const mockQuestions: Record<number, Question[]> = {
    1: [ // 高血压相关问题
        {
            id: 101,
            content: '您的血压是否经常超过140/90mmHg？',
            type: 'single',
            options: [
                { id: 1, value: 'yes', label: '是' },
                { id: 2, value: 'no', label: '否' }
            ],
            required: true,
            diseaseId: 1
        },
        {
            id: 102,
            content: '是否正在服用降压药？',
            type: 'single',
            options: [
                { id: 1, value: 'yes', label: '是' },
                { id: 2, value: 'no', label: '否' }
            ],
            required: true,
            diseaseId: 1
        }
    ],
    2: [ // 糖尿病相关问题
        {
            id: 201,
            content: '您的空腹血糖是多少？',
            type: 'number',
            required: true,
            diseaseId: 2
        },
        {
            id: 202,
            content: '是否有糖尿病家族史？',
            type: 'single',
            options: [
                { id: 1, value: 'yes', label: '是' },
                { id: 2, value: 'no', label: '否' }
            ],
            required: true,
            diseaseId: 2
        }
    ],
    3: [ // 冠心病相关问题
        {
            id: 301,
            content: '是否有胸痛症状？',
            type: 'single',
            options: [
                { id: 1, value: 'yes', label: '有' },
                { id: 2, value: 'no', label: '没有' }
            ],
            required: true,
            diseaseId: 3
        },
        {
            id: 302,
            content: '请选择您有的症状（多选）',
            type: 'multiple',
            options: [
                { id: 1, value: 'chest_tightness', label: '胸闷' },
                { id: 2, value: 'shortness_of_breath', label: '气短' },
                { id: 3, value: 'palpitation', label: '心悸' },
                { id: 4, value: 'fatigue', label: '乏力' }
            ],
            required: true,
            diseaseId: 3
        }
    ]
};

// 模拟产品数据
const mockProduct = {
    id: 1,
    name: '康乐一生重大疾病保险',
    code: 'KLYS_2024',
    status: 'enabled',
    channel: {
        id: 1,
        name: '个人业务渠道',
        code: 'PERSONAL'
    },
    insuranceCompany: {
        id: 1,
        name: '阳光人寿保险',
        code: 'SICC'
    },
    productType: {
        id: 1,
        name: '重疾险',
        code: 'CI'
    },
    aiParameter: {
        id: 1,
        name: '标准体智能核保',
        rule: {
            id: 1,
            name: '标准体核保规则V1.0'
        }
    },
    createdAt: '2024-01-16'
};

// API接口封装
export const api = {
    // 产品相关
    getProduct: (id: number) =>
        // 临时使用模拟数据
        Promise.resolve(mockProduct),

    getAIParameter: (id: number) =>
        request<AIParameter>(`/business/ai-parameters/${id}`),

    // 疾病相关
    getDiseases: () =>
        // 临时使用模拟数据
        Promise.resolve(mockDiseases),

    searchDiseases: (keyword: string) =>
        // 临时使用模拟数据进行搜索
        Promise.resolve(mockDiseases.filter(d =>
            d.name.includes(keyword) ||
            d.code.includes(keyword.toUpperCase()) ||
            d.category.includes(keyword)
        )),

    // 问题相关
    getQuestions: (diseaseIds: number[]) =>
        // 临时使用模拟数据
        Promise.resolve(
            diseaseIds.reduce((acc, diseaseId) => {
                const questions = mockQuestions[diseaseId] || [];
                return [...acc, ...questions];
            }, [] as Question[])
        ),

    // 核保评估
    evaluate: (data: {
        productId: number;
        userInfo: UserInfo;
        diseases: number[];
        answers: Answer[];
    }) =>
        // 临时返回模拟的核保结果
        Promise.resolve({
            decision: 'manual_review',
            conclusion: '需人工核保',
            additionalFee: 0,
            specialNotice: '暂无特别说明',
            insuranceType: '暂未确定',
            reason: ''
        } as UnderwritingResult),

    // 用户相关
    saveUserInfo: (info: UserInfo) =>
        request<void>('/users/info', {
            method: 'POST',
            body: JSON.stringify(info),
        }),

    // 订单相关
    createOrder: (data: CreateOrderRequest) =>
        request<Order>('/orders', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    getOrder: (id: number) =>
        request<Order>(`/orders/${id}`),
}; 