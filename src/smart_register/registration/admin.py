import logging
from collections import defaultdict
from datetime import datetime

from admin_extra_buttons.decorators import button, link, view
from adminfilters.autocomplete import AutoCompleteFilter
from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import SimpleListFilter, register
from django.db.models import Count, JSONField
from django.db.models.functions import ExtractHour, TruncDay
from django.db.transaction import atomic
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import ImportExportMixin
from jsoneditor.forms import JSONEditor
from smart_admin.modeladmin import SmartModelAdmin

from ..core.utils import clone_form, clone_model, is_root
from .forms import CloneForm
from .models import Record, Registration

logger = logging.getLogger(__name__)


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration


def last_day_of_month(date):
    return date.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)


@register(Registration)
class RegistrationAdmin(ImportExportMixin, SmartModelAdmin):
    search_fields = ("name", "title", "slug")
    date_hierarchy = "start"
    list_filter = ("active",)
    list_display = ("name", "title", "slug", "locale", "secure", "active", "validator")
    exclude = ("public_key",)
    change_form_template = None
    autocomplete_fields = ("flex_form",)
    save_as = True
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }

    def secure(self, obj):
        return bool(obj.public_key)

    secure.boolean = True

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "/static/clipboard%s.js" % extra,
            ]
        )

    @view()
    def data(self, request, registration):
        qs = Record.objects.filter(registration_id=registration)
        param_day = request.GET.get("d", None)
        if param_day:
            day = datetime.strptime(param_day, "%Y-%m-%d")
            qs = qs.filter(timestamp__date=day)
            qs = qs.annotate(hour=ExtractHour("timestamp")).values("hour").annotate(c=Count("id"))
            data = defaultdict(lambda: 0)
            for record in qs.all():
                data[record["hour"]] = record["c"]
            hours = list(range(0, 24))
            data = {
                "label": day.strftime("%A, %d %B"),
                "day": day.strftime("%Y-%m-%d"),
                "labels": hours,
                "data": [data[x] for x in hours],
            }
        else:
            param_month = request.GET.get("m", None)
            if param_month:
                day = datetime.strptime(param_month, "%Y-%m-%d")
            else:
                day = timezone.now().today()
            qs = qs.filter(timestamp__month=day.month)
            qs = qs.annotate(day=TruncDay("timestamp")).values("day").annotate(c=Count("id"))
            data = defaultdict(lambda: 0)
            for record in qs.all():
                data[record["day"].day] = record["c"]
            last_day = last_day_of_month(day)
            days = list(range(1, 1 + last_day.day))
            data = {
                "label": day.strftime("%B"),
                "day": day.strftime("%Y-%m-%d"),
                "labels": days,
                "data": [data[x] for x in days],
            }

        response = JsonResponse(data)
        response["Cache-Control"] = f"max-age={60 * 60 * 24}"
        return response

    @button(label="Chart")
    def chart(self, request, pk):
        ctx = self.get_common_context(request, pk, title="chart")
        ctx["today"] = datetime.now().strftime("%Y-%m-%d")
        return render(request, "admin/registration/registration/chart.html", ctx)

    @button()
    def create_translation(self, request, pk):
        ctx = self.get_common_context(
            request,
            pk,
            media=self.media,
            title="Generate Translation",
        )
        instance: Registration = ctx["original"]
        if request.method == "POST":
            form = CloneForm(request.POST, instance=instance)
            if form.is_valid():
                try:
                    with atomic():
                        created = []
                        locale = form.cleaned_data["locale"]
                        base_form = instance.flex_form
                        cloned = clone_form(base_form, name=f"{base_form.name} {locale}")
                        for fs in base_form.formsets.all():
                            o = clone_form(fs.flex_form, name=f"{fs.flex_form.name} {locale}")
                            fs = clone_model(
                                fs,
                                parent=cloned,
                                flex_form=o,
                            )

                        reg = clone_model(
                            instance,
                            name=f"{instance.name} {locale}",
                            flex_form=cloned,
                            active=False,
                            locale=locale,
                            public_key=None,
                        )
                        created.append(fs)

                        ctx["cloned"] = reg
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)

            else:
                self.message_user(request, "----")
                ctx["form"] = form
        else:
            form = CloneForm(instance=ctx["original"])
            ctx["form"] = form
        return render(request, "admin/registration/registration/clone.html", ctx)

    @link(html_attrs={"class": "aeb-green "})
    def _view_on_site(self, button):
        try:
            if button.original:
                button.href = reverse("register", args=[button.original.locale, button.original.slug])
                button.html_attrs["target"] = f"_{button.original.slug}"
        except Exception as e:
            logger.exception(e)

    @link(permission=is_root, html_attrs={"class": "aeb-warn "})
    def view_collected_data(self, button):
        try:
            if button.original:
                base = reverse("admin:registration_record_changelist")
                button.href = f"{base}?registration__exact={button.original.pk}"
                button.html_attrs["target"] = f"_{button.original.pk}"
        except Exception as e:
            logger.exception(e)

    @view()
    def removekey(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Remove Encryption Key")
        if request.method == "POST":
            self.object = self.get_object(request, pk)
            self.object.public_key = ""
            self.object.save()
            self.message_user(request, "Encryption key removed", messages.WARNING)
            self.log_change(request, self.object, "Encryption Key has been removed")
            return HttpResponseRedirect("..")
        else:
            return render(request, "admin/registration/registration/keys_remove.html", ctx)

    @view()
    def generate_keys(self, request, pk):
        ctx = self.get_common_context(
            request, pk, media=self.media, title="Generate Private/Public Key pair to encrypt this Registration data"
        )

        if request.method == "POST":
            ctx["title"] = "Key Pair Generated"
            private_pem, public_pem = self.object.setup_encryption_keys()
            ctx["private_key"] = private_pem
            ctx["public_key"] = public_pem
            self.log_change(request, self.object, "Encryption Keys have been generated")

        return render(request, "admin/registration/registration/keys.html", ctx)


class DecryptForm(forms.Form):
    key = forms.CharField(widget=forms.Textarea)


class HourFilter(SimpleListFilter):
    parameter_name = "hours"
    title = "Latest [n] hours"
    slots = (
        (30, _("30 min")),
        (60, _("1 hour")),
        (60 * 4, _("4 hour")),
        (60 * 6, _("6 hour")),
        (60 * 8, _("8 hour")),
        (60 * 12, _("12 hour")),
        (60 * 24, _("24 hour")),
    )

    def lookups(self, request, model_admin):
        return self.slots

    def queryset(self, request, queryset):
        if self.value():
            offset = datetime.datetime.now() - datetime.timedelta(minutes=int(self.value()))
            queryset = queryset.filter(timestamp__gte=offset)

        return queryset


@register(Record)
class RecordAdmin(SmartModelAdmin):
    date_hierarchy = "timestamp"
    search_fields = ("registration__name",)
    list_display = ("timestamp", "id", "registration", "ignored")
    readonly_fields = ("registration", "timestamp", "id")
    list_filter = (("registration", AutoCompleteFilter), HourFilter, "ignored")
    change_form_template = None
    change_list_template = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("registration")
        return qs

    def get_common_context(self, request, pk=None, **kwargs):
        return super().get_common_context(request, pk, is_root=is_root(request), **kwargs)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = {"is_root": is_root(request)}
        return super().changeform_view(request, object_id, form_url, extra_context)

    @button(label="Preview", permission=is_root)
    def preview(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Preview")
        return render(request, "admin/registration/record/preview.html", ctx)

    @button(permission=is_root)
    def decrypt(self, request, pk):
        ctx = self.get_common_context(request, pk, title="To decrypt you need to provide Registration Private Key")
        if request.method == "POST":
            form = DecryptForm(request.POST)
            ctx["title"] = "Data have been decrypted only to be showed on this page. Still encrypted on the DB"
            if form.is_valid():
                key = form.cleaned_data["key"]
                try:
                    ctx["decrypted"] = self.object.decrypt(key)
                except Exception as e:
                    ctx["title"] = "Error decrypting data"
                    self.message_error_to_user(request, e)
        else:
            form = DecryptForm()

        ctx["form"] = form
        return render(request, "admin/registration/record/decrypt.html", ctx)

    def has_view_permission(self, request, obj=None):
        return is_root(request) or settings.DEBUG

    def has_add_permission(self, request):
        return is_root(request) or settings.DEBUG

    def has_delete_permission(self, request, obj=None):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return is_root(request) or settings.DEBUG
