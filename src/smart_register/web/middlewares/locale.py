import logging

from django.utils import translation
from flags.state import flag_enabled

from smart_register.core.utils import get_default_language
from smart_register.state import state

logger = logging.getLogger(__name__)


class LocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = get_default_language(request)
        request.selected_language = lang
        translation.activate(lang)
        state.collect_messages = flag_enabled("I18N_COLLECT_MESSAGES", request=request)

        ret = self.get_response(request)
        state.collect_messages = False
        translation.deactivate()
        return ret
