## Virtual environment
init-venv:
	poetry shell

## Install all packages using poetry
install:
	poetry install

## Migration.
migrate:
	alembic upgrade heads

## Project
run:
	uvicorn src.main:app --reload

## Pytest
test:
	pytest -ra

## Docker
docker:
	docker-compose -f ./docker-compose.dev.yml up


