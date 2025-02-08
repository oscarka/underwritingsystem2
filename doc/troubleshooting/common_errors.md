# 常见错误和解决方案

## 一、前端错误

### 1.1 启动错误
1. **找不到 package.json**
   ```
   npm error code ENOENT
   npm error syscall open
   npm error path /Users/xxx/package.json
   ```
   解决方案：
   - 确认当前目录是否正确
   - 进入正确的项目目录（app/frontend）
   - 检查 package.json 文件是否存在

2. **端口被占用**
   ```
   Error: listen EADDRINUSE: address already in use :::3002
   ```
   解决方案：
   - 使用 `lsof -i :3002` 查找占用进程
   - 使用 `kill -9 <PID>` 结束进程
   - 修改 vite.config.ts 中的端口号

### 1.2 运行时错误
1. **Cannot read properties of undefined**
   ```
   Uncaught (in promise) TypeError: Cannot read properties of undefined (reading 'length')
   ```
   解决方案：
   - 检查数据初始化
   - 添加空值判断
   - 使用可选链操作符

2. **Token 相关错误**
   ```
   401 Unauthorized
   ```
   解决方案：
   - 检查 Token 是否过期
   - 确认 Token 格式是否正确
   - 尝试重新登录

## 二、后端错误

### 2.1 数据库错误
1. **连接失败**
   ```
   OperationalError: (sqlite3.OperationalError) unable to open database file
   ```
   解决方案：
   - 检查数据库文件权限
   - 确认数据库文件路径
   - 检查磁盘空间

2. **迁移错误**
   ```
   Error: Target database is not up to date
   ```
   解决方案：
   - 执行 `flask db upgrade`
   - 检查迁移文件是否完整
   - 确认数据库版本

### 2.2 API 错误
1. **参数验证失败**
   ```
   {
     "code": 40001,
     "message": "参数验证失败",
     "data": {
       "field": "name",
       "reason": "名称不能为空"
     }
   }
   ```
   解决方案：
   - 检查请求参数
   - 参考API文档
   - 添加参数验证

2. **权限错误**
   ```
   {
     "code": 40300,
     "message": "无操作权限"
   }
   ```
   解决方案：
   - 检查用户角色
   - 确认权限配置
   - 联系管理员

## 三、部署错误

### 3.1 环境配置
1. **Python 版本不匹配**
   ```
   ModuleNotFoundError: No module named 'typing_extensions'
   ```
   解决方案：
   - 使用 Python 3.8+
   - 更新 pip
   - 重新安装依赖

2. **Node 版本不匹配**
   ```
   Error: The engine "node" is incompatible with this module
   ```
   解决方案：
   - 使用 Node 16+
   - 更新 npm
   - 清除 node_modules

### 3.2 构建错误
1. **前端构建失败**
   ```
   Build failed with 2 errors:
   error: Failed to resolve import
   ```
   解决方案：
   - 检查依赖版本
   - 清理缓存
   - 重新安装依赖

2. **后端构建失败**
   ```
   ImportError: cannot import name 'xyz' from 'package'
   ```
   解决方案：
   - 更新依赖版本
   - 检查导入路径
   - 重建虚拟环境

## 四、性能问题

### 4.1 前端性能
1. **页面加载慢**
   - 优化资源加载
   - 启用懒加载
   - 使用缓存

2. **操作响应慢**
   - 优化数据处理
   - 减少不必要的渲染
   - 使用虚拟列表

### 4.2 后端性能
1. **API响应慢**
   - 优化数据库查询
   - 添加缓存
   - 使用异步处理

2. **内存占用高**
   - 优化数据结构
   - 及时释放资源
   - 控制并发数量

## 五、问题排查流程

1. **收集信息**
   - 错误信息
   - 操作步骤
   - 环境信息

2. **定位问题**
   - 查看日志
   - 复现问题
   - 分析堆栈

3. **解决问题**
   - 制定方案
   - 验证修复
   - 更新文档

4. **预防措施**
   - 完善监控
   - 优化流程
   - 更新测试用例 