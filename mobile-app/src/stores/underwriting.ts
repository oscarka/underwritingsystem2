import { defineStore } from 'pinia';
import type { Disease, Question, Answer, UnderwritingResult, UserInfo } from '@/api/types/underwriting';
import type { Product } from '@/api/types/product';
import { api } from '@/api';
import { useUserStore } from './user';

interface UnderwritingState {
    productId: number | null;
    product: Product | null;
    selectedDiseases: Disease[];
    questions: Question[];
    answers: Answer[];
    result: UnderwritingResult | null;
    loading: boolean;
    error: string | null;
}

export const useUnderwritingStore = defineStore('underwriting', {
    state: (): UnderwritingState => ({
        productId: null,
        product: null,
        selectedDiseases: [],
        questions: [],
        answers: [],
        result: null,
        loading: false,
        error: null,
    }),

    getters: {
        hasSelectedDiseases: (state) => state.selectedDiseases.length > 0,
        isComplete: (state) => {
            if (!state.questions.length) return false;
            const requiredQuestions = state.questions.filter(q => q.required);
            const answeredRequired = requiredQuestions.every(q =>
                state.answers.some(a => a.questionId === q.id)
            );
            return answeredRequired;
        },
    },

    actions: {
        async setProductId(id: number) {
            this.productId = id;
            await this.loadProduct();
        },

        async loadProduct() {
            if (!this.productId) return;

            this.loading = true;
            this.error = null;

            try {
                this.product = await api.getProduct(this.productId);
            } catch (error) {
                console.error('加载产品信息失败:', error);
                this.error = '加载产品信息失败';
                throw error;
            } finally {
                this.loading = false;
            }
        },

        addDisease(disease: Disease) {
            if (!this.selectedDiseases.some(d => d.id === disease.id)) {
                this.selectedDiseases.push(disease);
                this.loadQuestions();
            }
        },

        removeDisease(diseaseId: number) {
            this.selectedDiseases = this.selectedDiseases.filter(d => d.id !== diseaseId);
            this.questions = this.questions.filter(q => q.diseaseId !== diseaseId);
            this.answers = this.answers.filter(a =>
                this.questions.some(q => q.id === a.questionId)
            );
        },

        async loadQuestions() {
            if (!this.selectedDiseases.length) return [];

            this.loading = true;
            this.error = null;

            try {
                const diseaseIds = this.selectedDiseases.map(d => d.id);
                const questions = await api.getQuestions(diseaseIds);
                this.questions = questions;
                return questions;
            } catch (error) {
                console.error('加载问题失败:', error);
                this.error = '加载问题失败';
                return [];
            } finally {
                this.loading = false;
            }
        },

        setAnswer(answer: Answer) {
            const index = this.answers.findIndex(a => a.questionId === answer.questionId);
            if (index > -1) {
                this.answers[index] = answer;
            } else {
                this.answers.push(answer);
            }
        },

        async evaluate() {
            if (!this.productId || !this.isComplete) {
                this.error = '请完成所有必填问题';
                return;
            }

            this.loading = true;
            this.error = null;

            try {
                const userStore = useUserStore();
                if (!userStore.isComplete) {
                    this.error = '请完善个人信息';
                    return;
                }

                this.result = await api.evaluate({
                    productId: this.productId,
                    diseases: this.selectedDiseases.map(d => d.id),
                    answers: this.answers,
                    userInfo: userStore.userInfo
                });

                return this.result;
            } catch (error) {
                console.error('核保评估失败:', error);
                this.error = '核保评估失败';
                throw error;
            } finally {
                this.loading = false;
            }
        },

        reset() {
            this.$reset();
        },

        async submitAnswers(answers: Array<{ questionId: number; answer: any }>) {
            this.loading = true;
            this.error = null;

            try {
                // 开发阶段，直接返回成功
                console.log('提交的答案:', answers);
                return true;
            } catch (error) {
                console.error('提交答案失败:', error);
                this.error = '提交答案失败';
                throw error;
            } finally {
                this.loading = false;
            }
        },
    },
}); 