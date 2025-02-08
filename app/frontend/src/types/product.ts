export type ProductStatus = 'enabled' | 'disabled'

export interface Product {
    id: number
    name: string
    code: string
    channel?: {
        id: number
        name: string
        code: string
    }
    insuranceCompany?: {
        id: number
        name: string
        code: string
    }
    productType?: {
        id: number
        name: string
        code: string
    }
    aiParameter?: {
        id: number
        name: string
        rule?: {
            id: number
            name: string
        }
    }
    status: ProductStatus
    createdAt: string
    updatedAt?: string
} 