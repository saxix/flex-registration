import logging

from dateutil.utils import today

from admin_extra_buttons.decorators import button, link
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.value import ValueFilter
from django.contrib.admin import register
from django.shortcuts import render

from smart_admin.modeladmin import SmartModelAdmin

from .models import Message

logger = logging.getLogger(__name__)


@register(Message)
class MessageAdmin(SmartModelAdmin):
    search_fields = ("msgid__icontains",)
    list_display = ("id", "msgid", "locale", "msgstr", "draft")
    list_editable = ("msgstr", "draft")
    list_filter = (
        ("msgid", ValueFilter),
        ("md5", ValueFilter),
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

    @link()
    def translate(self, button):
        return button

    @button()
    def create_translation(self, request):
        from smart_register.i18n.models import Message
        from smart_register.i18n.forms import TranslationForm

        ctx = self.get_common_context(
            request,
            media=self.media,
            title="Generate Translation",
        )
        if request.method == "POST":
            form = TranslationForm(request.POST)
            if form.is_valid():
                locale = form.cleaned_data["locale"]
                existing = Message.objects.filter(locale=locale).count()
                try:
                    for msg in Message.objects.exclude(locale=locale).order_by("msgid").distinct():
                        Message.objects.create(msgid=msg.msgid, msgstr=msg.msgid, locale=locale, draft=True)
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)

                updated = Message.objects.filter(locale=locale).count()
                added = Message.objects.filter(locale=locale, draft=True, timestamp__date=today())
                self.message_user(request, f"{updated - existing} messages created. {updated} available")
                ctx["locale"] = locale
                ctx["added"] = added
            else:
                ctx["form"] = form
        else:
            form = TranslationForm()
            ctx["form"] = form
        return render(request, "admin/i18n/message/translation.html", ctx)

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
