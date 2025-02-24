# 智能核保系统

一个基于 Flask 和 Vue.js 的智能核保系统，包含管理后台和移动端。

## 功能特点

- 管理后台
  - 产品配置
  - 核保规则管理
  - 用户管理
  - 订单管理

- 移动端
  - 用户信息采集
  - 疾病选择
  - 智能问答
  - 核保结果展示

## 技术栈

- 后端：Flask + SQLAlchemy + PostgreSQL
- 管理后台：Vue.js + Element Plus
- 移动端：Vue.js + Vant

## 部署说明

1. 克隆代码
```bash
git clone <repository-url>
cd <project-directory>
```

2. 安装依赖
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd app/frontend
npm install

# 移动端依赖
cd ../../mobile-app
npm install
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填写必要的配置信息
```

4. 构建前端
```bash
# 构建管理后台
cd app/frontend
npm run build

# 构建移动端
cd ../../mobile-app
npm run build
```

5. 启动服务
```bash
python run.py
```

## Railway 部署

1. Fork 本仓库
2. 在 Railway 中创建新项目
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway 会自动检测并使用 Procfile
6. 在 Railway 中设置必要的环境变量

## 环境变量说明

- `DATABASE_URL`: 数据库连接 URL
- `SECRET_KEY`: Flask 密钥
- `FLASK_ENV`: 运行环境 (development/production)
- `PORT`: 应用端口
- `ADMIN_USERNAME`: 管理员用户名
- `ADMIN_PASSWORD`: 管理员密码

## 开发说明

1. 启动开发服务器
```bash
# 后端
python run.py

# 管理后台
cd app/frontend
npm run dev

# 移动端
cd mobile-app
npm run dev
```

2. 访问地址
- 管理后台：http://localhost:3004；/admin
- 移动端：http://localhost:3001；/product/1/basic-info
- API：http://localhost:8000

## 许可证

MIT 
