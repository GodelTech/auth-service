#! /usr/bin/env sh

set -e

# Environment
export ENV_FOR_DYNACONF="pipeline"
echo "Environment - 0: $ENV_FOR_DYNACONF"
echo "Environment - 1: $ENVIRONMENT_NAME"
echo "Environment - 2: $CI_ENVIRONMENT_NAME"
echo "Environment - 3: $NAME"



echo "uvicorn src.main:app --host 0.0.0.0 --port 8000"
uvicorn src.main:app --host 0.0.0.0 --port 8000
