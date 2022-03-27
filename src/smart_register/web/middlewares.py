import logging
import re
from enum import IntFlag, unique

from constance import config
from constance.signals import config_updated
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.functional import cached_property
from htmlmin.main import Minifier
from sentry_sdk import configure_scope

from smart_register.core.utils import get_default_language
from smart_register.state import state

logger = logging.getLogger(__name__)


class SentryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with configure_scope() as scope:
            scope.set_tag("debug", settings.DEBUG)
            response = self.get_response(request)
        return response


class LocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = get_default_language(request)
        request.selected_language = lang
        translation.activate(lang)
        ret = self.get_response(request)
        translation.deactivate()
        return ret


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        """
        if config.MAINTENANCE_MODE:
            url = reverse("maintenance")
            if not url == request.path and settings.DJANGO_ADMIN_URL not in request.path:
                return HttpResponseRedirect(url)

        return self.get_response(request)


class SecurityHeadersMiddleware(object):
    """
    Ensure that we have proper security headers set
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "X-Frame-Options" not in response:
            response["X-Frame-Options"] = "deny"
        if "X-Content-Type-Options" not in response:
            response["X-Content-Type-Options"] = "nosniff"
        if "X-XSS-Protection" not in response:
            response["X-XSS-Protection"] = "1; mode=block"
        return response


class ThreadLocalMiddleware:
    """Middleware that puts the request object in thread local storage."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        state.request = request
        ret = self.get_response(request)
        state.request = None
        return ret


@unique
class MinifyFlag(IntFlag):
    HTML = 1
    NEWLINE = 2
    SPACES = 4


class HtmlMinMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.minifier = Minifier(
            remove_comments=True,
            remove_empty_space=True,
            remove_all_empty_space=True,
            remove_optional_attribute_quotes=True,
            reduce_empty_attributes=True,
        )
        config_updated.connect(self.update_config)

    @cached_property
    def config_value(self):
        return int(config.MINIFY_RESPONSE)

    @cached_property
    def ignore_regex(self):
        if config.MINIFY_IGNORE_PATH:
            return re.compile(config.MINIFY_IGNORE_PATH)

    def update_config(self, sender, key, old_value, new_value, **kwargs):
        if hasattr(self, "config_value"):
            del self.config_value

        if hasattr(self, "ignore_regex"):
            del self.ignore_regex

    def ignore_path(self, path):
        if self.ignore_regex:
            return self.ignore_regex.match(path)

    def can_minify(self, request, response):
        return (
            "Content-Type" in response
            and "text/html" in response["Content-Type"]
            and "admin/" not in request.path_info
            and not hasattr(request, "no_minify")
            and not self.ignore_path(request.path_info)
            and not request.headers.get("X-No-Minify")
        )

    def __call__(self, request):
        response = self.get_response(request)
        if not response.streaming and len(response.content) < 200:
            return response

        if self.can_minify(request, response):
            if bool(self.config_value & MinifyFlag.HTML):
                response.content = self.minifier.minify(response.content.decode()).encode()
                response.content = response.content.replace(b"\n", b"")
            if bool(self.config_value & MinifyFlag.NEWLINE):
                response.content = response.content.replace(b"\n", b"")
            if bool(self.config_value & MinifyFlag.SPACES):
                s = response.content
                while b"  " in s:
                    s = s.replace(b"  ", b" ")
                response.content = s
            response.headers["Content-Length"] = str(len(response.content))
        elif settings.DEBUG:
            logger.warn(f'Skip minification of "{request.path_info}"')
        return response
