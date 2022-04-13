import uuid

from environ import Env


def parse_bookmarks(value):
    return "".join(value.split(r"\n"))


def parse_emails(value):
    admins = value.split(",")
    v = [(a.split("@")[0].strip(), a.strip()) for a in admins]
    return v


DEFAULTS = {
    # "CSP_INCLUDE_NONCE_IN": (, True),
    "CSP_REPORT_ONLY": (bool, True),
    # "CSP_DEFAULT_SRC": (list, ),
    # "CSP_SCRIPT_SRC": (str, None),
    "DJANGO_ADMIN_URL": (str, f"{uuid.uuid4().hex}/"),
    "DJANGO_ADMIN_TITLE": (str, "="),
    "AUTHENTICATION_BACKENDS": (list, []),
    "SECRET_KEY": (str, ""),
    "ADMINS": (parse_emails, ""),
    "ALLOWED_HOSTS": (list, []),
    "CAPTCHA_TEST_MODE": (bool, False),
    "CORS_ALLOWED_ORIGINS": (list, []),
    "DATABASE_URL": (str, "psql://postgres:@postgres:5432/smart_register"),
    "DEBUG": (bool, False),
    "DEBUG_PROPAGATE_EXCEPTIONS": (bool, False),
    "LOG_LEVEL": (str, "ERROR"),
    "ROOT_KEY": (str, uuid.uuid4().hex),
    # "FERNET_KEY": (str, "Nl_puP2z0-OKVNKMtPXx4jEI-ox7sKLM7CgnGT-yAug="),
    "EMAIL_BACKEND": (str, "django.core.mail.backends.smtp.EmailBackend"),
    "EMAIL_HOST": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_FROM_EMAIL": (str, ""),
    "EMAIL_PORT": (int, 587),
    "EMAIL_SUBJECT_PREFIX": (str, "[SmartRegister]"),
    "EMAIL_USE_LOCALTIME": (bool, False),
    "EMAIL_USE_TLS": (bool, True),
    "EMAIL_USE_SSL": (bool, False),
    "EMAIL_TIMEOUT": (int, 30),
    "INTERNAL_IPS": (list, ["127.0.0.1", "localhost"]),
    "LANGUAGE_CODE": (str, "en-us"),
    "CACHE_DEFAULT": (str, "locmemcache://"),
    "MEDIA_ROOT": (str, "/tmp/media/"),
    "ROOT_TOKEN": (str, uuid.uuid4().hex),
    # Sentry - see CONTRIBUTING.md
    "SENTRY_DSN": (str, ""),
    "SENTRY_SECURITY_TOKEN": (str, ""),
    "SENTRY_SECURITY_TOKEN_HEADER": (str, "X-Sentry-Token"),
    "SESSION_COOKIE_DOMAIN": (str, "localhost"),
    "SESSION_COOKIE_SECURE": (bool, "false"),
    "SESSION_COOKIE_NAME": (str, "reg_id"),
    "SMART_ADMIN_BOOKMARKS": (parse_bookmarks, ""),
    "STATIC_ROOT": (str, "/tmp/static/"),
    "STATICFILES_STORAGE": (str, "django.contrib.staticfiles.storage.StaticFilesStorage"),
    "USE_X_FORWARDED_HOST": (bool, "false"),
    "USE_HTTPS": (bool, False),
    "AZURE_CLIENT_ID": (str, None),
    "AZURE_CLIENT_SECRET": (str, None),
    "AZURE_TENANT_KEY": (str, None),
    "WHITENOISE": (bool, False),
    "LANGUAGE_CODE": (str, "en-us"),
}

env = Env(**DEFAULTS)
