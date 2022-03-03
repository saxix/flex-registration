ARG BASE_IMAGE
FROM registry.gitlab.com/bitcaster/sos/base:${BASE_IMAGE}

EXPOSE 8000
VOLUME ["/var/sos/"]
WORKDIR /var/sos

ENV DOCKER_BUILD=${BUILD_DATE}  \
    ADMINS="" \
    AUTOSTART_CELERY=1 \
    BUILD_DATE=$BUILD_DATE \
    CHANNEL_URLS=""\
    DATABASE_URL="" \
    DEV_FOOTER_INFO="" \
    DJANGO_SETTINGS_MODULE="sos.config.settings" \
    IPSTACK_KEY="" \
    LOG_LEVEL="ERROR" \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY="secret-key-just-for-build" \
    SENTRY_DSN="" \
    STATIC_ROOT="/var/run/static" \
    SOCIAL_AUTH_GOOGLE_OAUTH_KEY=""\
    SOCIAL_AUTH_GOOGLE_OAUTH_SECRET=""\
    TWILIO_CALLER_ID=""\
    VERSION=${VERSION}

COPY . /code
WORKDIR /code
RUN set -ex \
    ls -al /code \
    && mkdir -p /var/sos/ \
    && sha1sum -c /CHECKSUM \
    && pip install -U pip "poetry==1.1.5" \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY docker/circus.conf /etc/
COPY docker/uwsgi.ini /etc/

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["run"]
