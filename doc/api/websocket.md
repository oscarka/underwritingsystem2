# WebSocket 接口规范

## 一、连接规范

### 1.1 连接地址
```typescript
const wsUrl = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/api/v1/ws`;
```

### 1.2 连接参数
```typescript
interface WsConnectParams {
  token: string;           // 认证token
  clientId: string;        // 客户端ID
  protocol: string;        // 协议版本
}
```

### 1.3 心跳机制
```typescript
const HEARTBEAT_INTERVAL = 30000;  // 心跳间隔：30秒
const HEARTBEAT_TIMEOUT = 5000;    // 心跳超时：5秒

// 心跳消息格式
interface HeartbeatMessage {
  type: 'heartbeat';
  timestamp: number;
}
```

## 二、消息格式

### 2.1 基础消息格式
```typescript
interface WsMessage<T = any> {
  type: string;           // 消息类型
  data: T;               // 消息数据
  timestamp: number;     // 时间戳
  messageId: string;     // 消息ID
  sequence?: number;     // 消息序号（用于消息排序）
}
```

### 2.2 消息类型
```typescript
enum MessageType {
  // 系统消息
  CONNECT = 'connect',           // 连接成功
  DISCONNECT = 'disconnect',     // 断开连接
  ERROR = 'error',              // 错误消息
  HEARTBEAT = 'heartbeat',      // 心跳消息
  
  // 业务消息
  NOTIFICATION = 'notification', // 通知消息
  STATUS_CHANGE = 'status',     // 状态变更
  DATA_UPDATE = 'data',         // 数据更新
  
  // 控制消息
  SUBSCRIBE = 'subscribe',      // 订阅主题
  UNSUBSCRIBE = 'unsubscribe', // 取消订阅
  ACK = 'ack'                  // 确认消息
}
```

## 三、消息示例

### 3.1 连接消息
```typescript
// 连接成功
{
  type: 'connect',
  data: {
    clientId: 'client_123',
    serverTime: 1643673600000
  },
  timestamp: 1643673600000,
  messageId: 'msg_123'
}

// 连接错误
{
  type: 'error',
  data: {
    code: 40100,
    message: 'Token invalid'
  },
  timestamp: 1643673600000,
  messageId: 'msg_124'
}
```

### 3.2 业务消息
```typescript
// 通知消息
{
  type: 'notification',
  data: {
    title: '新订单提醒',
    content: '收到新的订单：ORDER_123',
    level: 'info'
  },
  timestamp: 1643673600000,
  messageId: 'msg_125'
}

// 状态变更
{
  type: 'status',
  data: {
    entityType: 'order',
    entityId: 'ORDER_123',
    status: 'completed'
  },
  timestamp: 1643673600000,
  messageId: 'msg_126'
}
```

## 四、错误处理

### 4.1 错误码定义
```typescript
enum WsErrorCode {
  // 连接错误 (1000-1999)
  CONNECT_ERROR = 1000,        // 连接失败
  AUTH_FAILED = 1001,         // 认证失败
  INVALID_PROTOCOL = 1002,    // 协议错误
  
  // 消息错误 (2000-2999)
  INVALID_MESSAGE = 2000,     // 消息格式错误
  MESSAGE_TOO_LARGE = 2001,   // 消息过大
  RATE_LIMIT = 2002,         // 消息频率限制
  
  // 业务错误 (3000-3999)
  SUBSCRIBE_FAILED = 3000,    // 订阅失败
  PERMISSION_DENIED = 3001,   // 权限不足
  INVALID_OPERATION = 3002    // 非法操作
}
```

### 4.2 错误消息格式
```typescript
interface WsError {
  code: number;        // 错误码
  message: string;     // 错误信息
  details?: any;       // 错误详情
}
```

## 五、客户端实现

### 5.1 连接管理
```typescript
class WsClient {
  private ws: WebSocket;
  private reconnectCount: number = 0;
  private heartbeatTimer?: number;
  
  constructor(private config: WsConfig) {
    this.connect();
  }
  
  private connect() {
    this.ws = new WebSocket(this.getWsUrl());
    this.setupEventHandlers();
    this.startHeartbeat();
  }
  
  private setupEventHandlers() {
    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
  }
  
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.sendHeartbeat();
    }, HEARTBEAT_INTERVAL);
  }
}
```

### 5.2 消息处理
```typescript
class WsClient {
  private messageHandlers: Map<string, Function> = new Map();
  
  public on(type: string, handler: Function) {
    this.messageHandlers.set(type, handler);
  }
  
  private handleMessage(event: MessageEvent) {
    const message = JSON.parse(event.data);
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message.data);
    }
  }
  
  public send(type: string, data: any) {
    const message: WsMessage = {
      type,
      data,
      timestamp: Date.now(),
      messageId: this.generateMessageId()
    };
    this.ws.send(JSON.stringify(message));
  }
}
```

## 六、使用示例

### 6.1 基础用法
```typescript
// 创建WebSocket客户端
const wsClient = new WsClient({
  token: 'your_token',
  clientId: 'client_123',
  protocol: '1.0'
});

// 监听消息
wsClient.on('notification', (data) => {
  console.log('收到通知:', data);
});

wsClient.on('status', (data) => {
  console.log('状态变更:', data);
});

// 发送消息
wsClient.send('subscribe', {
  topic: 'order_updates',
  params: { orderId: 'ORDER_123' }
});
```

### 6.2 错误处理
```typescript
wsClient.on('error', (error: WsError) => {
  switch (error.code) {
    case WsErrorCode.AUTH_FAILED:
      // 重新登录
      break;
    case WsErrorCode.RATE_LIMIT:
      // 等待一段时间后重试
      break;
    default:
      console.error('WebSocket错误:', error);
  }
});
```

## 七、最佳实践

### 7.1 连接管理
1. 自动重连
   - 断线后自动重连
   - 重连间隔递增
   - 最大重连次数限制

2. 心跳检测
   - 定时发送心跳
   - 检测心跳超时
   - 超时后重连

### 7.2 消息处理
1. 消息去重
   - 使用消息ID去重
   - 记录已处理消息
   - 定期清理消息记录

2. 消息确认
   - 重要消息需确认
   - 超时重发机制
   - 确认消息幂等性

### 7.3 性能优化
1. 连接复用
   - 单个连接处理多个订阅
   - 避免频繁重连
   - 合理控制并发

2. 消息压缩
   - 大消息使用压缩
   - 批量消息合并
   - 减少传输数据量 