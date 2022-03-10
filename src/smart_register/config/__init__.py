import uuid

from environ import Env


def parse_bookmarks(value):
    return "".join(value.split(r"\n"))


def parse_emails(value):
    admins = value.split(",")
    v = [(a.split("@")[0].strip(), a.strip()) for a in admins]
    return v


DEFAULTS = {
    "AUTHENTICATION_BACKENDS": (list, []),
    "SECRET_KEY": (str, ""),
    "ADMINS": (parse_emails, ""),
    "TEST_USERS": (parse_emails, ""),
    "ALLOWED_HOSTS": (list, ""),
    "DATABASE_URL": (str, "psql://postgres:@postgres:5432/smart_register"),
    "DEBUG": (bool, False),
    "DEBUG_PROPAGATE_EXCEPTIONS": (bool, False),
    "ROOT_KEY": (str, uuid.uuid4().hex),
    "EMAIL_BACKEND": (str, "django.core.mail.backends.smtp.EmailBackend"),
    # 'EMAIL_BACKEND': (str, 'mailer.backend.DbBackend'),
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
    "FERNET_KEYS": (list, ""),
    # Firebase - see CONTRIBUTING.md
    "GCM_API_KEY": (str, ""),
    "GCM_APP_ID": (str, ""),
    "GCM_PROJECT_ID": (str, ""),
    "GCM_SENDER_ID": (str, ""),
    "GCM_SERVER_KEY": (str, ""),
    "GOOGLE_ANALYTICS_GTAG_PROPERTY_ID": (str, ""),
    "GOOGLE_ANALYTICS_JS_PROPERTY_ID": (str, ""),
    "ANALYTICAL_INTERNAL_IPS": (list, ["127.0.0.1"]),
    "IMPERSONATE_HEADER_KEY": (str, ""),
    "INTERNAL_IPS": (list, ["127.0.0.1", "localhost"]),
    "CACHE_DEFAULT": (str, "locmemcache://"),
    # 'CACHE_DEFAULT': (str, 'redis://redis/2?client_class=django_redis.client.DefaultClient'),
    "MEDIA_ROOT": (str, "/tmp/media/"),
    # Sentry - see CONTRIBUTING.md
    "SENTRY_DSN": (str, ""),
    "SENTRY_SECURITY_TOKEN": (str, ""),
    "SENTRY_SECURITY_TOKEN_HEADER": (str, "X-Sentry-Token"),
    "SESSION_COOKIE_DOMAIN": (str, "bob.sosbob.com"),
    "SESSION_COOKIE_SECURE": (bool, "false"),
    "SESSION_COOKIE_NAME": (str, "bob_id"),
    "SMART_ADMIN_BOOKMARKS": (parse_bookmarks, ""),
    "SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS": (list, ["os4d.org"]),
    "SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS": (list, []),
    # Google OAUTH - see CONTRIBUTING.md
    "SOCIAL_AUTH_GOOGLE_OAUTH_KEY": (str, ""),
    "SOCIAL_AUTH_GOOGLE_OAUTH_SECRET": (str, ""),
    "STATIC_ROOT": (str, "/tmp/static/"),
    "STATICFILES_STORAGE": (str, "django.contrib.staticfiles.storage.StaticFilesStorage"),
    # Stripe - see CONTRIBUTING.md
    "STRIPE_SECRET_KEY": (str, ""),
    "STRIPE_PUBLIC_KEY": (str, ""),
    "STRIPE_WEBHOOK_SECRET": (str, ""),
    # Twilio - see CONTRIBUTING.md
    "TWILIO_SID": (str, ""),
    "TWILIO_TOKEN": (str, ""),
    "TWILIO_SERVICE": (str, ""),
    "TWILIO_CALLER": (str, "+80012345678"),  # should be a twilio provided phone number
    "TWO_FACTOR_REMEMBER_COOKIE_SECURE": (bool, True),
    "TWO_FACTOR_REMEMBER_COOKIE_HTTPONLY": (bool, True),
    "USE_X_FORWARDED_HOST": (bool, "false"),
    "USE_HTTPS": (bool, False),
}

env = Env(**DEFAULTS)
