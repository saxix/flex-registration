from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, translate_url
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import (
    LANGUAGE_SESSION_KEY,
    check_for_language,
    get_language,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.views.i18n import JavaScriptCatalog

from aurora.i18n.engine import translator

LANGUAGE_QUERY_PARAMETER = "language"


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


class SmartJavascriptCatalog(JavaScriptCatalog):
    domain = "djangojs"
    packages = None

    def get_catalog(self):
        catalog: dict = super().get_catalog()
        current_locale = get_language()
        dictionary = translator[current_locale]
        catalog.update(dictionary.messages)
        return catalog

    @method_decorator(condition(lambda *a, **kw: cache.get("i18n")))
    def get(self, request, *args, **kwargs):
        return super().get(request)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return response


@csrf_exempt
def set_language(request):
    """
    Redirect to a given URL while setting the chosen language in the session
    (if enabled) and in a cookie. The URL and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next_url = request.POST.get("next", request.GET.get("next"))
    if (next_url or request.accepts("text/html")) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == "POST":
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            if next_url:
                next_trans = translate_url(next_url, lang_code)
                if next_trans != next_url:
                    response = HttpResponseRedirect(next_trans)
            if hasattr(request, "session"):
                # Storing the language in the session is deprecated.
                # (RemovedInDjango40Warning)
                request.session[LANGUAGE_SESSION_KEY] = lang_code
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
    return response
