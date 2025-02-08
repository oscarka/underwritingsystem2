type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastOptions {
  duration?: number
  position?: 'top' | 'bottom'
}

interface ConfirmOptions {
  title?: string
  content: string
  confirmText?: string
  cancelText?: string
  confirmType?: 'primary' | 'danger'
}

let toastContainer: HTMLDivElement | null = null
let confirmContainer: HTMLDivElement | null = null

function createToastContainer() {
  if (toastContainer) return toastContainer

  toastContainer = document.createElement('div')
  toastContainer.className = 'toast-container'
  document.body.appendChild(toastContainer)

  const style = document.createElement('style')
  style.textContent = `
    .toast-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
    }
    
    .toast {
      padding: 12px 24px;
      border-radius: 4px;
      margin-bottom: 10px;
      color: #fff;
      font-size: 14px;
      opacity: 0;
      transform: translateX(100%);
      transition: all 0.3s ease;
    }
    
    .toast.show {
      opacity: 1;
      transform: translateX(0);
    }
    
    .toast.success {
      background-color: #67c23a;
    }
    
    .toast.error {
      background-color: #f56c6c;
    }
    
    .toast.warning {
      background-color: #e6a23c;
    }
    
    .toast.info {
      background-color: #909399;
    }
  `
  document.head.appendChild(style)

  return toastContainer
}

export function showToast(type: ToastType, message: string, options: ToastOptions = {}) {
  const container = createToastContainer()
  const { duration = 3000, position = 'top' } = options

  const toast = document.createElement('div')
  toast.className = `toast ${type}`
  toast.textContent = message

  container.appendChild(toast)

  // 触发重绘以应用过渡效果
  toast.offsetHeight
  toast.classList.add('show')

  setTimeout(() => {
    toast.classList.remove('show')
    setTimeout(() => {
      container.removeChild(toast)
    }, 300)
  }, duration)
}

export function showConfirm(options: ConfirmOptions): Promise<boolean> {
  return new Promise((resolve) => {
    const {
      title = '确认',
      content,
      confirmText = '确定',
      cancelText = '取消',
      confirmType = 'primary'
    } = options

    if (!confirmContainer) {
      confirmContainer = document.createElement('div')
      confirmContainer.className = 'confirm-container'
      document.body.appendChild(confirmContainer)

      const style = document.createElement('style')
      style.textContent = `
                .confirm-container {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }

                .confirm-box {
                    background: #fff;
                    border-radius: 4px;
                    padding: 20px;
                    width: 400px;
                    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
                }

                .confirm-title {
                    font-size: 16px;
                    font-weight: 500;
                    margin-bottom: 12px;
                }

                .confirm-content {
                    font-size: 14px;
                    color: #606266;
                    margin-bottom: 20px;
                }

                .confirm-buttons {
                    display: flex;
                    justify-content: flex-end;
                    gap: 12px;
                }

                .confirm-button {
                    padding: 8px 16px;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                    font-size: 14px;
                }

                .confirm-button.cancel {
                    background: #f4f4f5;
                    color: #909399;
                }

                .confirm-button.primary {
                    background: #409eff;
                    color: #fff;
                }

                .confirm-button.danger {
                    background: #f56c6c;
                    color: #fff;
                }
            `
      document.head.appendChild(style)
    }

    const box = document.createElement('div')
    box.className = 'confirm-box'
    box.innerHTML = `
            <div class="confirm-title">${title}</div>
            <div class="confirm-content">${content}</div>
            <div class="confirm-buttons">
                <button class="confirm-button cancel">${cancelText}</button>
                <button class="confirm-button ${confirmType}">${confirmText}</button>
            </div>
        `

    confirmContainer.appendChild(box)

    const [cancelButton, confirmButton] = box.querySelectorAll('.confirm-button')

    cancelButton.addEventListener('click', () => {
      confirmContainer?.removeChild(box)
      resolve(false)
    })

    confirmButton.addEventListener('click', () => {
      confirmContainer?.removeChild(box)
      resolve(true)
    })
  })
} 