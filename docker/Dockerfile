FROM python:3.9.2-alpine3.13
ARG BUILD_DATE
ARG VERSION

RUN apk add --no-cache --virtual .build-deps \
        build-base \
        cargo \
        gcc \
        g++ \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        linux-headers \
        jpeg-dev \
        zlib-dev \
        musl-dev \
        openssl-dev \
        postgresql-dev \
        python3-dev \
        rust

RUN apk add --no-cache --virtual .run-deps \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gosu \
        nginx \
        libpq \
        libjpeg \
        libxml2 \
        libxslt \
        mailcap

WORKDIR /tmp

ENV PATH = "${PATH}:/root/.poetry/bin" \
    ADMINS="" \
    BUILD_DATE=${BUILD_DATE} \
    DATABASE_URL="" \
    DJANGO_SETTINGS_MODULE="smart_register.config.settings" \
    IPSTACK_KEY="" \
    LOG_LEVEL="ERROR" \
    NGINX_CACHE_DIR="/data/nginx/cache" \
    NGINX_MAX_BODY_SIZE=30M \
    PYTHONPATH="/code/src/" \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY="secret-key-just-for-build" \
    SENTRY_DSN="" \
    STATIC_ROOT="/var/static" \
    STATIC_URL="/static/" \
    UWSGI_PROCESSES=4 \
    VERSION=${VERSION}

RUN mkdir -p /code
COPY . /code
WORKDIR /code

RUN set -ex \
    ls -al /code \
    && pip install -U pip "poetry==1.1.13" \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root --no-interaction --no-ansi

RUN apk del .build-deps \
    && rm -rf /var/cache/apk/* \
    && rm -fr /root/.cache/ \
    && rm -fr /usr/include/ \
    && pip uninstall --help \
    && pip uninstall --no-input poetry


RUN find /usr/local/lib/python3.9/site-packages/ -name *.pyc | xargs rm -f \
    && python -O -m compileall -fqb /usr/local/lib/python3.9/site-packages/ \
    && find /usr/local/lib/python3.9/site-packages/ -name *.py | xargs rm -f

RUN addgroup --gid 1024 www \
    && adduser --disabled-password --ingroup www -S www

EXPOSE 8000

WORKDIR /code

COPY docker/bin/* /usr/local/bin/
COPY docker/conf/* /conf/
RUN ln -s /etc/nginx/nginx.conf /conf/nginx.conf

ENTRYPOINT ["docker-entrypoint.sh"]
