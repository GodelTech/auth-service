## colors
GREEN=$(if $(filter $(OS),Windows_NT),,$(shell  echo "\033[32m"))
RESET=$(if $(filter $(OS),Windows_NT),,$(shell    echo "\033[0m"))


## Activate virtual environment
init-venv:
	poetry shell


## Project
run:
	uvicorn src.main:app --reload


## Makes migration.
migrate:
	alembic upgrade heads


## Run pytests
test:
	@echo '${GREEN}Running tests:${RESET}'
	pytest -ra


## Docker
docker:
	docker-compose -f ./docker-compose.dev.yml up

docker-test:
	docker exec -it identity-server-poc_app_1 sh -c "pytest -ra -cov tests"