import { ElMessage, ElMessageBox } from 'element-plus'

export const useMessage = () => {
    const success = (message: string) => {
        ElMessage.success(message)
    }

    const error = (message: string) => {
        ElMessage.error(message)
    }

    const warning = (message: string) => {
        ElMessage.warning(message)
    }

    const info = (message: string) => {
        ElMessage.info(message)
    }

    const confirm = (message: string, title = '提示') => {
        return ElMessageBox.confirm(message, title, {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
    }

    return {
        success,
        error,
        warning,
        info,
        confirm
    }
} 