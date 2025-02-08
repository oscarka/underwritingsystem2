# API设计规范文档

## 一、基础规范

### 1.1 通用原则
- API 必须遵循 RESTful 设计规范
- 所有接口都必须进行版本控制
- 统一使用 HTTPS 协议
- 接口基础路径：`/api/v1/`

### 1.2 版本控制
- 版本号在 URL 中体现：`/api/v1/`
- 主版本号变更代表不兼容的 API 修改
- 次版本号变更代表向下兼容的功能性新增
- 修订号变更代表向下兼容的问题修正

### 1.3 认证方式
1. **公开接口**
   - 无需认证
   - URL 路径包含 `/public/`
   - 例如：`/api/v1/public/products`

2. **认证接口**
   - 使用 JWT Token 认证
   - 在 Header 中携带：`Authorization: Bearer <token>`
   - 支持静默请求模式（不触发登录跳转）

### 1.4 响应格式
```json
{
  "code": 200,          // 状态码
  "message": "success", // 状态描述
  "data": {             // 响应数据
    "list": [],         // 数据列表（分页时）
    "total": 100,       // 总条数（分页时）
    "page": 1,          // 当前页码（分页时）
    "pageSize": 10      // 每页条数（分页时）
  }
}
```

### 1.5 状态码规范
- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 二、接口设计规范

### 2.1 URL 命名规范
- 使用小写字母、数字、连字符
- 使用名词复数形式表示资源集合
- 使用名词单数形式表示具体资源
- 避免使用动词，除非是特殊操作

示例：
```
GET    /api/v1/companies        # 获取公司列表
GET    /api/v1/companies/{id}   # 获取单个公司
POST   /api/v1/companies        # 创建公司
PUT    /api/v1/companies/{id}   # 更新公司
DELETE /api/v1/companies/{id}   # 删除公司
```

### 2.2 请求参数规范

1. **Query 参数**
   - 用于过滤和分页
   - 参数名使用 camelCase
   - 示例：`/companies?pageSize=10&page=1&keyword=test`

2. **Path 参数**
   - 用于标识具体资源
   - 参数名使用小写字母
   - 示例：`/companies/{id}/channels`

3. **Body 参数**
   - 使用 JSON 格式
   - 字段名使用 camelCase
   - 必须指定 Content-Type: application/json

### 2.3 响应规范

1. **成功响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "公司名称",
    "createTime": "2024-01-16T10:30:00Z"
  }
}
```

2. **错误响应**
```json
{
  "code": 40001,
  "message": "参数错误",
  "data": {
    "field": "name",
    "reason": "名称不能为空"
  }
}
```

3. **分页响应**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [],           // 数据列表
    "total": 100,         // 总条数
    "page": 1,           // 当前页码
    "pageSize": 10       // 每页条数
  }
}
```

## 三、安全规范

### 3.1 认证安全
- Token 有效期控制
- 敏感操作需要二次验证
- 登录尝试次数限制
- 定期刷新 Token

### 3.2 数据安全
- 敏感数据传输必须加密
- 响应中敏感信息脱敏
- SQL 注入防护
- XSS 防护

### 3.3 访问控制
- 基于角色的权限控制（RBAC）
- 操作日志记录
- IP 白名单控制
- 频率限制

## 四、性能规范

### 4.1 响应时间
- API 平均响应时间 < 200ms
- 99% 请求响应时间 < 1s
- 超时时间设置为 10s

### 4.2 并发处理
- 合理使用连接池
- 大量数据分页处理
- 添加缓存机制
- 异步处理耗时操作

### 4.3 数据优化
- 响应数据精简
- 合理使用索引
- 避免大事务
- 结果集限制

## 五、文档规范

### 5.1 接口文档
- 使用 Markdown 格式
- 详细的接口说明
- 完整的请求/响应示例
- 错误码说明

### 5.2 文档结构
```
/doc/api/
├── api-standard.md     # API设计标准
├── request.md          # 请求工具规范
├── error-codes.md      # 错误码定义
└── changelog.md        # 更新日志
```

## 六、测试规范

### 6.1 测试覆盖
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要流程
- 性能测试达标
- 安全测试通过

### 6.2 测试用例
- 正常流程测试
- 异常流程测试
- 边界条件测试
- 并发测试

## 七、维护规范

### 7.1 版本管理
- 遵循语义化版本
- 及时更新文档
- 保持向下兼容
- 版本更新计划

### 7.2 监控告警
- 接口可用性监控
- 性能指标监控
- 错误日志监控
- 业务指标监控

## 八、开发流程

### 8.1 接口开发流程
1. 需求分析
2. 接口设计
3. 文档编写
4. 接口实现
5. 测试验证
6. 代码审查
7. 部署上线
8. 监控运维

### 8.2 变更流程
1. 提出变更申请
2. 评估影响范围
3. 制定变更方案
4. 通知相关方
5. 实施变更
6. 验证确认
7. 更新文档

## 九、前后端交互规范

### 9.1 Loading 状态处理
1. **全局 Loading**
   - 页面初始化加载
   - 路由切换加载
   - 全局操作加载

2. **局部 Loading**
   - 表格数据加载
   - 表单提交加载
   - 按钮点击加载

### 9.2 错误处理
1. **全局错误**
   - 网络错误
   - 401 未授权
   - 403 无权限
   - 500 服务器错误

2. **业务错误**
   - 表单验证错误
   - 业务规则错误
   - 数据一致性错误

### 9.3 静默请求
1. **使用场景**
   - WebSocket 心跳检测
   - 后台数据轮询
   - Token 刷新请求
   - 不需要打断用户操作的请求

2. **配置方式**
   ```typescript
   // 静默请求示例
   const res = await request.get('/api/data', {
     silent: true  // 不触发登录跳转
   });
   ```

### 9.4 数据缓存
1. **缓存策略**
   - 列表数据缓存
   - 字典数据缓存
   - 用户信息缓存

2. **缓存更新**
   - 定时更新
   - 手动刷新
   - 数据变更时更新

## 十、错误码规范

### 10.1 系统级错误码
```typescript
enum SystemErrorCode {
  SUCCESS = 200,                    // 成功
  BAD_REQUEST = 400,               // 请求参数错误
  UNAUTHORIZED = 401,              // 未授权
  FORBIDDEN = 403,                 // 权限不足
  NOT_FOUND = 404,                 // 资源不存在
  METHOD_NOT_ALLOWED = 405,        // 方法不允许
  TIMEOUT = 408,                   // 请求超时
  CONFLICT = 409,                  // 资源冲突
  GONE = 410,                      // 资源不可用
  PAYLOAD_TOO_LARGE = 413,         // 请求体过大
  UNSUPPORTED_MEDIA_TYPE = 415,    // 媒体类型不支持
  TOO_MANY_REQUESTS = 429,         // 请求过于频繁
  INTERNAL_ERROR = 500,            // 服务器内部错误
  SERVICE_UNAVAILABLE = 503,       // 服务不可用
  GATEWAY_TIMEOUT = 504            // 网关超时
}
```

### 10.2 业务错误码
```typescript
enum BusinessErrorCode {
  // 用户相关：1000-1999
  USER_NOT_FOUND = 1000,           // 用户不存在
  USER_ALREADY_EXISTS = 1001,      // 用户已存在
  PASSWORD_ERROR = 1002,           // 密码错误
  ACCOUNT_LOCKED = 1003,           // 账号被锁定
  
  // 权限相关：2000-2999
  NO_PERMISSION = 2000,            // 没有权限
  TOKEN_EXPIRED = 2001,            // 令牌过期
  TOKEN_INVALID = 2002,            // 令牌无效
  
  // 产品相关：3000-3999
  PRODUCT_NOT_FOUND = 3000,        // 产品不存在
  PRODUCT_OFFLINE = 3001,          // 产品已下线
  STOCK_NOT_ENOUGH = 3002,         // 库存不足
  
  // 订单相关：4000-4999
  ORDER_NOT_FOUND = 4000,          // 订单不存在
  ORDER_ALREADY_PAID = 4001,       // 订单已支付
  ORDER_EXPIRED = 4002,            // 订单已过期
  
  // 支付相关：5000-5999
  PAYMENT_FAILED = 5000,           // 支付失败
  BALANCE_NOT_ENOUGH = 5001,       // 余额不足
  PAYMENT_TIMEOUT = 5002,          // 支付超时
  
  // 文件相关：6000-6999
  FILE_TOO_LARGE = 6000,           // 文件过大
  FILE_TYPE_NOT_ALLOWED = 6001,    // 文件类型不允许
  UPLOAD_FAILED = 6002,            // 上传失败
  
  // 验证码相关：7000-7999
  CAPTCHA_ERROR = 7000,            // 验证码错误
  CAPTCHA_EXPIRED = 7001,          // 验证码过期
  SEND_TOO_FREQUENTLY = 7002       // 发送过于频繁
}
```

### 10.3 错误响应格式
```typescript
interface ErrorResponse {
  code: number;                    // 错误码
  message: string;                 // 错误信息
  data?: any;                      // 错误详情
  timestamp: string;               // 时间戳
  requestId: string;               // 请求ID
  path: string;                    // 请求路径
  details?: {                      // 详细错误信息
    field?: string;               // 错误字段
    value?: any;                  // 错误值
    reason?: string;              // 错误原因
  }[];
}

// 示例
{
  "code": 1002,
  "message": "密码错误",
  "timestamp": "2024-01-16T10:30:00Z",
  "requestId": "req-123456",
  "path": "/api/v1/auth/login",
  "details": [
    {
      "field": "password",
      "reason": "密码至少包含一个大写字母"
    }
  ]
}
```

## 十一、接口性能规范

### 11.1 响应时间要求
1. **接口响应时间**
   - P95 < 200ms
   - P99 < 1s
   - 超时设置 3s

2. **批量接口要求**
   - 单次请求数据量 < 1000条
   - 分页大小 <= 100
   - 导出数据量 < 10000条

3. **并发处理**
   - 限流配置
   - 降级策略
   - 熔断机制

### 11.2 数据优化建议
1. **请求优化**
   - 合并请求
   - 请求缓存
   - 按需加载

2. **响应优化**
   - 数据压缩
   - 响应裁剪
   - 增量更新

3. **查询优化**
   - 索引优化
   - 分页查询
   - 字段过滤

## 十二、接口测试规范

### 12.1 单元测试
1. **测试覆盖要求**
   - 核心业务逻辑覆盖率 > 80%
   - 工具类覆盖率 > 90%
   - 异常分支覆盖率 > 70%

2. **测试用例设计**
   ```typescript
   describe('用户登录', () => {
     it('正常登录', async () => {
       // 准备测试数据
       const loginData = {
         username: 'test',
         password: 'Test123'
       };
       
       // 执行测试
       const response = await userService.login(loginData);
       
       // 验证结果
       expect(response.code).toBe(200);
       expect(response.data.token).toBeDefined();
     });
     
     it('密码错误', async () => {
       // 异常测试用例
     });
   });
   ```

### 12.2 接口测试
1. **测试环境要求**
   - 开发环境
   - 测试环境
   - 预发环境
   - 生产环境

2. **测试项目**
   - 功能测试
   - 性能测试
   - 安全测试
   - 兼容性测试

3. **自动化测试**
   ```javascript
   // 使用 Postman/Newman 自动化测试示例
   pm.test("响应状态码检查", () => {
     pm.response.to.have.status(200);
   });
   
   pm.test("响应格式检查", () => {
     const response = pm.response.json();
     pm.expect(response).to.have.property('code');
     pm.expect(response).to.have.property('data');
   });
   ```

## 十三、监控告警规范

### 13.1 性能监控
1. **监控指标**
   - 响应时间
   - 并发数
   - 错误率
   - QPS/TPS

2. **监控维度**
   - 接口维度
   - 服务维度
   - 实例维度
   - 区域维度

3. **告警规则**
   ```yaml
   # 告警配置示例
   rules:
     - name: api_response_time
       threshold: 1000  # 毫秒
       duration: 5m
       severity: warning
     
     - name: api_error_rate
       threshold: 1%
       duration: 5m
       severity: critical
   ```

### 13.2 业务监控
1. **核心指标**
   - 业务成功率
   - 业务量监控
   - 用户行为
   - 转化率

2. **异常监控**
   - 业务异常
   - 系统异常
   - 依赖异常
   - 安全异常

3. **监控报表**
   - 实时监控
   - 定时报表
   - 异常分析
   - 趋势分析

## 十四、文档维护规范

### 14.1 文档结构
```
/api-docs/
├── overview/
│   ├── introduction.md           # 项目介绍
│   ├── architecture.md          # 架构设计
│   └── changelog.md            # 更新日志
│
├── guides/
│   ├── getting-started.md      # 快速开始
│   ├── authentication.md       # 认证授权
│   └── best-practices.md      # 最佳实践
│
├── api/
│   ├── user/                  # 用户相关接口
│   ├── product/              # 产品相关接口
│   └── order/               # 订单相关接口
│
└── schemas/                 # 数据结构定义
    ├── user.schema.json
    ├── product.schema.json
    └── order.schema.json
```

### 14.2 文档更新规范
1. **更新时机**
   - 接口变更时
   - 版本发布时
   - Bug修复时
   - 性能优化时

2. **更新内容**
   - 接口变更说明
   - 兼容性说明
   - 示例代码更新
   - 注意事项更新

3. **版本控制**
   ```markdown
   ## 更新历史
   
   ### v1.1.0 (2024-01-16)
   - 新增用户注册接口
   - 优化登录流程
   - 修复token刷新问题
   
   ### v1.0.1 (2024-01-15)
   - 修复已知bug
   - 更新文档示例
   ```

## 十五、开发工具规范

### 15.1 接口调试工具
1. **Postman 使用规范**
   - 环境配置
   - 集合组织
   - 变量管理
   - 测试脚本

2. **Swagger 使用规范**
   - 接口文档
   - 在线调试
   - 代码生成
   - Mock服务

3. **Charles/Fiddler 使用规范**
   - 请求拦截
   - 响应修改
   - 断点调试
   - 性能分析

### 15.2 开发辅助工具
1. **代码生成器**
   - 接口代码
   - 测试用例
   - 文档生成
   - 客户端代码

2. **Mock 服务**
   ```javascript
   // Mock 数据示例
   Mock.mock('/api/v1/users', 'get', {
     'code': 200,
     'data|10': [{
       'id|+1': 1,
       'name': '@name',
       'email': '@email',
       'created_at': '@datetime'
     }]
   });
   ```

3. **调试工具**
   - Chrome DevTools
   - VS Code Debugger
   - 接口测试工具
   - 性能分析工具