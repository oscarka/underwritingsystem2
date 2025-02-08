#!/bin/bash

echo "开始构建项目..."

# 安装后端依赖
echo "安装后端依赖..."
pip install -r requirements.txt

# 构建管理后台前端
echo "构建管理后台前端..."
cd app/frontend
npm install
npm run build

# 构建移动端应用
echo "构建移动端应用..."
cd ../../mobile-app
npm install
npm run build

# 移动构建结果到静态目录
echo "移动构建结果到静态目录..."
cd ..
mkdir -p app/static/admin
mkdir -p app/static/mobile
cp -r app/frontend/dist/* app/static/admin/
cp -r mobile-app/dist/* app/static/mobile/

echo "构建完成！"
