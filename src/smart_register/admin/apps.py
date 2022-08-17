import django.contrib.admin
from django.apps import AppConfig
from smart_admin.apps import SmartConfig


class AuroraAdminConfig(SmartConfig):
    default_site = "smart_register.admin.site.AuroraAdminSite"
    default = False

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
        from django.contrib.admin import site
        from .panels import loaddata, dumpdata
        from smart_admin.console import panel_migrations, panel_sysinfo

        site.register_panel(loaddata)
        site.register_panel(dumpdata)
        site.register_panel(panel_migrations)
        site.register_panel(panel_sysinfo)


class AuroraAdminUIConfig(AppConfig):
    name = "smart_register.admin.ui"
