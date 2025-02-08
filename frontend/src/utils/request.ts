import axios from 'axios'
import { getToken } from '@/utils/auth'

const service = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(
    (config) => {
        const token = getToken()
        console.log('Request interceptor - Token:', token)
        console.log('Request interceptor - URL:', config.url)

        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`
            console.log('Request interceptor - Added Authorization header:', config.headers.Authorization)
        }
        return config
    },
    (error) => {
        console.error('Request interceptor error:', error)
        return Promise.reject(error)
    }
)

export default service 