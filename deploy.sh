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
EOL

# 4. 更新 Procfile
echo "更新 Procfile..."
echo "web: gunicorn 'app:create_app()' --bind 0.0.0.0:\$PORT" > Procfile

echo "部署准备完成！"
echo "请检查文件并提交到 GitHub。" 