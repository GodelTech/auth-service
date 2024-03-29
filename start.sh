#! /usr/bin/env sh

set -e

# Environment
export ENV_FOR_DYNACONF=$ENVIRONMENT_NAME
echo "Environment: $ENV_FOR_DYNACONF"


if [ "$ENV_FOR_DYNACONF" = "test" ] || [ "$ENV_FOR_DYNACONF" = "pipeline" ]; then
  echo "Test or Pipeline environment. Migration and population of database done inside the tests execution"
elif [ "$ENV_FOR_DYNACONF" = "local" ] || [ "$ENV_FOR_DYNACONF" = "development" ]; then
  echo "Migrations"
  python -m factories.purge
  alembic upgrade head
  echo "Population of database"
  python -m factories.commands
else # production
  echo "Migrations"
  alembic upgrade head
  echo "Create initial data in DB"
  python -m src.initial_data
fi


echo "uvicorn src.main:app --host 0.0.0.0 --port 8000"
uvicorn src.main:app --host 0.0.0.0 --port 8000
make celery
