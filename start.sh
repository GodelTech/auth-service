#! /usr/bin/env sh

set -e

export ENV_FOR_DYNACONF="pipeline"
echo "Environment: $ENV_FOR_DYNACONF"

echo "uvicorn src.main:app --host 0.0.0.0 --port 8000"
uvicorn src.main:app --host 0.0.0.0 --port 8000
