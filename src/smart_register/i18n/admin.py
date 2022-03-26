from django.contrib.admin import register
from smart_admin.modeladmin import SmartModelAdmin

from .models import Message


@register(Message)
class MessageAdmin(SmartModelAdmin):
    pass
