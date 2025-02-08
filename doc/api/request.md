# 请求工具使用规范

## 一、基础配置

```typescript
// utils/request.ts
import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// 扩展请求配置
interface RequestConfig extends AxiosRequestConfig {
    loading?: boolean;  // 是否显示loading
    toast?: boolean;    // 是否显示错误提示
    silent?: boolean;   // 是否静默处理错误(不跳转登录页)
}

// API响应数据类型
interface ApiResponse<T = any> {
    code: number;
    message: string;
    data: T;
}

class Request {
    private instance: AxiosInstance;

    constructor(config: AxiosRequestConfig) {
        this.instance = axios.create({
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json'
            },
            ...config
        });

        this.setupInterceptors();
    }

    private setupInterceptors() {
        // 请求拦截器
        this.instance.interceptors.request.use(
            (config: RequestConfig) => {
                console.log('发送请求:', {
                    url: config.url,
                    method: config.method,
                    params: config.params,
                    data: config.data,
                    headers: config.headers,
                    silent: config.silent
                });

                const token = getToken();
                if (token && config.headers) {
                    config.headers['Authorization'] = `Bearer ${token}`;
                    console.log('添加认证头:', {
                        token,
                        authHeader: config.headers['Authorization']
                    });
                }
                return config;
            },
            (error) => {
                console.error('请求错误:', error);
                return Promise.reject(error);
            }
        );

        // 响应拦截器
        this.instance.interceptors.response.use(
            (response) => {
                console.log('收到响应:', {
                    url: response.config.url,
                    status: response.status,
                    data: response.data,
                    silent: (response.config as RequestConfig).silent
                });

                const res = response.data;
                if (res.code === 200) {
                    return response;
                } else {
                    return Promise.reject(res);
                }
            },
            (error) => {
                console.error('响应错误:', error);
                
                if (error.response) {
                    const { status } = error.response;
                    const config = error.config as RequestConfig;
                    
                    // 只有非静默请求才处理401错误
                    if (status === 401 && !config?.silent) {
                        const currentPath = window.location.pathname;
                        // 避免在登录页重复跳转
                        if (currentPath !== '/login') {
                            // 保存当前路径
                            localStorage.setItem('redirect', currentPath);
                            removeToken();
                            removeUser();
                            // 延迟跳转避免频繁刷新
                            setTimeout(() => {
                                window.location.href = '/login';
                            }, 100);
                        }
                    }
                }
                return Promise.reject(error);
            }
        );
    }

    // 封装请求方法
    public get<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.instance.get(url, config).then(res => res.data);
    }

    public post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.instance.post(url, data, config).then(res => res.data);
    }

    public put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.instance.put(url, data, config).then(res => res.data);
    }

    public delete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.instance.delete(url, config).then(res => res.data);
    }

    // 静默请求方法
    public silentGet<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.get(url, { ...config, silent: true });
    }

    public silentPost<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.post(url, data, { ...config, silent: true });
    }

    public silentPut<T = any>(url: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.put(url, data, { ...config, silent: true });
    }

    public silentDelete<T = any>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
        return this.delete(url, { ...config, silent: true });
    }
}

export default new Request({});
```

## 二、使用示例

### 1. 普通请求
```typescript
// GET请求
const getList = async () => {
    const res = await get('/api/v1/business/companies', { 
        params: { page: 1, pageSize: 10 } 
    });
    return res.data;
};

// POST请求
const createItem = async (data: any) => {
    const res = await post('/api/v1/business/companies', data);
    return res.data;
};
```

### 2. 静默请求
```typescript
// 不触发登录跳转的请求
const getDataSilently = async () => {
    const res = await silentGet('/api/v1/business/companies');
    return res.data;
};

// WebSocket相关请求
const wsConnect = async () => {
    const res = await silentGet('/api/ws/connect');
    return res.data;
};
```

## 三、类型定义

```typescript
// 分页请求参数
interface PaginationQuery {
    page: number;
    pageSize: number;
    keyword?: string;
}

// 分页响应数据
interface PaginationResponse<T> {
    list: T[];         // 数据列表
    total: number;     // 总条数
    page: number;      // 当前页码
    pageSize: number;  // 每页条数
}
```

## 四、最佳实践

1. 错误处理：
   - 使用 try-catch 捕获业务错误
   - 401错误统一处理登录跳转
   - 特殊场景使用静默请求

2. 登录处理：
   - 保存跳转前的路径
   - 避免登录页重复跳转
   - 使用延迟跳转避免频繁刷新

3. 日志记录：
   - 记录请求和响应详情
   - 记录错误信息
   - 便于问题定位

4. 代码组织：
   - 按功能模块组织API
   - 使用TypeScript类型
   - 保持代码简洁清晰 