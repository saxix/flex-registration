import uuid
from urllib.parse import urlencode, urlparse

from environ import Env

from aurora.core.flags import parse_bool


def parse_bookmarks(value):
    return "".join(value.split(r"\n"))


def parse_emails(value):
    admins = value.split(",")
    v = [(a.split("@")[0].strip(), a.strip()) for a in admins]
    return v


DEFAULTS = {
    "AURORA_ROLE": (str, "MASTER"),  # PUBLIC | EDITOR | SOLO
    "CSP_REPORT_ONLY": (bool, True),
    # "CSP_DEFAULT_SRC": (list, ),
    # "CSP_SCRIPT_SRC": (str, None),
    "DJANGO_ADMIN_URL": (str, f"{uuid.uuid4().hex}/"),
    "DJANGO_ADMIN_TITLE": (str, "Aurora"),
    "AUTHENTICATION_BACKENDS": (list, []),
    "SECRET_KEY": (str, ""),
    "ADMINS": (parse_emails, ""),
    "ALLOWED_HOSTS": (list, []),
    "CAPTCHA_TEST_MODE": (bool, False),
    "CORS_ALLOWED_ORIGINS": (list, []),
    "DATABASE_URL": (str, "psql://postgres:@postgres:5432/aurora"),
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
    "FERNET_KEY": (str, "2jQklRvSAZUdsVOKH-521Wbf_p5t2nTDA0LgD9sgim4="),
    "INTERNAL_IPS": (list, ["127.0.0.1", "localhost"]),
    "LANGUAGE_CODE": (str, "en-us"),
    "CACHE_DEFAULT": (str, "locmemcache://"),
    "CONSTANCE_DATABASE_CACHE_BACKEND": (str, ""),
    "MEDIA_ROOT": (str, "/tmp/media/"),
    "MIGRATION_LOCK_KEY": (str, "django-migrations"),
    "ROOT_TOKEN": (str, uuid.uuid4().hex),
    "PRODUCTION_SERVER": (str, ""),
    "PRODUCTION_TOKEN": (str, ""),
    # Sentry - see CONTRIBUTING.md
    "SENTRY_DSN": (str, ""),
    "SENTRY_SECURITY_TOKEN": (str, ""),
    "SENTRY_SECURITY_TOKEN_HEADER": (str, "X-Sentry-Token"),
    "SESSION_COOKIE_DOMAIN": (str, "localhost"),
    "SESSION_COOKIE_SECURE": (bool, "false"),
    "SESSION_COOKIE_NAME": (str, "reg_id"),
    "SMART_ADMIN_BOOKMARKS": (parse_bookmarks, ""),
    # "STATIC_ROOT": (str, "/tmp/static/"),
    # "STATICFILES_STORAGE": (str, "django.contrib.staticfiles.storage.StaticFilesStorage"),
    "STATICFILES_STORAGE": (str, "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"),
    "USE_X_FORWARDED_HOST": (bool, "false"),
    "USE_HTTPS": (bool, False),
    "AZURE_CLIENT_ID": (str, None),
    "AZURE_CLIENT_SECRET": (str, None),
    "AZURE_TENANT_KEY": (str, None),
    "WHITENOISE": (bool, False),
}


class SmartEnv(Env):
    def cache_url(self, var=Env.DEFAULT_CACHE_ENV, default=Env.NOTSET, backend=None):
        v = self.str(var, default)
        if v.startswith("redisraw://"):
            scheme, string = v.split("redisraw://")
            host, *options = string.split(",")
            config = dict([v.split("=", 1) for v in options])
            if parse_bool(config.get("ssl", "false")):
                scheme = "rediss"
            else:
                scheme = "redis"
            auth = ""
            credentials = [config.pop("user", ""), config.pop("password", "")]
            if credentials[0] or credentials[1]:
                auth = f"{':'.join(credentials)}@"
            new_url = f"{scheme}://{auth}{host}/?{urlencode(config)}"
            return self.cache_url_config(urlparse(new_url), backend=backend)
        return super().cache_url(var, default, backend)


env = SmartEnv(**DEFAULTS)
