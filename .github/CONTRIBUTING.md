# Contributing to Auth Service

- if you have found a bug or a discrepancy with technical specifications <!-- Insert link to specs -->, consider creating an issue
- to submit a change, consider opening a PR with a concise description and preferably a link to an issue it solves (consider first creating one if it doesn't exist)

# Developer setup

## Environment

The project uses [poetry](https://github.com/python-poetry/poetry) to manage dependencies and virtual environments.
- To install dependencies into a virtual environment run:
```bash
poetry install
```
**Note:** the project has a [`.python-version`](https://github.com/GodelTech/auth-service/blob/main/.python-version) file - if you use [pyenv](https://github.com/pyenv/pyenv) to manage your python versions, it will try to use the version pinned in the file.

- To activate the virtual environment run:
```bash
poetry shell
```

Poetry keeps virtualenvs in `$HOME/.cache/pypoetry/virtualenvs` by default. If you use VSCode, you'll need to point it at this path for it to recognize the virtualenv: add `"python.venvPath": "$HOME/.cache/pypoetry/virtualenvs"` to your settings. Alternatively, you can make poetry create virtualenvs in a classic per-project `.venv` directory:
```bash
poetry config virtualenvs.in-project true
```

## Running the project locally

[Dynaconf](https://github.com/dynaconf/dynaconf) is used for configuration management. To start working, create a `.env` file in the project's root directory, and set `ENV_FOR_DYNACONF` variable:
```bash
ENV_FOR_DYNACONF=local
```
Use `local` when using a local db, use `test` when running tests.

For development, the app server runs locally, and other services (`postgres`, `pgadmin` and `redis`) run inside Docker.

To run the app server, use:
```bash
make run
```
To run Docker containers:
```bash
make docker-dev
```
or use [`./docker-compose.dev.yml`](https://github.com/GodelTech/auth-service/blob/main/docker-compose.dev.yml) directly.

After all services are up:
- the app is exposed at http://localhost:8000
- Swagger docs at http://localhost:8000/docs
- pgadmin at http://localhost/login?next=%2Fbrowser%2F

For migrations, the project uses [Alembic](https://github.com/sqlalchemy/alembic).
To run upgrade:
```bash
make migrate
```
To make changes:
```bash
alembic revision --autogenerate -m "[YOUR_MESSAGE]"
```

### PostgreSQL Admin

When you first log in, use **username**:*admin@example.com*, **password**:*admin*. Then create your personal account.

Register the db server with:
  - **name:** *is_db*
  - **address:** *172.20.0.1*
  - **username:** *postgres*
  - **password:** *postgres*

## Running tests

Tests run inside `postgres` container. Remember to set `ENV_FOR_DYNACONF` to `test` inside your `.env` file.
To run tests, use:
```bash
poetry run pytest
```

## Installing pre-commit checks

We use `pre-commit` for style checking and autoformatting - please, make sure you install `pre-commit` hooks before you start working.
To do so, run:
```bash
make install-hooks
```
