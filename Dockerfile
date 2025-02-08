# 前端构建阶段
FROM node:18 AS frontend-builder
WORKDIR /frontend
COPY app/frontend/package*.json ./
RUN npm install
COPY app/frontend .
RUN npm run build

# 后端构建阶段
FROM python:3.9-slim

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
    LOG_TO_STDOUT=true

# 创建必要的目录
RUN mkdir -p app/uploads app/static/admin logs && \
    chmod -R 777 app/uploads logs

# 暴露端口
EXPOSE $PORT

# 启动命令
CMD flask db upgrade && \
    gunicorn --bind "0.0.0.0:$PORT" --workers 1 --timeout 120 "app:create_app()" 