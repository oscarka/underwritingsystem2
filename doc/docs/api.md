# 渠道管理接口文档

## 通用说明

### 基础路径
所有接口都以 `/business/channel/api` 为基础路径

### 响应格式
```typescript
// 成功响应
interface SuccessResponse<T> {
  success: true
  message?: string
  data: T
}

// 错误响应
interface ErrorResponse {
  success: false
  message: string
}

// 分页响应
interface PaginatedResponse<T> {
  success: true
  data: T[]
  total: number
  page: number
  pageSize: number
}
```

### 状态码说明
- 200: 请求成功
- 400: 请求参数错误
- 401: 未登录或登录过期
- 403: 无权限访问
- 404: 资源不存在
- 500: 服务器内部错误

### 数据类型定义
```typescript
// 渠道状态枚举
enum ChannelStatus {
  ENABLED = 'enabled',   // 启用
  DISABLED = 'disabled'  // 禁用
}

// 渠道信息
interface Channel {
  id: number            // 渠道ID
  name: string          // 渠道名称
  code: string          // 渠道编码
  description?: string  // 描述
  status: ChannelStatus // 状态
  created_at: string    // 创建时间
  updated_at: string    // 更新时间
}

// 查询参数
interface ChannelQuery {
  name?: string         // 渠道名称,模糊匹配
  status?: ChannelStatus// 状态
  page?: number         // 页码,默认1
  pageSize?: number     // 每页条数,默认10
}
```

## 接口列表

### 获取渠道列表

- 路径: GET /channels
- 功能: 分页获取渠道列表
- 请求参数: 
  ```typescript
  ChannelQuery
  ```
- 响应数据:
  ```typescript
  PaginatedResponse<Channel>
  ```
- 示例:
  ```bash
  # 请求
  GET /business/channel/api/channels?name=测试&status=enabled&page=1&pageSize=10
  
  # 响应
  {
    "success": true,
    "data": [
      {
        "id": 1,
        "name": "测试渠道",
        "code": "TEST_CHANNEL",
        "description": "这是一个测试渠道",
        "status": "enabled",
        "created_at": "2024-01-24 10:00:00",
        "updated_at": "2024-01-24 10:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 10
  }
  ```

### 创建渠道

- 路径: POST /channels
- 功能: 创建新渠道
- 请求参数:
  ```typescript
  {
    name: string        // 必填,最大长度50
    code: string        // 必填,最大长度30,只能包含大写字母、数字和下划线
    description?: string// 可选,描述
    status?: ChannelStatus // 可选,默认enabled
  }
  ```
- 响应数据:
  ```typescript
  SuccessResponse<Channel>
  ```
- 示例:
  ```bash
  # 请求
  POST /business/channel/api/channels
  {
    "name": "测试渠道",
    "code": "TEST_CHANNEL",
    "description": "这是一个测试渠道"
  }
  
  # 响应
  {
    "success": true,
    "message": "创建成功",
    "data": {
      "id": 1,
      "name": "测试渠道",
      "code": "TEST_CHANNEL",
      "description": "这是一个测试渠道",
      "status": "enabled",
      "created_at": "2024-01-24 10:00:00",
      "updated_at": "2024-01-24 10:00:00"
    }
  }
  ```

### 更新渠道

- 路径: PUT /channels/{id}
- 功能: 更新渠道信息
- 请求参数:
  ```typescript
  {
    name: string        // 必填,最大长度50
    code: string        // 必填,最大长度30,只能包含大写字母、数字和下划线
    description?: string// 可选,描述
    status?: ChannelStatus // 可选
  }
  ```
- 响应数据:
  ```typescript
  SuccessResponse<Channel>
  ```
- 示例:
  ```bash
  # 请求
  PUT /business/channel/api/channels/1
  {
    "name": "测试渠道更新",
    "code": "TEST_CHANNEL",
    "description": "这是一个更新后的测试渠道",
    "status": "disabled"
  }
  
  # 响应
  {
    "success": true,
    "message": "更新成功",
    "data": {
      "id": 1,
      "name": "测试渠道更新", 
      "code": "TEST_CHANNEL",
      "description": "这是一个更新后的测试渠道",
      "status": "disabled",
      "created_at": "2024-01-24 10:00:00",
      "updated_at": "2024-01-24 11:00:00"
    }
  }
  ```

### 删除渠道

- 路径: DELETE /channels/{id}
- 功能: 删除指定渠道
- 请求参数: 无
- 响应数据:
  ```typescript
  SuccessResponse<null>
  ```
- 示例:
  ```bash
  # 请求
  DELETE /business/channel/api/channels/1
  
  # 响应
  {
    "success": true,
    "message": "删除成功"
  }
  ```

## 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400001 | 渠道名称不能为空 | 检查name字段 |
| 400002 | 渠道编码不能为空 | 检查code字段 |
| 400003 | 渠道编码格式错误 | code只能包含大写字母、数字和下划线 |
| 400004 | 渠道编码已存在 | 更换code值 |
| 400005 | 渠道名称超长 | name长度不能超过50 |
| 400006 | 渠道编码超长 | code长度不能超过30 |
| 404001 | 渠道不存在 | 检查渠道id是否正确 |

## 注意事项

1. 所有接口都需要登录权限
2. 创建和更新接口会对参数进行严格校验
3. 渠道编码创建后不建议修改
4. 删除操作不可恢复,请谨慎操作 