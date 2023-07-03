![image](https://img.shields.io/github/actions/workflow/status/GodelTech/auth-service/build-and-test.yml?logo=github)
![image](https://img.shields.io/docker/v/levigoldman/auth-service?logo=docker)
![image](https://img.shields.io/github/release-date-pre/GodelTech/auth-service?logo=github)
![image](https://img.shields.io/github/contributors/GodelTech/auth-service?logo=github)

![image](https://img.shields.io/github/v/release/GodelTech/auth-service?include_prereleases)
![image](https://img.shields.io/docker/v/levigoldman/auth-service)

# Project installation

##### Link to the GIT repository:

- *https://gitlab.godeltech.com/gte-internal/python/identity-server-poc*

##### Settings
1. Create `.env` file in project root directory and add row:
>ENV_FOR_DYNACONF=local
2. Use local for ENV_FOR_DYNACONF if you want to run migrations and populate local database
3. Use docker for ENV_FOR_DYNACONF if your database is running in a docker container
3. Our tests are running inside PostgresContainer. You need to switch ENV_FOR_DYNACONF to test
in order to execute tests.

##### Running docker:

We have docker-compose.dev.yml and docker-compose.yml where the first one
will run postgresql, pgadmin and redis.
And the docker-compose.yml will create a separate network and run
postgresql, pgadmin, redis and app all together.
If you want to spin up all services, first you need to switch to DockerAppSettings
In src/config/setup.py make: app_env = DockerAppSettings().app_env
And run the following command

- *docker-compose -f ./docker-compose.yml up*

You may run another command in a second terminal to execute tests with the following command

- *docker exec -it identity-server-poc_app_1 sh -c "pytest -ra -cov tests"*

Or run the following command to run just postgresql, pgadmin, and redis services

- *docker-compose -f ./docker-compose.dev.yml up*

##### Starting poetry:

- *poetry install*
- *poetry shell*

##### Server start:

- uvicorn src.main:app --reload

##### Settings for tests:

- Add to the pyproject.toml this:

*[tool.pytest.ini_options]
pythonpath = [
  ".", "src",
]*

- Create file "*pytest.ini*" and add to it this:

*[pytest]
pythonpath = . src*

- Run tests with "*poetry run pytest""*

##### Settings for debugger:

Add to your *.vscode/settings.json* file your paths to Virtualenv folder and to the python. To get this paths use "*poetry env info*".

Example (add your versions to *.vscode/settings.json*):
*"python.pythonPath": "/home/danya/.cache/pypoetry/virtualenvs/identity-server-poc-hY52nw-1-py3.10",
"python.defaultInterpreterPath": "/home/danya/.cache/pypoetry/virtualenvs/identity-server-poc-hY52nw-1-py3.10/bin/python",*

##### PostgreSQL admin:

*http://localhost/login?next=%2Fbrowser%2F*

- login: *admin@example.com*, password: *admin* .After logging create your personal accaunt.
- After relogging:right click "*Server*" -> "*Register*" ->"*Server*".

  Name:*is_db*

  Host name/adress:*172.20.0.1* (or your own adress)

  Username:***postgres***

  Password:*postgres*

##### Alembic update or change DB:

- upgrade:
  "alembic upgrade heads"
- change:
  "alembic revision --autogenerate -m "[_**Your comment**_]" "

##### Run Celery:

- worker:
  "celery -A src.celery_logic.celery_main worker --loglevel=info"
- beat:
  "celery -A src.celery_logic.celery_main beat --loglevel=info"

##### Links:

* Server:

  *http://127.0.0.1:8000/*
* Swagger:
* http://127.0.0.1:8000/docs*

- PostgreSQL admin:
  *http://localhost/login?next=%2Fbrowser%2F*
