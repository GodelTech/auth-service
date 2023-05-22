## colors
GREEN=$(if $(filter $(OS),Windows_NT),,$(shell  echo "\033[32m"))
RESET=$(if $(filter $(OS),Windows_NT),,$(shell    echo "\033[0m"))


## Activate virtual environment
init-venv:
	poetry shell


## Project
run:
	uvicorn src.main:app --reload


## Install all packages using poetry
install:
	poetry install
	$(MAKE) install-hooks

## Install pre-commit hooks.
install-hooks:
	pre-commit install --hook-type pre-commit
	pre-commit install --hook-type commit-msg
	pre-commit install --install-hooks


## Makes migration.
migrate:
	alembic upgrade heads


## Linters with pre-commit
check:
	@echo '${GREEN}Checking Linters${RESET}'
	pre-commit run --all-files


## Populate database
populate-db:
	python -m factories.commands


## Run pytests
test:
	@echo '${GREEN}Running tests:${RESET}'
	pytest -ra


## Docker
docker-dev:
	docker-compose -f ./docker-compose.dev.yml up

docker:
	docker run -d --name identity-server-provider --net=host -p 8000:8000 -v /var/run/docker.sock:/var/run/docker.sock identity

docker-test:
	docker exec -it identity-server-provider sh -c "pytest -ra -cov tests"


## Bump2version
mark-patch:
	bump2version --allow-dirty patch

mark-minor:
	bump2version --allow-dirty minor

mark-major:
	bump2version --allow-dirty major
