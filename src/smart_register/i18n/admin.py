from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.value import ValueFilter
from django.contrib.admin import register
from smart_admin.modeladmin import SmartModelAdmin

from .models import Message


@register(Message)
class MessageAdmin(SmartModelAdmin):
    search_fields = ("msgid__icontains",)
    list_display = ("msgid", "locale", "msgstr", "draft")
    list_editable = ("msgstr", "draft")
    list_filter = (
        ("msgid", ValueFilter),
        ("locale", ChoicesFieldComboFilter),
        "draft",
        ("msgstr", ValueFilter),
    )
    date_hierarchy = "timestamp"
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
        (
            None,
            {
                "fields": (
                    "draft",
                    "auto",
                )
            },
        ),
    )
    actions = ["approve"]

    def approve(self, request, queryset):
        queryset.update(draft=False)

    def get_readonly_fields(self, request, obj=None):
        if obj.pk:
            return ("msgid",)
        return self.readonly_fields

    # @button()
    # def collect(self, request):
    #     ctx = self.get_common_context(request, title="Collect")
    #     field_names = []
    #     ignored_field_names = []
    #     for model in FlexForm, FlexFormField, Registration:
    #         for record in model.objects.all():
    #             for fname in model.I18N_FIELDS:
    #                 value = getattr(record, fname)
    #                 field_names.append([fname, value])
    #         # for fname in model.I18N_ADVANCED:
    #
    #     ctx["fields"] = field_names
    #     ctx["ignored_field_names"] = ignored_field_names
    #     return render(request, "admin/i18n/message/collect.html", ctx)
