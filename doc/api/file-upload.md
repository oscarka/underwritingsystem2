# 文件上传规范

## 一、基本要求

### 1.1 支持的文件类型
```typescript
const ALLOWED_FILE_TYPES = {
  // 图片
  IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
  // 文档
  DOCUMENT: ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
  // 压缩包
  ARCHIVE: ['.zip', '.rar', '.7z'],
  // 其他
  OTHER: ['.txt', '.json', '.xml']
};
```

### 1.2 文件大小限制
```typescript
const FILE_SIZE_LIMITS = {
  IMAGE: 5 * 1024 * 1024,      // 5MB
  DOCUMENT: 20 * 1024 * 1024,  // 20MB
  ARCHIVE: 50 * 1024 * 1024,   // 50MB
  OTHER: 10 * 1024 * 1024      // 10MB
};
```

### 1.3 文件命名规范
```typescript
interface FileNaming {
  prefix: string;        // 业务前缀
  timestamp: number;     // 时间戳
  random: string;        // 随机字符串
  extension: string;     // 文件扩展名
}

// 示例：company_logo_1643673600000_abc123.jpg
```

## 二、上传接口

### 2.1 单文件上传
```typescript
POST /api/v1/files/upload

// 请求头
Content-Type: multipart/form-data

// 请求参数
{
  file: File,                 // 文件对象
  type: string,              // 文件类型
  module: string,            // 业务模块
  description?: string       // 文件描述
}

// 响应格式
{
  code: number,              // 状态码
  data: {
    fileId: string,          // 文件ID
    fileName: string,        // 文件名
    fileUrl: string,         // 文件URL
    fileSize: number,        // 文件大小
    mimeType: string,        // MIME类型
    uploadTime: number       // 上传时间
  },
  message: string            // 响应消息
}
```

### 2.2 多文件上传
```typescript
POST /api/v1/files/batch-upload

// 请求头
Content-Type: multipart/form-data

// 请求参数
{
  files: File[],            // 文件对象数组
  type: string,             // 文件类型
  module: string,           // 业务模块
  description?: string      // 文件描述
}

// 响应格式
{
  code: number,             // 状态码
  data: {
    successList: Array<{    // 上传成功的文件列表
      fileId: string,
      fileName: string,
      fileUrl: string,
      fileSize: number,
      mimeType: string,
      uploadTime: number
    }>,
    failList: Array<{       // 上传失败的文件列表
      fileName: string,
      error: string
    }>
  },
  message: string           // 响应消息
}
```

### 2.3 分片上传
```typescript
// 1. 初始化上传
POST /api/v1/files/multipart/init

// 请求参数
{
  fileName: string,         // 文件名
  fileSize: number,        // 文件大小
  chunkSize: number,       // 分片大小
  type: string,            // 文件类型
  module: string           // 业务模块
}

// 响应格式
{
  code: number,
  data: {
    uploadId: string,      // 上传ID
    chunkSize: number,     // 分片大小
    chunks: number         // 分片数量
  },
  message: string
}

// 2. 上传分片
POST /api/v1/files/multipart/upload

// 请求参数
{
  uploadId: string,        // 上传ID
  chunkIndex: number,      // 分片索引
  chunk: File             // 分片数据
}

// 响应格式
{
  code: number,
  data: {
    chunkIndex: number,    // 分片索引
    received: boolean      // 接收状态
  },
  message: string
}

// 3. 完成上传
POST /api/v1/files/multipart/complete

// 请求参数
{
  uploadId: string         // 上传ID
}

// 响应格式
{
  code: number,
  data: {
    fileId: string,
    fileName: string,
    fileUrl: string,
    fileSize: number,
    mimeType: string,
    uploadTime: number
  },
  message: string
}
```

## 三、客户端实现

### 3.1 文件校验
```typescript
class FileValidator {
  // 校验文件类型
  static validateFileType(file: File, allowedTypes: string[]): boolean {
    const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0];
    return extension ? allowedTypes.includes(extension) : false;
  }
  
  // 校验文件大小
  static validateFileSize(file: File, maxSize: number): boolean {
    return file.size <= maxSize;
  }
  
  // 校验文件名
  static validateFileName(fileName: string): boolean {
    return /^[a-zA-Z0-9_\-\.]+$/.test(fileName);
  }
}
```

### 3.2 上传进度监控
```typescript
class UploadProgress {
  constructor(private onProgress: (progress: number) => void) {}
  
  createUploadRequest(url: string, formData: FormData): XMLHttpRequest {
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const progress = Math.round((event.loaded / event.total) * 100);
        this.onProgress(progress);
      }
    });
    
    return xhr;
  }
}
```

### 3.3 断点续传
```typescript
class ResumableUpload {
  private chunks: Blob[] = [];
  private uploadedChunks: Set<number> = new Set();
  
  async upload(file: File, chunkSize: number) {
    // 1. 分片
    this.chunks = this.createChunks(file, chunkSize);
    
    // 2. 获取上传进度
    const uploadedChunks = await this.getUploadedChunks();
    this.uploadedChunks = new Set(uploadedChunks);
    
    // 3. 上传未完成的分片
    for (let i = 0; i < this.chunks.length; i++) {
      if (!this.uploadedChunks.has(i)) {
        await this.uploadChunk(i);
      }
    }
    
    // 4. 完成上传
    return this.completeUpload();
  }
  
  private createChunks(file: File, chunkSize: number): Blob[] {
    const chunks: Blob[] = [];
    let start = 0;
    
    while (start < file.size) {
      chunks.push(file.slice(start, start + chunkSize));
      start += chunkSize;
    }
    
    return chunks;
  }
}
```

## 四、使用示例

### 4.1 基础上传
```typescript
// 单文件上传
async function uploadFile(file: File) {
  // 1. 校验文件
  if (!FileValidator.validateFileType(file, ALLOWED_FILE_TYPES.IMAGE)) {
    throw new Error('不支持的文件类型');
  }
  
  if (!FileValidator.validateFileSize(file, FILE_SIZE_LIMITS.IMAGE)) {
    throw new Error('文件大小超出限制');
  }
  
  // 2. 创建表单数据
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', 'IMAGE');
  formData.append('module', 'user-avatar');
  
  // 3. 发送请求
  const response = await fetch('/api/v1/files/upload', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}
```

### 4.2 带进度的上传
```typescript
function uploadWithProgress(file: File, onProgress: (progress: number) => void) {
  const progress = new UploadProgress(onProgress);
  const formData = new FormData();
  formData.append('file', file);
  
  const xhr = progress.createUploadRequest('/api/v1/files/upload', formData);
  
  return new Promise((resolve, reject) => {
    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.response));
      } else {
        reject(new Error('上传失败'));
      }
    };
    
    xhr.onerror = () => reject(new Error('网络错误'));
    xhr.send(formData);
  });
}
```

### 4.3 分片上传
```typescript
async function uploadLargeFile(file: File) {
  const uploader = new ResumableUpload();
  const chunkSize = 5 * 1024 * 1024; // 5MB per chunk
  
  try {
    const result = await uploader.upload(file, chunkSize);
    console.log('上传完成:', result);
  } catch (error) {
    console.error('上传失败:', error);
  }
}
```

## 五、最佳实践

### 5.1 安全性
1. 文件类型验证
   - 服务端验证文件Magic Number
   - 限制允许的文件类型
   - 防止文件类型伪造

2. 文件大小控制
   - 限制单文件大小
   - 限制总上传大小
   - 根据用户权限设置限制

3. 存储安全
   - 文件名随机化
   - 防止路径穿越
   - 权限访问控制

### 5.2 性能优化
1. 上传优化
   - 启用分片上传
   - 支持断点续传
   - 并发上传控制

2. 存储优化
   - 图片压缩处理
   - 文件去重存储
   - CDN加速分发

3. 带宽优化
   - 限制上传速率
   - 队列处理请求
   - 错峰调度上传

### 5.3 用户体验
1. 进度反馈
   - 显示上传进度
   - 剩余时间估算
   - 上传速率显示

2. 容错处理
   - 断线自动重试
   - 错误友好提示
   - 取消上传支持

3. 预览功能
   - 图片即时预览
   - 文件基本信息
   - 上传前压缩 