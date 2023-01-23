import os

from django.conf import settings

from aurora.core.utils import get_session_id, has_token


def smart(request):
    return {
        "session_id": get_session_id(),
        "project": {
            "build_date": os.environ.get("BUILD_DATE", ""),
            "version": os.environ.get("VERSION", ""),
            "debug": settings.DEBUG,
            "env": settings.SMART_ADMIN_HEADER,
            "sentry_dsn": settings.SENTRY_DSN,
            "has_token": has_token(request),
            "languages": settings.LANGUAGES,
            "settings": settings,
        },
    }
