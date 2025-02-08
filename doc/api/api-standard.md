# API 设计规范

## 一、URL 设计规范

1. 基础路径
   - 所有API都以 `/api/v1` 开头
   - 版本号使用 `v1`, `v2` 等形式

2. 资源命名
   - 使用复数名词: `/companies`, `/channels`
   - 使用小写字母和连字符: `user-profiles`
   - 避免动词: 使用 `POST /orders` 而不是 `/create-order`

3. 子资源表示
   - 使用嵌套结构: `/companies/{id}/channels`
   - 限制嵌套层级不超过3层

## 二、HTTP 方法使用

1. GET
   - 获取资源列表: `GET /companies`
   - 获取单个资源: `GET /companies/{id}`
   - 查询参数使用: `GET /companies?page=1&pageSize=10`

2. POST
   - 创建资源: `POST /companies`
   - 批量操作: `POST /companies/batch-delete`

3. PUT
   - 全量更新: `PUT /companies/{id}`
   - 幂等性操作: 多次调用结果一致

4. PATCH
   - 部分更新: `PATCH /companies/{id}`
   - 仅更新指定字段

5. DELETE
   - 删除资源: `DELETE /companies/{id}`
   - 支持批量: `DELETE /companies?ids=1,2,3`

## 三、请求规范

1. 请求头
   ```
   Content-Type: application/json
   Authorization: Bearer <token>
   Accept-Language: zh-CN
   ```

2. 查询参数
   ```typescript
   interface QueryParams {
     page?: number;         // 页码，从1开始
     pageSize?: number;     // 每页条数
     keyword?: string;      // 搜索关键词
     sortField?: string;    // 排序字段
     sortOrder?: 'asc' | 'desc'; // 排序方向
     [key: string]: any;    // 其他业务参数
   }
   ```

3. 请求体
   - POST/PUT请求使用JSON格式
   - 文件上传使用 multipart/form-data

## 四、响应规范

1. 状态码使用
   - 200: 成功
   - 201: 创建成功
   - 400: 请求参数错误
   - 401: 未认证
   - 403: 无权限
   - 404: 资源不存在
   - 500: 服务器错误

2. 响应体格式
   ```typescript
   interface ApiResponse<T = any> {
     code: number;        // 业务状态码
     message: string;     // 提示信息
     data: T;            // 响应数据
     timestamp?: number; // 时间戳
   }
   ```

3. 分页响应格式
   ```typescript
   interface PaginationResponse<T> {
     list: T[];          // 数据列表
     total: number;      // 总条数
     page: number;       // 当前页码
     pageSize: number;   // 每页条数
   }
   ```

## 五、错误处理

1. 错误响应格式
   ```typescript
   interface ErrorResponse {
     code: number;       // 错误码
     message: string;    // 错误信息
     details?: any;      // 详细信息
     timestamp: number;  // 时间戳
   }
   ```

2. 业务错误码
   - 40001: 参数验证失败
   - 40100: 未登录或Token失效
   - 40300: 无操作权限
   - 40400: 资源不存在
   - 50000: 服务器内部错误

3. 错误提示规范
   - 面向用户的友好提示
   - 包含错误原因和解决建议
   - 支持国际化

## 六、安全规范

1. 认证
   - 使用 JWT Token
   - Token 在请求头中传递
   - 支持 Token 刷新机制

2. 权限
   - 基于 RBAC 模型
   - 支持细粒度权限控制
   - 接口级别的权限校验

3. 数据安全
   - 敏感数据加密传输
   - 支持数据脱敏
   - 防止 SQL 注入和 XSS

## 七、性能优化

1. 缓存策略
   - 使用 ETag
   - 合理设置 Cache-Control
   - 支持条件请求

2. 数据压缩
   - 启用 GZIP
   - 大文件分片上传
   - 图片等资源 CDN 加速

3. 限流措施
   - 基于 IP 的限流
   - 基于用户的限流
   - 基于接口的限流 