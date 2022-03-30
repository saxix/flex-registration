import os

from django.conf import settings

from smart_register.core.utils import has_token


def smart(request):
    return {
        "project": {
            "build_date": os.environ.get("BUILD_DATE", ""),
            "version": os.environ.get("VERSION", ""),
            "debug": settings.DEBUG,
            "env": settings.SMART_ADMIN_HEADER,
            "sentry_dsn": settings.SENTRY_DSN,
            "has_token": has_token(request),
        }
    }
