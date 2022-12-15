#! /usr/bin/env sh

set -e

# Environment
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@postgres:5432/is_db"
export SECRET_KEY="postgres"

# Run migrations
echo "Migrations"
alembic upgrade heads

echo "Uvicorn running src.main:app --reload --host 0.0.0.0 --port 8000"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

