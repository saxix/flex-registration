from django.apps import AppConfig


class Config(AppConfig):
    name = "smart_register.core"

    def ready(self):
        from smart_register.core.registry import field_registry
        from smart_register.core.models import CustomFieldType

        for field in CustomFieldType.objects.all():
            field_registry.register(field.get_class())
