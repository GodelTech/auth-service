FROM python:3.9-slim-buster

WORKDIR /Identity

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /Identity/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

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

RUN chmod +x /Identity/start.sh

EXPOSE 8000

CMD /Identity/start.sh
