import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from smart_admin.modeladmin import SmartModelAdmin

from aurora.core.admin_sync import SyncMixin

from .models import AuroraUser, OrganizationRole, RegistrationRole

logger = logging.getLogger(__name__)


@register(AuroraUser)
class AuroraUserAdmin(SyncMixin, UserAdmin):
    pass


@register(RegistrationRole)
class RegistrationRoleAdmin(SyncMixin, SmartModelAdmin):
    list_display = ("registration", "user", "role")
    list_filter = (
        ("registration", AutoCompleteFilter),
        ("user", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
    )


@register(OrganizationRole)
class OrganizationRoleAdmin(SyncMixin, SmartModelAdmin):
    list_display = ("organization", "user", "role")
    list_filter = (
        ("organization", AutoCompleteFilter),
        ("user", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
    )
