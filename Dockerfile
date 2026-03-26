FROM python:3.10-slim-bullseye as requirements-stage

WORKDIR /tmp

RUN pip install poetry==1.8.3 poetry-plugin-export==1.8.0

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without dev --without-hashes

FROM python:3.10-slim-bullseye

WORKDIR /Identity

COPY --from=requirements-stage /tmp/requirements.txt /Identity/requirements.txt

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
  && pip install --no-cache-dir --upgrade -r /Identity/requirements.txt

COPY . /Identity

RUN sed -i 's/\r//' /Identity/start.sh && chmod +x /Identity/start.sh

EXPOSE 8000

CMD /Identity/start.sh
