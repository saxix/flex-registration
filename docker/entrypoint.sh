#!/bin/bash
set -e
export NGINX_MAX_BODY_SIZE="${NGINX_MAX_BODY_SIZE:-30M}"
export NGINX_CACHE_DIR="${NGINX_CACHE_DIR:-/data/nginx/cache}"
export DOLLAR='$'
export STATIC_ROOT="${STATIC_ROOT}${STATIC_URL}"

mkdir -p /var/run ${NGINX_CACHE_DIR} ${MEDIA_ROOT} ${STATIC_ROOT}
echo "created support dirs /var/run ${MEDIA_ROOT} ${STATIC_ROOT}"


if [ $# -eq 0 ]; then
    python manage.py upgrade --no-input
    envsubst < /conf/nginx.conf.tpl > /conf/nginx.conf && nginx -tc /conf/nginx.conf
    nginx -c /conf/nginx.conf
    exec uwsgi --ini /conf/uwsgi.ini
#   exec gunicorn smart_register.config.wsgi -c /conf/gunicorn_config.py
else
    case "$1" in
        "dev")
        until pg_isready -h db -p 5432;
          do echo "waiting for database"; sleep 2; done;
        python manage.py collectstatic --no-input
        python manage.py migrate

        python manage.py runserver 0.0.0.0:8000
        ;;
       "dev")
       ;;
    *)
    exec "$@"
    ;;
    esac
fi
