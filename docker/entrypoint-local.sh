#!/bin/bash
set -e

if [ $# -eq 0 ]; then

    python manage.py upgrade
    exec gunicorn smart_register.config.wsgi -c /code/gunicorn_config.py
else
    case "$1" in
        "dev")
        until pg_isready -h db -p 5432;
          do echo "waiting for database"; sleep 2; done;
        python manage.py collectstatic --no-input
        python manage.py migrate

        python manage.py runserver 0.0.0.0:8000

        ;;
    *)
    exec "$@"
    ;;
    esac
fi
