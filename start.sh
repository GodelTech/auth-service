#! /usr/bin/env sh

set -e

# Run migrations
echo "Migrations"
alembic upgrade head

echo "uvicorn src.main:app --host 0.0.0.0 --port 8000"
uvicorn src.main:app --host 0.0.0.0 --port 8000
