import adminactions.actions as actions
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from smart_register.core.i18n import SmartJavascriptCatalog
from smart_register.web.views.site import error_404

actions.add_to_site(admin.site)

handler404 = error_404

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    re_path(r"sax-\d*/", admin.site.urls),
    path("", include("smart_register.web.urls")),
    path("", include("social_django.urls", namespace="social")),
    path("captcha/", include("captcha.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
    path("jsi18n/<str:locale>/", SmartJavascriptCatalog.as_view(), name="javascript-catalog"),
]
