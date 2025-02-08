# 前端构建阶段
FROM node:18 AS frontend-builder
WORKDIR /frontend
COPY app/frontend/package*.json ./
RUN npm install
COPY app/frontend .
RUN npm run build

# 后端构建阶段
FROM python:3.9-slim

# 构建参数
ARG VERSION=dev
ARG BUILD_DATE=unknown

# 镜像标签
LABEL maintainer="Your Name <your.email@example.com>" \
    version=${VERSION} \
    build-date=${BUILD_DATE} \
    description="核保系统应用镜像" \
    org.opencontainers.image.source="https://github.com/oscarka/underwritingsystem2"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .
# 复制前端构建结果
COPY --from=frontend-builder /frontend/dist app/static/admin/

# 基础环境变量
ENV FLASK_APP=app \
    FLASK_DEBUG=0 \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    LOG_TO_STDOUT=true \
    PORT=5000

# 数据库连接基础配置
ENV PGHOST=${PGHOST} \
    PGPORT=${PGPORT} \
    PGUSER=${PGUSER} \
    PGPASSWORD=${PGPASSWORD} \
    PGDATABASE=${PGDATABASE} \
    DATABASE_URL=${DATABASE_URL}

# 数据库连接池配置
ENV DB_POOL_SIZE=5 \
    DB_MAX_OVERFLOW=10 \
    DB_POOL_TIMEOUT=30 \
    DB_POOL_RECYCLE=1800 \
    DB_POOL_PRE_PING=true \
    DB_ECHO=false

# 数据库连接参数
ENV DB_CONNECT_TIMEOUT=10 \
    DB_KEEPALIVES=1 \
    DB_KEEPALIVES_IDLE=30 \
    DB_KEEPALIVES_INTERVAL=10 \
    DB_KEEPALIVES_COUNT=5 \
    DB_CLIENT_ENCODING=utf8 \
    DB_SSL_MODE=require \
    DB_APPLICATION_NAME=underwriting_system

# 创建必要的目录
RUN mkdir -p app/uploads app/static/admin logs && \
    chmod -R 777 app/uploads logs

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE 5000

# 启动命令
CMD flask db upgrade && \
    gunicorn --bind "0.0.0.0:$PORT" --workers 1 --timeout 120 "app:create_app()" 