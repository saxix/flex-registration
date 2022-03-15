from constance import config
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


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
