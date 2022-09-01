from django.apps import AppConfig


class AuroraAdminConfig(AppConfig):
    default = False
    name = "aurora.admin.ui"

    def ready(self):
        super().ready()
        from django.contrib.admin import site
        from smart_admin.console import (
            panel_email,
            panel_error_page,
            panel_migrations,
            panel_sentry,
            panel_redis,
            panel_sysinfo,
        )

        from .panels import dumpdata, loaddata

        site.register_panel(loaddata)
        site.register_panel(dumpdata)
        site.register_panel(panel_migrations)
        site.register_panel(panel_sysinfo)
        site.register_panel(panel_email)
        site.register_panel(panel_sentry)
        site.register_panel(panel_error_page)
        site.register_panel(panel_redis)
