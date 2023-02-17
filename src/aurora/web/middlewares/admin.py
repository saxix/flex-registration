import logging
import re
from urllib.parse import urlparse

from constance import config
from django.conf import settings
from django.http import HttpResponse

from aurora.core.utils import is_root

logger = logging.getLogger(__name__)


class AdminSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        parts = urlparse(request.get_raw_uri())
        if not is_root(request):
            try:
                public_regex = re.compile(config.WAF_REGISTRATION_ALLOWED_HOSTNAMES)
                if not (public_regex.match(parts.netloc) or parts.path.startswith(f"/{settings.DJANGO_ADMIN_URL}")):
                    return HttpResponse("Not Allowed")
                admin_regex = re.compile(config.WAF_REGISTRATION_ALLOWED_HOSTNAMES)
                if parts.path.startswith(f"/{settings.DJANGO_ADMIN_URL}") and not admin_regex.match(parts.netloc):
                    return HttpResponse("Not Allowed")
            except Exception:
                pass
        ret = self.get_response(request)
        return ret
