#!/bin/bash
set -e

echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment variables:"
echo "DATABASE_URL=$DATABASE_URL"
echo "PORT=$PORT"
echo "FLASK_APP=$FLASK_APP"
echo "FLASK_DEBUG=$FLASK_DEBUG"

export PGPASSWORD=your-password

echo "Waiting for database..."
while ! pg_isready -h db -p 5432 -U postgres; do
    sleep 1
done
echo "Database is ready!"

echo "Creating database if not exists..."
psql -h db -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'underwriting'" | grep -q 1 || psql -h db -U postgres -c "CREATE DATABASE underwriting"

echo "Checking database tables before migration..."
psql -h db -U postgres -d underwriting -c "\dt"

echo "Running database migrations..."
echo "Testing database connection..."
python << END
import sys
from sqlalchemy import create_engine
try:
    engine = create_engine('postgresql://postgres:your-password@db:5432/underwriting')
    connection = engine.connect()
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print("Database connection failed!")
    print(f"Error: {str(e)}")
    sys.exit(1)
END

echo "Running migrations..."
export PYTHONPATH=/app

# 尝试修复多个head的问题
echo "Merging multiple heads..."
FLASK_APP=app flask db merge heads || {
    echo "Failed to merge heads, trying to upgrade to specific revision..."
    FLASK_APP=app flask db upgrade eb157058c420 || {
        echo "Failed to upgrade to eb157058c420, trying next revision..."
        FLASK_APP=app flask db upgrade 455d66280d20 || {
            echo "Migration failed with error code $?"
            echo "Migration history:"
            FLASK_APP=app flask db history
            echo "Current migration head:"
            FLASK_APP=app flask db current
            exit 1
        }
    }
}

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT app:app --log-level debug --capture-output --reload 