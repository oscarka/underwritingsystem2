import { createVNode, render } from 'vue';
import BaseDialog from './BaseDialog.vue';

interface DialogOptions {
    title?: string;
    content: string;
    confirmText?: string;
    cancelText?: string;
    onConfirm?: () => void;
    onCancel?: () => void;
}

let container: HTMLElement | null = null;

export const Dialog = {
    show(options: DialogOptions) {
        if (!container) {
            container = document.createElement('div');
            document.body.appendChild(container);
        }

        const vnode = createVNode(BaseDialog, {
            ...options,
            onClose: () => {
                render(null, container!);
            }
        });

        render(vnode, container);
    }
}; 