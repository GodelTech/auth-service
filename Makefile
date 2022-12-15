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

## Pytests
test:
	pytest -ra

## Docker
docker:
	docker-compose -f ./docker-compose.dev.yml up

build-docker:
	docker build -t identity-server .

run-docker:
	docker run -it -p 8000:8000 identity-server


