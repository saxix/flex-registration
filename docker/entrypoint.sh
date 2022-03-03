#!/bin/sh -e
export MEDIA_ROOT="/var/sos/media"
export STATIC_ROOT="/var/sos/static"
export CACHE_TTL=604800 # 1 week

mkdir -p /var/sos/run ${MEDIA_ROOT} ${STATIC_ROOT}
chown www:sos -R /code /var/sos/ ${MEDIA_ROOT} ${STATIC_ROOT}
chmod 775 /code /var/sos/ ${MEDIA_ROOT} ${STATIC_ROOT}
chmod g+s /code /var/sos/ ${MEDIA_ROOT} ${STATIC_ROOT}

rm -f /var/sos/run/*

echo "$*"
echo "STATIC_ROOT ${STATIC_ROOT}"
echo "MEDIA_ROOT ${MEDIA_ROOT}"

export BOB_VERSION=`django-admin bob version`

cd /var/sos/

if [ "$*" = "run" ]; then
  django-admin upgrade -v 3
  exec gosu www circusd /etc/circus.conf
elif [ "$*" = "dev" ]; then
  exec gosu www django-admin runserver 0.0.0.0:8000
else
  exec "$@"
fi
