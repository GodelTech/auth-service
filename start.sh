#! /usr/bin/env sh

set -e

# Environment
#export ENV_FOR_DYNACONF="development"
#echo "Environment: $ENV_FOR_DYNACONF"


echo "Uvicorn running src.main:app --reload --host 0.0.0.0 --port 8000"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
