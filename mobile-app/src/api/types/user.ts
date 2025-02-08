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

export interface UserState extends UserInfo {
    isAuthenticated: boolean;
    token?: string;
} 