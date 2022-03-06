from import_export import resources

from django.contrib.admin import register
from import_export.admin import ImportExportMixin
from smart_admin.modeladmin import SmartModelAdmin

from .models import Registration, Record


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration


@register(Registration)
class RegistrationAdmin(ImportExportMixin, SmartModelAdmin):
    pass


@register(Record)
class RecordAdmin(SmartModelAdmin):
    pass
