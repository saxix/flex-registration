import logging
import mimetypes
import os
from collections import OrderedDict
from pathlib import Path

from django_regex.utils import RegexList

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
FERNET_KEY = env("FERNET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
DEBUG_PROPAGATE_EXCEPTIONS = env("DEBUG_PROPAGATE_EXCEPTIONS")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL")

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
    # -- dev --
    "debug_toolbar",
    # ---
    "smart_admin.apps.SmartLogsConfig",
    "smart_admin.apps.SmartTemplateConfig",
    "smart_admin.apps.SmartAuthConfig",
    "smart_admin.apps.SmartConfig",
    # 'smart_admin',
    "admin_ordering",
    "django_sysinfo",
    "admin_extra_buttons",
    "adminfilters",
    "adminactions",
    "constance",
    "constance.backends.database",
    "flags",
    "jsoneditor",
    "captcha",
    "social_django",
    "corsheaders",
    "simplemathcaptcha",
    # ---
    "smart_register",
    "smart_register.web",
    "smart_register.core",
    "smart_register.registration",
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

MIDDLEWARE = [
    # "django.middleware.cache.UpdateCacheMiddleware",
    "smart_register.web.middlewares.ThreadLocalMiddleware",
    "smart_register.web.middlewares.SentryMiddleware",
    "smart_register.web.middlewares.SecurityHeadersMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "smart_register.web.middlewares.MaintenanceMiddleware",
    "smart_register.web.middlewares.LocaleMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "smart_register.web.middlewares.HtmlMinMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "django.middleware.cache.FetchFromCacheMiddleware",
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
                "constance.context_processors.config",
                "smart_register.web.context_processors.smart",
                # Social auth context_processors
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "smart_register.config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = 60
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

LANGUAGE_CODE = env("LANGUAGE_CODE")
LANGUAGE_COOKIE_NAME = "smart-register-language"
LANGUAGES = (
    ("uk-ua", "український"),
    ("en-us", "English"),
    ("pl-pl", "Polskie"),
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
LOCALE_PATHS = (str(PACKAGE_DIR / "LOCALE"),)

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
# SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN')
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# Ensure STATIC_ROOT exists.
# os.makedirs(STATIC_ROOT, exist_ok=True)

STATIC_URL = f"/static/{os.environ.get('VERSION', '')}/"
# STATIC_URL = f"/static/"
STATIC_ROOT = env("STATIC_ROOT")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "web/static"),
]

# -------- Added Settings
ADMINS = env("ADMINS")
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
] + env("AUTHENTICATION_BACKENDS")

CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
CSRF_COOKIE_SECURE = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env("USE_X_FORWARDED_HOST")

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
        "level": env("LOG_LEVEL"),
    },
    "environ": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
        "propagate": False,
    },
    "flags": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
    },
    "django": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
    },
    "social_core": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
    },
    "smart_register": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
    },
}

# ------ Custom App


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

MAX_OBSERVED = 1
SENTRY_DSN = env("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            sentry_logging,
        ],
        release=smart_register.VERSION,
        send_default_pii=True,
    )
CORS_ALLOWED_ORIGINS = [
    "https://excubo.unicef.io",
] + env("CORS_ALLOWED_ORIGINS")

CONSTANCE_ADDITIONAL_FIELDS = {
    "html_minify_select": [
        "bitfield.forms.BitFormField",
        {"initial": 0, "required": False, "choices": (("html", "HTML"), ("line", "NEWLINE"), ("space", "SPACES"))},
    ],
}
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
# CONSTANCE_DATABASE_CACHE_BACKEND = 'default'
CONSTANCE_CONFIG = OrderedDict(
    {
        "CACHE_FORMS": (False, "", bool),
        "HOME_PAGE_REGISTRATIONS": ("", "", str),
        "SMART_ADMIN_BOOKMARKS": (
            "",
            "",
            str,
        ),
        "LOG_POST_ERRORS": (False, "", bool),
        "MINIFY_RESPONSE": (0, "select yes or no", "html_minify_select"),
        "MINIFY_IGNORE_PATH": (r"", "regex for ignored path", str),
        "BASE_TEMPLATE": ("base_lean.html", "Default base template", str),
        "HOME_TEMPLATE": ("home.html", "Default home.html", str),
        "QRCODE": (True, "Enable QRCode generation", bool),
        "SHOW_REGISTER_ANOTHER": (True, "Enable QRCode generation", bool),
        "MAINTENANCE_MODE": (False, "set maintenance mode On/Off", bool),
    }
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
SMART_ADMIN_HEADER = env("DJANGO_ADMIN_TITLE")
SMART_ADMIN_BOOKMARKS = "smart_register.core.utils.get_bookmarks"

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
    "DEVELOP_DEBUG_TOOLBAR": [],
    "SENTRY_JAVASCRIPT": [],
}

JSON_EDITOR_JS = "https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/8.6.4/jsoneditor.js"
JSON_EDITOR_CSS = "https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/8.6.4/jsoneditor.css"
JSON_EDITOR_INIT_JS = "jsoneditor/jsoneditor-init.js"

# CAPTCHA_IMAGE_SIZE = 300,200
CAPTCHA_FONT_SIZE = 40
CAPTCHA_CHALLENGE_FUNCT = "captcha.helpers.random_char_challenge"
CAPTCHA_TEST_MODE = env("CAPTCHA_TEST_MODE")
CAPTCHA_GET_FROM_POOL = True


# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'


# DEBUG TOOLBAR
def show_ddt(request):  # pragma: no-cover
    # use https://bewisse.com/modheader/ to set custom header
    # key must be `X-DDT` (no HTTP_ prefix no underscore)
    from flags.state import flag_enabled

    if request.path in RegexList(("/tpl/.*", "/api/.*", "/dal/.*")):
        return False
    return flag_enabled("DEVELOP_DEBUG_TOOLBAR", request=request)
    # if request.user.is_authenticated:
    #     if request.path in RegexList(('/tpl/.*', '/api/.*', '/dal/.*', '/healthcheck/')):
    #         return False
    # return request.META.get('HTTP_DEV_DDT', None) == env('DEV_DDT_KEY')


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_ddt,
    "JQUERY_URL": "",
}
INTERNAL_IPS = env.list("INTERNAL_IPS")
DEBUG_TOOLBAR_PANELS = [
    # 'debug_toolbar.panels.history.HistoryPanel',
    # 'debug_toolbar.panels.versions.VersionsPanel',
    # 'debug_toolbar.panels.timer.TimerPanel',
    # 'flags.panels.FlagsPanel',
    # 'flags.panels.FlagChecksPanel',
    # 'debug_toolbar.panels.settings.SettingsPanel',
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    # 'debug_toolbar.panels.templates.TemplatesPanel',
    "debug_toolbar.panels.cache.CachePanel",
    # 'debug_toolbar.panels.signals.SignalsPanel',
    "debug_toolbar.panels.logging.LoggingPanel",
    # 'debug_toolbar.panels.redirects.RedirectsPanel',
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

ROOT_TOKEN = env("ROOT_TOKEN")
CSRF_FAILURE_VIEW = "smart_register.web.views.site.error_csrf"

# Azure login

# Social Auth settings.
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = env("AZURE_CLIENT_ID")
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = env("AZURE_CLIENT_SECRET")
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = env("AZURE_TENANT_KEY")
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "email",
]
# SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_PIPELINE = (
    "smart_register.core.authentication.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "smart_register.core.authentication.require_email",
    "social_core.pipeline.social_auth.associate_by_email",
    "smart_register.core.authentication.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "smart_register.core.authentication.user_details",
)
SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_USER_FIELDS = [
    "email",
    "fullname",
]

SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SCOPE = [
    "openid",
    "email",
    "profile",
]

SOCIAL_AUTH_SANITIZE_REDIRECTS = True
# fix admin name
LOGIN_URL = "/login/azuread-tenant-oauth2"
LOGIN_REDIRECT_URL = f"/{DJANGO_ADMIN_URL}"

# allow upload big file
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 2  # 2M
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE
