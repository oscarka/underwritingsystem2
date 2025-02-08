export interface UserInfo {
    name: string;
    age: number;
    gender: 'male' | 'female';
    height: number;
    weight: number;
    policyNumber: string;
    idType: 'id_card' | 'passport';
    idNumber: string;
    phone: string;
    email: string;
}

export interface Disease {
    id: number;
    name: string;
    code: string;
    category: string;
    description?: string;
}

export interface Question {
    id: number;
    diseaseId: number;
    type: 'single' | 'multiple' | 'number' | 'text';
    content: string;
    required: boolean;
    options?: Array<{
        id: number;
        value: string;
        label: string;
    }>;
}

export interface Answer {
    questionId: number;
    value: string | number | string[];
}

export interface UnderwritingResult {
    decision: 'accept' | 'reject' | 'manual_review';
    conclusion?: string;
    additionalFee?: number;
    specialNotice?: string;
    insuranceType?: string;
    reason?: string;
    additionalInfo?: Record<string, any>;
} 