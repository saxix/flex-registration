FROM python:3.9.2-slim-buster
ARG BUILD_DATE
ARG VERSION

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    locales \
    circus \
    nginx \
    locales-all \
    gettext \
    libjpeg-dev \
    zlib1g-dev \
    git-core \
    postgresql-client \
    libpq-dev \
    python-psycopg2 \
    python-gdal \
    gdal-bin \
    curl \
    && locale-gen --no-purge uk_UA.UTF-8 \
    && apt-get clean

WORKDIR /tmp

ENV POETRY_VERSION=1.1.13
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH = "${PATH}:/root/.poetry/bin"
ENV ADMINS="" \
    BUILD_DATE=${BUILD_DATE} \
    VERSION=${VERSION} \
    DATABASE_URL="" \
    DJANGO_SETTINGS_MODULE="smart_register.config.settings" \
    IPSTACK_KEY="" \
    LOG_LEVEL="ERROR" \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY="secret-key-just-for-build" \
    SENTRY_DSN="" \
    STATIC_ROOT="/var/static" \
    STATIC_URL="/static/" \
    PYTHONPATH="/code/src/" \
    NGINX_MAX_BODY_SIZE=30M \

ADD pyproject.toml poetry.lock /tmp/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root \
  && pip install uwsgi


ADD . /code/

WORKDIR /code/

EXPOSE 8000

ADD ./docker/entrypoint.sh /bin/
ADD ./docker/conf/* /conf/

RUN chmod +x /bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
