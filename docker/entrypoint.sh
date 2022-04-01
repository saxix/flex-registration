#!/bin/bash
set -e
mkdir -p /var/sos/run ${MEDIA_ROOT} ${STATIC_ROOT}

if [ $# -eq 0 ]; then
    python manage.py upgrade --no-input
    nginx -c /etc/nginx.conf
    uwsgi --ini /etc/uwsgi.ini
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
