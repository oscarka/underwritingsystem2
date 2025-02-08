#!/bin/bash

echo "开始重置系统..."

# 1. 停止运行中的应用（如果有）
if [ -f "app.pid" ]; then
    kill $(cat app.pid)
    rm app.pid
    echo "已停止运行中的应用"
fi

# 2. 删除现有数据库和迁移文件
rm -f app.db
rm -rf migrations/
echo "已删除现有数据库和迁移文件"

# 3. 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development

# 4. 运行重置脚本
python reset_system.py
if [ $? -ne 0 ]; then
    echo "重置系统失败"
    exit 1
fi

# 5. 初始化数据库迁移
flask db init
if [ $? -ne 0 ]; then
    echo "数据库初始化失败"
    exit 1
fi

# 6. 创建并应用迁移
flask db migrate -m "Initial migration"
flask db upgrade

echo "系统重置完成!"
echo "现在可以启动应用了: python run.py" 