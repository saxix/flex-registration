import logging

from django.utils import translation

from smart_register.core.utils import get_default_language

logger = logging.getLogger(__name__)


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
