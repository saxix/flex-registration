import adminactions.actions as actions
import debug_toolbar
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import set_language
from smart_register.web.views.site import error_404

actions.add_to_site(admin.site)

handler404 = error_404

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    re_path(r"sax-\d*/", admin.site.urls),
    path("api/", include("smart_register.api.urls", namespace="api")),
    path("", include("smart_register.web.urls")),
    path("", include("social_django.urls", namespace="social")),
    path("captcha/", include("captcha.urls")),
    path("i18n/setlang/", set_language, name="set_language"),
    path("i18n/", include("smart_register.i18n.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]

urlpatterns += i18n_patterns(
    path("", include("smart_register.registration.urls")),
    path("", include("smart_register.core.urls")),
)
