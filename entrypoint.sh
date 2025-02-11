#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment variables:"
echo "DATABASE_URL=$DATABASE_URL"
echo "PORT=$PORT"
echo "FLASK_APP=$FLASK_APP"
echo "FLASK_DEBUG=$FLASK_DEBUG"

# 从 DATABASE_URL 解析连接信息
if [[ $DATABASE_URL =~ ^postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)$ ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASS="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
    export PGPASSWORD=$DB_PASS
else
    echo "无法解析 DATABASE_URL"
    exit 1
fi

echo "Waiting for database..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
    sleep 1
done
echo "Database is ready!"

echo "Testing database connection..."
python << END
import sys
from sqlalchemy import create_engine
try:
    engine = create_engine('${DATABASE_URL}')
    connection = engine.connect()
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print("Database connection failed!")
    print(f"Error: {str(e)}")
    sys.exit(1)
END

echo "Initializing database schema and default data..."
export PYTHONPATH=/app
python init_db.py

echo "Starting Gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug --capture-output --reload 