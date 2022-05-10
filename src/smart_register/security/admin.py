import logging
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib.admin import register
from smart_admin.modeladmin import SmartModelAdmin
from ..admin.mixin import LoadDumpMixin
from .models import RegistrationRole

logger = logging.getLogger(__name__)


@register(RegistrationRole)
class RegistrationRoleAdmin(LoadDumpMixin, SmartModelAdmin):
    list_display = ("registration", "user", "role")
    list_filter = (
        ("registration", AutoCompleteFilter),
        ("user", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
    )
