import logging
import mimetypes
import os
from collections import OrderedDict
from pathlib import Path

import smart_register

from . import env

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)

PACKAGE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PACKAGE_DIR.parent
DEV_DIR = SRC_DIR.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
DEBUG_PROPAGATE_EXCEPTIONS = env("DEBUG_PROPAGATE_EXCEPTIONS")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Application definition
SITE_ID = 1
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.forms",
    "import_export",
    # ---
    "smart_admin.apps.SmartLogsConfig",
    "smart_admin.apps.SmartTemplateConfig",
    "smart_admin.apps.SmartConfig",
    # 'smart_admin',
    "admin_ordering",
    "django_sysinfo",
    "admin_extra_buttons",
    "social_django",
    "adminfilters",
    "adminactions",
    "constance",
    "constance.backends.database",
    "flags",
    "hijack",
    "jsoneditor",
    "captcha",
    "smart_register",
    "smart_register.web",
    "smart_register.core",
    "smart_register.registration",
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "smart_register.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PACKAGE_DIR / "core/templates", PACKAGE_DIR / "web/templates"],
        # 'APP_DIRS': True,
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "constance.context_processors.config",
            ],
        },
    },
]

WSGI_APPLICATION = "smart_register.config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {"default": env.db("DATABASE_URL")}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

CACHES = {
    "default": env.cache_url("CACHE_DEFAULT"),
}

if DEBUG:
    AUTH_PASSWORD_VALIDATORS = []
else:
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGE_COOKIE_NAME = "smart-register-language"
LANGUAGES = (
    ("en-us", "English"),
    ("pl-pl", "Polskie"),
    ("uk-UA", "український")
    # ("de-de", "Deutsch"),
    # ("es-es", "Español"),
    # ("fr-fr", "Français"),
    # ("it-it", "Italiano"),
    # ("ro-ro", "Română"),
    # ("pt-pt", "Português"),
    # ("pl-pl", "Pусский"),
    # ('ta-ta', 'தமிழ்'),  # Tamil
    # ('hi-hi', 'हिंदी'),  # Hindi
)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
# SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN')
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOCALE_PATHS = (str(PACKAGE_DIR / "LOCALE"),)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# Ensure STATIC_ROOT exists.
os.makedirs(STATIC_ROOT, exist_ok=True)

STATIC_URL = "/static/"
# STATIC_ROOT = env('STATIC_ROOT')
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "web/static"),
]

# -------- Added Settings
ADMINS = env("ADMINS")
TEST_USERS = env("TEST_USERS")
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
] + env("AUTHENTICATION_BACKENDS")

HIJACK_PERMISSION_CHECK = "smart_register.utils.is_root"
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_DEFAULT_FROM = env("EMAIL_FROM_EMAIL")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_TIMEOUT = env("EMAIL_TIMEOUT")
EMAIL_USE_SSL = env("EMAIL_USE_SSL")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")

# FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'
LOGIN_REDIRECT_URL = "summary"
LOGOUT_REDIRECT_URL = "index"
# LOGIN_URL = 'index'
LOGIN_URL = "login"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s: %(message)s"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "environ": {
        "handlers": ["console"],
        "level": "ERROR",
        "propagate": False,
    },
    "flags": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "django": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "social_core": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "smart_register": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}

USE_X_FORWARDED_HOST = env("USE_X_FORWARDED_HOST")

# ------ Custom App
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
# CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

CONSTANCE_ADDITIONAL_FIELDS = {}

DATE_INPUT_FORMATS = [
    "%Y-%m-%d",  # '2006-10-25'
    "%Y/%m/%d",  # '2006/10/25'
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y",  # '10/25/06'
    "%b %d %Y",  # 'Oct 25 2006'
    "%b %d, %Y",  # 'Oct 25, 2006'
    "%d %b %Y",  # '25 Oct 2006'
    "%d %b, %Y",  # '25 Oct, 2006'
    "%B %d %Y",  # 'October 25 2006'
    "%B %d, %Y",  # 'October 25, 2006'
    "%d %B %Y",  # '25 October 2006'
    "%d %B, %Y",  # '25 October, 2006'
]

CONSTANCE_CONFIG = OrderedDict(
    {
        "SMART_ADMIN_BOOKMARKS": (
            env("SMART_ADMIN_BOOKMARKS"),
            "",
            str,
        ),
    }
)

MAX_OBSERVED = 1
SENTRY_DSN = env("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            sentry_logging,
            RedisIntegration(),
        ],
        release=smart_register.VERSION,
        send_default_pii=True,
    )

SMART_ADMIN_SECTIONS = {
    "Registration": ["registration"],
    "Form Builder": ["core"],
    "Configuration": ["constance", "flags"],
    "Security": ["auth", "social_auth"],
    "Other": [],
    "_hidden_": [],
}
SMART_ADMIN_TITLE = "="
SMART_ADMIN_HEADER = "="

SMART_ADMIN_PROFILE_LINK = True

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

RATELIMIT = {
    "PERIODS": {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 60 * 60,
        "M": 30 * 24 * 60 * 60,
        "y": 365 * 24 * 60 * 60,
    }
}

AA_PERMISSION_HANDLER = 3  # AA_PERMISSION_CREATE_USE_APPCONFIG

SYSINFO = {
    "host": True,
    "os": True,
    "python": True,
    "modules": True,
    # "project": {
    #     "mail": False,
    #     "installed_apps": False,
    #     "databases": False,
    #     "MEDIA_ROOT": False,
    #     "STATIC_ROOT": False,
    #     "CACHES": False
    # },
    # "checks": None,
}

IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

FLAGS_STATE_LOGGING = DEBUG

FLAGS = {
    "DEVELOP_DEVELOPER": [],
}

JSON_EDITOR_JS = "https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/8.6.4/jsoneditor.js"
JSON_EDITOR_CSS = "https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/8.6.4/jsoneditor.css"
JSON_EDITOR_INIT_JS = "jsoneditor/jsoneditor-init.js"

# CAPTCHA_IMAGE_SIZE = 300,200
CAPTCHA_FONT_SIZE = 40
CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.random_char_challenge"
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
