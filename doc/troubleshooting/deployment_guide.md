# 部署指南

## 一、环境要求

### 1.1 系统要求
- 操作系统：Linux/macOS/Windows
- CPU：2核以上
- 内存：4GB以上
- 磁盘：20GB以上

### 1.2 软件要求
- Python 3.8+
- Node.js 16+
- SQLite 3.x
- Git

## 二、开发环境部署

### 2.1 后端部署
1. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   ```bash
   flask db upgrade
   python init_db.py
   ```

4. **启动服务**
   ```bash
   python run.py
   ```

### 2.2 前端部署
1. **安装依赖**
   ```bash
   cd app/frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **构建生产版本**
   ```bash
   npm run build
   ```

## 三、生产环境部署

### 3.1 后端部署
1. **系统配置**
   ```bash
   # 创建应用目录
   mkdir -p /opt/app
   cd /opt/app
   
   # 克隆代码
   git clone <repository_url>
   
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **环境变量配置**
   ```bash
   # 创建环境变量文件
   cp .env.example .env
   
   # 编辑环境变量
   vim .env
   ```

3. **数据库配置**
   ```bash
   # 初始化数据库
   flask db upgrade
   
   # 导入初始数据
   python init_db.py
   ```

4. **服务配置**
   ```bash
   # 创建服务文件
   sudo vim /etc/systemd/system/app.service
   
   # 服务文件内容
   [Unit]
   Description=Flask App
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/opt/app
   Environment="PATH=/opt/app/venv/bin"
   ExecStart=/opt/app/venv/bin/python run.py
   
   [Install]
   WantedBy=multi-user.target
   ```

### 3.2 前端部署
1. **构建**
   ```bash
   # 进入前端目录
   cd app/frontend
   
   # 安装依赖
   npm install
   
   # 构建
   npm run build
   ```

2. **Nginx配置**
   ```nginx
   server {
       listen 80;
       server_name example.com;
   
       # 前端文件
       location / {
           root /opt/app/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
   
       # API代理
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 四、部署检查清单

### 4.1 环境检查
- [ ] Python版本正确
- [ ] Node.js版本正确
- [ ] 数据库可用
- [ ] 系统资源充足

### 4.2 配置检查
- [ ] 环境变量配置正确
- [ ] 数据库连接正确
- [ ] 日志路径可写
- [ ] 文件权限正确

### 4.3 功能检查
- [ ] 后端API可访问
- [ ] 前端页面可访问
- [ ] 登录功能正常
- [ ] 数据操作正常

### 4.4 性能检查
- [ ] 响应时间正常
- [ ] CPU使用率正常
- [ ] 内存使用正常
- [ ] 磁盘使用正常

## 五、常见问题

### 5.1 部署问题
1. **端口被占用**
   ```
   Error: listen EADDRINUSE
   ```
   解决方案：
   - 检查端口占用
   - 修改配置端口
   - 关闭占用进程

2. **权限不足**
   ```
   Permission denied
   ```
   解决方案：
   - 检查文件权限
   - 修改目录所有者
   - 添加执行权限

### 5.2 运行问题
1. **服务无法启动**
   ```
   Failed to start service
   ```
   解决方案：
   - 检查日志文件
   - 验证配置文件
   - 检查依赖安装

2. **数据库连接失败**
   ```
   Database connection failed
   ```
   解决方案：
   - 检查连接字符串
   - 验证数据库状态
   - 检查网络连接

## 六、维护指南

### 6.1 日常维护
1. **日志管理**
   ```bash
   # 查看日志
   tail -f /var/log/app/app.log
   
   # 清理旧日志
   find /var/log/app -name "*.log" -mtime +30 -delete
   ```

2. **备份管理**
   ```bash
   # 备份数据库
   ./backup.sh
   
   # 备份配置
   cp -r /opt/app/config /opt/backup/
   ```

### 6.2 更新维护
1. **代码更新**
   ```bash
   # 拉取最新代码
   git pull
   
   # 更新依赖
   pip install -r requirements.txt
   npm install
   
   # 重启服务
   sudo systemctl restart app
   ```

2. **数据库更新**
   ```bash
   # 执行迁移
   flask db upgrade
   
   # 验证数据
   python check_db.py
   ```

### 6.3 监控告警
1. **系统监控**
   - CPU使用率
   - 内存使用率
   - 磁盘使用率
   - 网络流量

2. **应用监控**
   - 接口响应时间
   - 错误率
   - 并发数
   - 业务指标 