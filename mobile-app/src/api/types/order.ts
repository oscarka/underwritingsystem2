import type { Product } from './product';
import type { UserInfo } from './user';
import type { Disease, Answer, UnderwritingResult } from './underwriting';

export interface Order {
    id?: number;
    orderNo: string;
    productId: number;
    product?: Product;
    userInfo: UserInfo;
    diseases: Disease[];
    answers: Answer[];
    underwritingResult: UnderwritingResult;
    status: 'pending' | 'completed' | 'cancelled';
    createdAt?: string;
    updatedAt?: string;
}

export interface CreateOrderRequest {
    productId: number;
    userInfo: UserInfo;
    diseases: Disease[];
    answers: Answer[];
    underwritingResult: UnderwritingResult;
} 