#!/bin/bash

echo "开始部署准备..."

# 1. 清理不需要的文件
echo "清理文件..."
rm -f test_*.py
rm -f migrations.py schema.sql

# 2. 创建必要的目录
echo "创建必要的目录..."
mkdir -p app/static/admin
mkdir -p app/static/mobile
mkdir -p logs

# 3. 更新 requirements.txt
echo "更新 requirements.txt..."
cat > requirements.txt << EOL
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-Migrate==2.7.0
psycopg2-binary==2.9.1
python-dotenv==0.19.0
gunicorn==20.1.0
Flask-Login==0.5.0
Flask-WTF==0.15.1
Werkzeug==2.0.1
Flask-CORS==4.0.0
PyJWT==2.1.0
psutil==5.9.0
EOL

# 4. 更新 Procfile
echo "更新 Procfile..."
echo "web: gunicorn 'app:create_app()' --bind 0.0.0.0:\$PORT" > Procfile

echo "部署准备完成！"

# 5. 运行构建脚本 - 只构建管理后台
echo "构建管理后台前端..."
cd app/frontend
npm install
npm run build

# 6. 移动构建结果到静态目录
echo "移动构建结果到静态目录..."
cd ../..
cp -r app/frontend/dist/* app/static/admin/

# 7. 启动应用
echo "启动应用..."
nohup gunicorn 'app:create_app()' --bind 0.0.0.0:5001 --reload --timeout 120 --log-level debug --error-logfile logs/error.log --access-logfile logs/access.log > logs/gunicorn.log 2>&1 &

# 8. 等待应用启动
echo "等待应用启动..."
sleep 5
if curl -s http://localhost:5001/ > /dev/null; then
    echo "应用启动成功!"
else
    echo "应用启动失败,请检查日志文件 logs/gunicorn.log"
    tail -n 50 logs/gunicorn.log
    exit 1
fi 