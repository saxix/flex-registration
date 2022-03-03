from django.contrib.admin import register
from smart_admin.modeladmin import SmartModelAdmin

from .models import DataSet, Record


@register(DataSet)
class DataSetAdmin(SmartModelAdmin):
    pass


@register(Record)
class RecordAdmin(SmartModelAdmin):
    pass
