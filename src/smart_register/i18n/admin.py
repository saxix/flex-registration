from admin_extra_buttons.decorators import button
from adminfilters.value import ValueFilter
from django.contrib.admin import register
from django.shortcuts import render
from smart_admin.modeladmin import SmartModelAdmin

from .models import Message
from ..core.models import FlexForm, FlexFormField
from ..registration.models import Registration


@register(Message)
class MessageAdmin(SmartModelAdmin):
    search_fields = ("msgid",)
    list_display = ("msgid", "locale", "msgstr")
    list_editable = ("msgstr",)
    list_filter = (
        "locale",
        ("msgstr", ValueFilter),
    )
    readonly_fields = ("msgid",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "msgid",
                    "msgstr",
                    "locale",
                )
            },
        ),
    )

    @button()
    def collect(self, request):
        ctx = self.get_common_context(request, title="Collect")
        field_names = []
        ignored_field_names = []
        for model in FlexForm, FlexFormField, Registration:
            for record in model.objects.all():
                for fname in model.I18N_FIELDS:
                    value = getattr(record, fname)
                    field_names.append([fname, value])
            # for fname in model.I18N_ADVANCED:

        ctx["fields"] = field_names
        ctx["ignored_field_names"] = ignored_field_names
        return render(request, "admin/i18n/message/collect.html", ctx)
