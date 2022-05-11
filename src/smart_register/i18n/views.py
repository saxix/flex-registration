from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import get_language

from smart_register.i18n.engine import translator


@login_required()
def editor_info(request):
    data = {
        "authenticated": request.user.is_authenticated,
        "staff": request.user.is_staff,
        "canTranslate": request.user.is_staff,
        "languageCode": get_language(),
        "editUrl": reverse("admin:i18n_message_get_or_create"),
    }
    return JsonResponse(data)


from django.views.i18n import JavaScriptCatalog, js_catalog_template

LANGUAGE_QUERY_PARAMETER = "language"


class SmartJavascriptCatalog(JavaScriptCatalog):
    domain = "djangojs"
    packages = None

    def get_catalog(self):
        catalog: dict = super().get_catalog()
        current_locale = get_language()
        dictionary = translator[current_locale]
        catalog.update(dictionary.messages)
        return catalog
