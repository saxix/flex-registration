import adminactions.actions as actions
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

actions.add_to_site(admin.site)

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("smart_register.web.urls")),
    path("captcha/", include("captcha.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]
