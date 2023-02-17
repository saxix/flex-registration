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
        if is_root(request):
            return self.get_response(request)
        else:
            parts = urlparse(request.get_raw_uri())
            try:
                if parts.path.startswith(f"/{settings.DJANGO_ADMIN_URL}"):
                    admin_regex = re.compile(config.WAF_ADMIN_ALLOWED_HOSTNAMES)
                    if not admin_regex.match(parts.netloc):
                        return HttpResponse("Not Allowed")
                else:
                    public_regex = re.compile(config.WAF_REGISTRATION_ALLOWED_HOSTNAMES)
                    if not public_regex.match(parts.netloc):
                        return HttpResponse("Not Allowed")
            except Exception as e:
                logging.exception(e)
            ret = self.get_response(request)
            return ret
