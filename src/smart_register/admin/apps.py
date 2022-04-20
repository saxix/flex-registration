import django.contrib.admin
from django.apps import AppConfig

from smart_admin.apps import SmartConfig


class AuroraAdminConfig(SmartConfig):
    default_site = "smart_register.admin.site.AuroraAdminSite"
    default = False

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()


class AuroraAdminUIConfig(AppConfig):
    name = "smart_register.admin.ui"
