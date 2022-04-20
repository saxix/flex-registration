import django.contrib.admin
from smart_admin.apps import SmartConfig


class AdminConfig(SmartConfig):
    default_site = "smart_register.admin.site.AuroraAdminSite"
    default = False

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
