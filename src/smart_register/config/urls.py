import adminactions.actions as actions
from django.contrib import admin
from django.urls import path, include

actions.add_to_site(admin.site)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('smart_register.web.urls')),
]
