from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


class Config(AppConfig):
    name = "smart_register.core"

    def ready(self):
        from smart_register.core.models import CustomFieldType
        from smart_register.core.registry import field_registry

        from . import flags  # noqa
        from .handlers import cache_handler

        cache_handler()
        try:
            for field in CustomFieldType.objects.all():
                field_registry.register(field.get_class())
        except (OperationalError, ProgrammingError):
            pass
