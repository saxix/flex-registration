from admin_extra_buttons.decorators import button
from django.contrib.admin import register
from django.db.models import CharField
from django.shortcuts import render
from smart_admin.modeladmin import SmartModelAdmin

from .models import Message
from ..core.models import FlexForm, FlexFormField, OptionSet
from ..registration.models import Registration


@register(Message)
class MessageAdmin(SmartModelAdmin):
    list_display = ("msgid", "locale", "msgstr")
    search_fields = ("msgid",)
    list_filter = ("locale",)
    FIELD_TYPES = (CharField,)

    @button()
    def collect(self, request):
        ctx = self.get_common_context(request, title="Collect")
        field_names = []
        ignored_field_names = []
        for model in FlexForm, FlexFormField, OptionSet, Registration:
            fields = model._meta.get_fields()
            for f in fields:
                if isinstance(f, self.FIELD_TYPES):
                    field_names.append(
                        [
                            f.name,
                            f.__class__.__name__,
                        ]
                    )
                else:
                    ignored_field_names.append(
                        [
                            f.name,
                            f.__class__.__name__,
                        ]
                    )

        ctx["fields"] = field_names
        ctx["ignored_field_names"] = ignored_field_names
        return render(request, "admin/i18n/message/collect.html", ctx)
