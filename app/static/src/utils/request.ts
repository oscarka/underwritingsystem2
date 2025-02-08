import axios from 'axios';
import { message } from 'antd';

// 创建axios实例
const request = axios.create({
    baseURL: '/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器
request.interceptors.request.use(
    (config) => {
        // 添加token
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
request.interceptors.response.use(
    (response) => {
        const res = response.data;
        if (res.code !== 200) {
            message.error(res.message || '请求失败');
            return Promise.reject(res);
        }
        return res;
    },
    (error) => {
        message.error(error.message || '网络错误');
        return Promise.reject(error);
    }
);

export default request; 