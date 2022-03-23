from constance import config
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from sentry_sdk import configure_scope

from smart_register.state import state


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
            if not url == request.path and settings.ADMIN_URL not in request.path:
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
