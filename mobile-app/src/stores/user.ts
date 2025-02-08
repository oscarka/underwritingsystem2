import { defineStore } from 'pinia';
import type { UserInfo } from '@/api/types/user';

interface UserState extends UserInfo {
    isAuthenticated: boolean;
    token?: string;
}

export const useUserStore = defineStore('user', {
    state: (): UserState => ({
        isAuthenticated: false,
        token: undefined,
        name: '',
        age: 0,
        gender: 'male',
        height: 0,
        weight: 0,
        policyNumber: '',
        idType: 'id_card',
        idNumber: '',
        phone: '',
        email: '',
    }),

    getters: {
        userInfo: (state): UserInfo => ({
            name: state.name,
            age: state.age,
            gender: state.gender,
            height: state.height,
            weight: state.weight,
            policyNumber: state.policyNumber,
            idType: state.idType,
            idNumber: state.idNumber,
            phone: state.phone,
            email: state.email,
        }),

        isComplete: (state) => {
            return Boolean(
                state.name &&
                state.age > 0 &&
                state.gender &&
                state.height > 0 &&
                state.weight > 0 &&
                state.policyNumber &&
                state.idType &&
                state.idNumber &&
                state.phone
            );
        },
    },

    actions: {
        setUserInfo(info: Partial<UserInfo>) {
            Object.assign(this, info);
        },

        reset() {
            this.$reset();
        },
    },
}); 