<template>
  <div class="base-dialog-overlay" @click="handleOverlayClick">
    <div class="base-dialog" @click.stop>
      <div v-if="title" class="base-dialog__header">
        {{ title }}
      </div>
      
      <div class="base-dialog__content" v-html="content"></div>
      
      <div class="base-dialog__footer">
        <button 
          v-if="showCancel" 
          class="base-dialog__btn base-dialog__btn--cancel"
          @click="handleCancel"
        >
          {{ cancelText }}
        </button>
        <button 
          class="base-dialog__btn base-dialog__btn--confirm"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  title?: string;
  content: string;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
  closeOnClickOverlay?: boolean;
}>(), {
  confirmText: '确定',
  cancelText: '取消',
  showCancel: false,
  closeOnClickOverlay: true
});

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

function handleConfirm() {
  emit('confirm');
  emit('close');
}

function handleCancel() {
  emit('cancel');
  emit('close');
}

function handleOverlayClick() {
  if (props.closeOnClickOverlay) {
    emit('close');
  }
}
</script>

<style scoped>
.base-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.base-dialog {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.base-dialog__header {
  padding: 16px;
  font-size: 18px;
  font-weight: 500;
  border-bottom: 1px solid #eee;
}

.base-dialog__content {
  padding: 16px;
  line-height: 1.5;
}

.base-dialog__footer {
  padding: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #eee;
}

.base-dialog__btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.base-dialog__btn:hover {
  opacity: 0.8;
}

.base-dialog__btn--cancel {
  background-color: #f5f5f5;
  color: #666;
}

.base-dialog__btn--confirm {
  background-color: var(--color-primary, #007aff);
  color: white;
}
</style> 