import logging
from urllib.parse import unquote

from django.urls import reverse

from admin_extra_buttons.decorators import button, link, view
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.value import ValueFilter
from dateutil.utils import today
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import register
from django.http import HttpResponseRedirect
from django.shortcuts import render
from smart_admin.modeladmin import SmartModelAdmin

from ..admin.mixin import LoadDumpMixin
from .models import Message

logger = logging.getLogger(__name__)


@register(Message)
class MessageAdmin(LoadDumpMixin, SmartModelAdmin):
    search_fields = ("msgid__icontains",)
    list_display = ("id", "msgid", "locale", "msgstr", "draft")
    list_editable = ("msgstr", "draft")
    readonly_fields = ("md5", "msgcode")
    list_filter = (
        ("msgid", ValueFilter),
        ("msgcode", ValueFilter),
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
            {"fields": (("draft", "auto"),)},
        ),
        (
            None,
            {"fields": (("md5", "msgcode"),)},
        ),
    )
    actions = ["approve", "rehash"]

    def approve(self, request, queryset):
        queryset.update(draft=False)

    @link()
    def translate(self, button):
        return button

    @view()
    def get_or_create(self, request):
        if request.method == "POST":
            msgid = unquote(request.POST["msgid"])
            lang = request.POST["lang"]
            queryset = self.get_queryset(request)
            try:
                obj = queryset.get(msgid=msgid, locale=lang)
                self.message_user(request, "Found")
            except Message.DoesNotExist:
                obj = Message(msgid=msgid, locale=lang)
                obj.save()
                self.message_user(request, "Created", messages.WARNING)
            cl = reverse("admin:i18n_message_change", args=[obj.pk])
        else:
            cl = reverse("admin:i18n_message_changelist")

        return HttpResponseRedirect(cl)

    def rehash(self, request, queryset):
        for m in queryset.all():
            m.save()

    @button()
    def siblings(self, request, pk):
        obj = self.get_object(request, pk)
        cl = reverse("admin:i18n_message_changelist")
        return HttpResponseRedirect(f"{cl}?msgid__exact={obj.msgid}")

    @button()
    def create_translation(self, request):
        from smart_register.i18n.forms import TranslationForm
        from smart_register.i18n.models import Message

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
                    for msg in Message.objects.filter(locale=settings.LANGUAGE_CODE).order_by("msgid").distinct():
                        Message.objects.get_or_create(
                            msgid=msg.msgid,
                            locale=locale,
                            defaults={"md5": Message.get_md5(locale, msg.msgid), "draft": True},
                        )
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
        if obj:
            return ("msgid",) + self.readonly_fields
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
