# 前端架构设计文档

## 一、技术栈

- 框架: Vue 3 + TypeScript
- 构建工具: Vite
- 状态管理: Pinia
- 路由: Vue Router
- HTTP 请求: Axios
- UI 组件: 自研组件库
- 代码规范: ESLint + Prettier

## 二、目录结构

```
app/frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   │   ├── base/       # 基础组件
│   │   ├── feedback/   # 反馈组件
│   │   └── layout/     # 布局组件
│   ├── router/         # 路由配置
│   ├── stores/         # 状态管理
│   ├── styles/         # 全局样式
│   ├── types/          # 类型定义
│   ├── utils/          # 工具函数
│   └── views/          # 页面组件
├── public/             # 公共资源
└── docs/              # 文档
```

## 三、组件系统

### 1. 基础组件

所有基础组件都以 `Base` 为前缀，位于 `components/base` 目录：

- `BaseButton.vue`: 按钮组件
- `BaseInput.vue`: 输入框组件
- `BaseSelect.vue`: 选择框组件
- `BaseThemeSwitch.vue`: 主题切换组件

### 2. 反馈组件

位于 `components/feedback` 目录：

- `Toast.vue`: 消息提示组件
- `Loading.vue`: 加载状态组件

### 3. 布局组件

位于 `components/layout` 目录：

- `AppLayout.vue`: 应用布局组件
- `Container.vue`: 容器组件
- `Row.vue`: 行组件
- `Col.vue`: 列组件

## 四、主题系统

### 1. 变量定义

所有主题相关的 CSS 变量定义在 `styles/variables.css` 中：

```css
:root {
  /* 颜色 */
  --color-primary: #1890ff;
  --color-success: #52c41a;
  --color-warning: #faad14;
  --color-danger: #ff4d4f;
  
  /* 文字颜色 */
  --color-text-primary: rgba(0, 0, 0, 0.85);
  --color-text-secondary: rgba(0, 0, 0, 0.45);
  
  /* 背景颜色 */
  --color-bg-base: #f0f2f5;
  --color-bg-container: #ffffff;
  
  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* 字体大小 */
  --font-size-sm: 12px;
  --font-size-md: 14px;
  --font-size-lg: 16px;
  
  /* 动画 */
  --transition-normal: 0.3s;
}

/* 暗色主题 */
[data-theme="dark"] {
  --color-text-primary: rgba(255, 255, 255, 0.85);
  --color-bg-base: #141414;
  --color-bg-container: #1f1f1f;
}
```

### 2. 主题切换

主题切换通过修改 `<html>` 标签的 `data-theme` 属性实现。

## 五、接口规范

### 1. 请求响应类型

```typescript
// API 响应的基础结构
interface ApiResponse<T = any> {
  code: number      // 业务状态码
  data: T          // 响应数据
  message?: string // 提示信息
}

// 分页请求参数
interface PaginationQuery {
  page: number     // 当前页码
  pageSize: number // 每页条数
}

// 分页响应数据
interface PaginationResponse<T> {
  list: T[]       // 数据列表
  total: number   // 总条数
  page: number    // 当前页码
  pageSize: number // 每页条数
}
```

### 2. 请求工具

统一使用 `utils/request.ts` 中封装的方法发送请求：

```typescript
// GET 请求
get<T>(url: string, params?: any): Promise<T>

// POST 请求
post<T>(url: string, data?: any): Promise<T>

// PUT 请求
put<T>(url: string, data?: any): Promise<T>

// DELETE 请求
del<T>(url: string, params?: any): Promise<T>
```

### 3. 错误处理

- HTTP 错误统一在响应拦截器中处理
- 业务错误通过 `code` 判断，非 0 表示错误
- 错误信息统一使用 Toast 组件展示

### 4. 加载状态

- 请求发起时自动显示 Loading
- 请求结束时自动隐藏 Loading
- 支持多个请求的 Loading 状态管理

## 六、开发规范

### 1. 命名规范

- 文件名：
  - 组件文件使用 PascalCase（如 `BaseButton.vue`）
  - 其他文件使用 kebab-case（如 `api-types.ts`）

- 变量名：
  - 普通变量使用 camelCase
  - 常量使用 UPPER_SNAKE_CASE
  - 组件名使用 PascalCase

### 2. 样式规范

- 使用 scoped CSS
- 使用 CSS 变量实现主题
- 布局使用 flex 或 grid
- 响应式设计使用 media query

### 3. TypeScript 规范

- 所有变量和函数都要定义类型
- 使用 interface 而不是 type 定义对象类型
- 导出类型定义放在单独的 types 文件中

### 4. Git 规范

提交信息格式：
```
<type>(<scope>): <subject>

<body>

<footer>
```

type 类型：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

## 七、后端接口规范

### 1. 请求格式

- GET 请求：查询参数使用 URL 参数
- POST/PUT 请求：数据放在 body 中，格式为 JSON
- 请求头：Content-Type: application/json

### 2. 响应格式

```json
{
  "code": 0,        // 0 表示成功，非 0 表示错误
  "data": {},       // 响应数据
  "message": ""     // 错误信息
}
```

### 3. 错误码约定

- 0: 成功
- 400x: 客户端错误
- 500x: 服务端错误

### 4. 分页格式

请求：
```json
{
  "page": 1,
  "pageSize": 10,
  "keyword": "搜索关键词",
  "sort": {
    "field": "创建时间",
    "order": "desc"
  }
}
```

响应：
```json
{
  "code": 0,
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
``` 