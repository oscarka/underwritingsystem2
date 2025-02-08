export interface Product {
    id: number;
    name: string;
    code: string;
    status: 'enabled' | 'disabled';
    aiParameterId: number;
    channel: {
        id: number;
        name: string;
        code: string;
    };
    insuranceCompany: {
        id: number;
        name: string;
        code: string;
    };
    productType: {
        id: number;
        name: string;
        code: string;
    };
    aiParameter: {
        id: number;
        name: string;
        code: string;
    };
    createdAt: string;
}

export interface AIParameter {
    id: number;
    name: string;
    code: string;
    underwritingRule: string;
} 