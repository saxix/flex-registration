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
                redis-server \
                gdal-bin \
                curl \
    && locale-gen --no-purge uk_UA.UTF-8 \
    && apt-get clean

ENV POETRY_VERSION=1.1.13 \
    PATH="${PATH}:/root/.poetry/bin" \
    ADMINS="" \
    BUILD_DATE=${BUILD_DATE} \
    CACHE_DEFAULT="redis://127.0.0.1/0" \
    CONSTANCE_DATABASE_CACHE_BACKEND="" \
    DATABASE_URL="" \
    DJANGO_SETTINGS_MODULE="aurora.config.settings" \
    IPSTACK_KEY="" \
    LOG_LEVEL="ERROR" \
    NGINX_CACHE_DIR="/data/nginx/cache" \
    NGINX_MAX_BODY_SIZE=30M \
    REDIS_LOGLEVEL="warning" \
    REDIS_MAXMEMORY="100Mb" \
    REDIS_MAXMEMORY_POLICY="volatile-ttl" \
    PYTHONPATH="/code/src/" \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY="secret-key-just-for-build" \
    SENTRY_DSN="" \
    STATIC_ROOT="/var/static" \
    STATIC_URL="/static/" \
    UWSGI_PROCESSES=4 \
    VERSION=${VERSION}

WORKDIR /code/
ADD . /code/

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root \
    && pip install uwsgi

EXPOSE 8000

ADD ./docker/conf/nginx/* /var/nginx/
ADD ./docker/conf/* /conf/
ADD ./docker/bin/* /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
