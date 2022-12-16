# colors
RED=$(if $(filter $(OS),Windows_NT),,$(shell    echo "\033[31m"))
GREEN=$(if $(filter $(OS),Windows_NT),,$(shell  echo "\033[32m"))
YELLOW=$(if $(filter $(OS),Windows_NT),,$(shell echo "\033[33m"))
BOLD=$(if $(filter $(OS),Windows_NT),,$(shell   echo "\033[1m"))
GRAY=$(if $(filter $(OS),Windows_NT),,$(shell    echo "\033[37m"))
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
	docker exec -it identity-server-poc_1 sh -c "pytest -ra -cov tests"