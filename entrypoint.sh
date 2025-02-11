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

echo "Initializing database schema and default data..."
export PYTHONPATH=/app
python init_db.py

echo "Starting Gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --log-level debug --capture-output --reload 