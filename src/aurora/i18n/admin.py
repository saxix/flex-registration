import logging
from unittest.mock import Mock
from urllib.parse import unquote

from admin_extra_buttons.decorators import button, view
from adminfilters.combo import ChoicesFieldComboFilter
from adminfilters.value import ValueFilter
from dateutil.utils import today
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import register
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import translation
from django.utils.translation import get_language
from smart_admin.modeladmin import SmartModelAdmin

from ..admin.mixin import LoadDumpMixin
from ..core.models import FlexForm
from ..publish.mixin import PublishMixin
from ..state import state
from .engine import translator
from .forms import TranslationForm
from .models import Message

logger = logging.getLogger(__name__)


@register(Message)
class MessageAdmin(PublishMixin, LoadDumpMixin, SmartModelAdmin):
    search_fields = ("msgid__icontains",)
    list_display = ("id", "msgid", "locale", "msgstr", "draft", "used")
    list_editable = ("draft",)
    readonly_fields = ("md5", "msgcode")
    list_filter = (
        "draft",
        "used",
        ("locale", ChoicesFieldComboFilter),
        ("msgid", ValueFilter),
        ("msgstr", ValueFilter),
        ("msgcode", ValueFilter),
        ("md5", ValueFilter),
        "last_hit",
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
            {"fields": (("draft", "auto", "used"),)},
        ),
        (
            None,
            {"fields": (("md5", "msgcode"),)},
        ),
    )
    actions = ["approve", "rehash"]

    def approve(self, request, queryset):
        queryset.update(draft=False)

    @button()
    def check_orphans(self, request):
        ctx = self.get_common_context(request, media=self.media, title="Check Orphans", pre={}, post={})
        if request.method == "POST":
            form = TranslationForm(request.POST)
            locale = get_language()
            if form.is_valid():
                lang = form.cleaned_data["locale"]
                translator.activate(lang)
                translation.activate(lang)
                translator[lang].reset()
                ctx["pre"]["total_messages"] = Message.objects.all().count()
                ctx["pre"]["used"] = Message.objects.filter(used=True).count()
                ctx["pre"]["unused"] = Message.objects.filter(used=False).count()
                Message.objects.update(last_hit=None, used=False)
                try:
                    state.collect_messages = True
                    state.hit_messages = True
                    for flex_form in FlexForm.objects.all():
                        frm_cls = flex_form.get_form_class()
                        for frm in [frm_cls(), frm_cls({})]:
                            loader.render_to_string(
                                "smart/_form.html",
                                {
                                    "form": frm,
                                    "formsets": flex_form.get_formsets({}),
                                    "request": Mock(selected_language=lang),
                                },
                            )
                except Exception as e:
                    logger.exception(e)
                finally:
                    ctx["post"]["total_messages"] = Message.objects.all().count()
                    ctx["post"]["used"] = Message.objects.filter(used=True).count()
                    ctx["post"]["unused"] = Message.objects.filter(used=False).count()
                    translator.activate(locale)
                    translation.activate(locale)
                    state.collect_messages = False
                    state.hit_messages = False
                    # return render(request, "admin/i18n/message/check_orphans.html", ctx)
        else:
            form = TranslationForm()
            ctx["form"] = form
        return render(request, "admin/i18n/message/check_orphans.html", ctx)

    # @link()
    # def translate(self, button):
    #     return button

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

    @button(label="Create Translation")
    def create_translation_single(self, request, pk):
        ctx = self.get_common_context(
            request,
            pk,
            media=self.media,
            title="Generate Translation",
        )
        if request.method == "POST":
            form = TranslationForm(request.POST)
            if form.is_valid():
                locale = form.cleaned_data["locale"]
                original = ctx["original"]
                try:
                    msg, created = Message.objects.get_or_create(
                        msgid=original.msgid,
                        locale=locale,
                        defaults={"md5": Message.get_md5(locale, original.msgid), "draft": True},
                    )
                    if created:
                        self.message_user(request, "Message created.")
                    else:
                        self.message_user(request, "Message found.", messages.WARNING)

                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)
                return HttpResponseRedirect(reverse("admin:i18n_message_change", args=[msg.pk]))
            else:
                ctx["form"] = form
        else:
            form = TranslationForm()
            ctx["form"] = form
        return render(request, "admin/i18n/message/translation.html", ctx)

    @button()
    def create_translation(self, request):
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
