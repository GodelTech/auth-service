#! /usr/bin/env sh

set -e

# Environment
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/is_db"
export SECRET_KEY="postgres"

echo "Uvicorn running src.main:app --reload --host 0.0.0.0 --port 8000"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000