import adminactions.actions as actions
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

actions.add_to_site(admin.site)

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path("", include("smart_register.web.urls")),
    path("", include("social_django.urls", namespace="social")),
    path("api/", include("smart_register.api.urls", namespace="api")),
    path("captcha/", include("captcha.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]
