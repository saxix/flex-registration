#!/bin/bash
set -e

until pg_isready -h db -p 5432;
  do echo "waiting for database"; sleep 2; done;
case "$1" in
    "dev")
    python manage.py collectstatic --no-input
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000

    ;;
*)
exec "$@"
;;
esac