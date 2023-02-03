from django.apps import AppConfig
from django.contrib.auth import get_user_model
from smart_admin.apps import SmartAuthConfig


class AuroraAuthConfig(SmartAuthConfig):
    name = "smart_admin.smart_auth"

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from smart_admin.decorators import smart_register
        from smart_admin.smart_auth.admin import ContentTypeAdmin, PermissionAdmin

        from aurora.administration.admin import AuroraGroupAdmin, AuroraUserAdmin

        smart_register(Group)(AuroraGroupAdmin)
        smart_register(get_user_model())(AuroraUserAdmin)
        smart_register(Permission)(PermissionAdmin)
        smart_register(ContentType)(ContentTypeAdmin)


class AuroraAdminConfig(AppConfig):
    default = False
    name = "aurora.administration"

    def ready(self):
        super().ready()
        from django.contrib.admin import site
        from smart_admin.console import (
            panel_email,
            panel_error_page,
            panel_migrations,
            panel_redis,
            panel_sentry,
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
