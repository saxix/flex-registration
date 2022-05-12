from django.apps import AppConfig


class Config(AppConfig):
    name = "smart_register.i18n"

    def ready(self):
        from . import handlers  # noqa
