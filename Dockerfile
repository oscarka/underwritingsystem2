# 前端构建阶段
FROM node:18-slim AS frontend-builder
WORKDIR /frontend
COPY app/frontend/package*.json ./
RUN npm install --legacy-peer-deps --no-audit --no-fund
COPY app/frontend .
RUN npm run build

# 移动端构建阶段
FROM node:18-slim AS mobile-builder
WORKDIR /mobile
COPY mobile-app/package*.json ./
RUN npm install --legacy-peer-deps --no-audit --no-fund
COPY mobile-app .
# 增加 NODE_OPTIONS 来增加内存限制
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# 后端构建阶段
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖（增加 DEBIAN_FRONTEND 以减少交互）
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .
# 复制前端构建结果
COPY --from=frontend-builder /frontend/dist app/static/admin/
# 复制移动端构建结果
COPY --from=mobile-builder /mobile/dist app/static/mobile/

# 复制并设置启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 基础环境变量
ENV FLASK_APP=app \
    FLASK_DEBUG=0 \
    PYTHONUNBUFFERED=1 \
    LOG_TO_STDOUT=true \
    PORT=5001

# 创建必要的目录并设置权限
RUN mkdir -p app/uploads app/static/admin app/static/mobile logs && \
    chmod -R 777 app/uploads logs app/static && \
    chown -R nobody:nogroup /app

# 切换到非root用户
USER nobody

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD ["/entrypoint.sh"] 