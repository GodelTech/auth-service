FROM repository.godeltech.com:18443/python:3.9.9-slim-buster as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM repository.godeltech.com:18443/python:3.9.9-slim-buster

WORKDIR /

COPY --from=requirements-stage /tmp/requirements.txt /requirements.txt

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . /

RUN chmod +x /start.sh

EXPOSE 8000

CMD /start.sh
