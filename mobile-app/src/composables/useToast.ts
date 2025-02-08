import { showToast as vantShowToast } from 'vant';

interface ToastOptions {
    type?: 'success' | 'fail' | 'loading' | 'text';
    message: string;
    duration?: number;
}

export function useToast() {
    const show = (options: ToastOptions) => {
        vantShowToast({
            type: options.type || 'text',
            message: options.message,
            duration: options.duration || 2000,
        });
    };

    return {
        show
    };
} 