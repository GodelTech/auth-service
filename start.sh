#! /usr/bin/env sh

set -e

# Run migrations
echo "Migrations"
alembic upgrade heads

echo "Uvicorn running src.main:app --reload --host 192.168.8.104 --port 8000"
uvicorn src.main:app --reload --host 192.168.8.104 --port 8000
