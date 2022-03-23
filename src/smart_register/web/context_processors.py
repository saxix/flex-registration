import os

from django.conf import settings


def smart(request):
    return {
        "project": {
            "build_date": os.environ.get("BUILD_DATE", ""),
            "version": os.environ.get("VERSION", ""),
            "debug": settings.DEBUG,
            "env": settings.SMART_ADMIN_HEADER,
            "sentry_dsn": settings.SENTRY_DSN,
        }
    }
