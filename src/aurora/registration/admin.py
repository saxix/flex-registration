import json
import logging
from datetime import datetime, timedelta

from admin_extra_buttons.decorators import button, choice, link, view
from admin_sync.mixin import SyncMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.value import ValueFilter
from dateutil.utils import today
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import SimpleListFilter, register
from django.core.cache import cache
from django.db.models import JSONField
from django.db.models.signals import post_delete, post_save
from django.db.transaction import atomic
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import Template
from django.template.loader import select_template
from django.urls import reverse, translate_url
from django.utils.text import slugify
from django.utils.translation import gettext as _
from jsoneditor.forms import JSONEditor
from smart_admin.modeladmin import SmartModelAdmin

from .protocol import AuroraSyncRegistrationProtocol
from ..core.admin import ConcurrencyVersionAdmin
from ..core.models import FormSet
from ..core.utils import (
    build_form_fake_data,
    clone_model,
    get_system_cache_version,
    is_root,
    namify,
)
from ..i18n.forms import TemplateForm
from .forms import CloneForm, RegistrationForm
from .models import Record, Registration
from .paginator import LargeTablePaginator

logger = logging.getLogger(__name__)

DATA = {
    "registration.Registration": [],
    "core.FlexForm": [],
    "core.FormSet": [],
    "core.Validator": [],
    "core.OptionSet": [],
    "core.FlexFormField": [],
    "i18n.Message": [],
}


class JamesForm(forms.ModelForm):
    # unique_field = forms.CharField(widget=forms.HiddenInput)
    unique_field_path = forms.CharField(
        label="JMESPath expression", widget=forms.TextInput(attrs={"style": "width:90%"})
    )
    data = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Registration
        fields = ("unique_field_path", "data")

    class Media:
        js = [
            "https://cdnjs.cloudflare.com/ajax/libs/jmespath/0.16.0/jmespath.min.js",
        ]


@register(Registration)
class RegistrationAdmin(ConcurrencyVersionAdmin, SyncMixin, SmartModelAdmin):
    search_fields = ("name", "title", "slug")
    date_hierarchy = "start"
    list_filter = ("active", "archived")
    list_display = ("name", "title", "slug", "locale", "secure", "active", "validator", "archived", "is_pwa_enabled")
    exclude = ("public_key",)
    autocomplete_fields = ("flex_form",)
    save_as = True
    form = RegistrationForm
    readonly_fields = ("version", "last_update_date")
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
    change_form_template = None
    change_list_template = None
    filter_horizontal = ("scripts",)
    fieldsets = [
        (None, {"fields": (("version", "last_update_date", "active"),)}),
        (None, {"fields": ("name", "title", "slug")}),
        (
            "Unique",
            {
                "fields": (
                    "unique_field_path",
                    "unique_field_error",
                )
            },
        ),
        ("Config", {"fields": ("flex_form", "validator", "scripts")}),
        ("Validity", {"classes": ("collapse",), "fields": (("start", "end"), ("archived", "active"))}),
        ("Languages", {"classes": ("collapse",), "fields": ("locale", "locales")}),
        ("Security", {"classes": ("collapse",), "fields": ("protected", "restrict_to_groups")}),
        ("Text", {"classes": ("collapse",), "fields": ("intro", "footer")}),
        ("Advanced", {"fields": ("advanced",)}),
        ("Others", {"fields": ("__others__",)}),
    ]
    protocol_class = AuroraSyncRegistrationProtocol

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ["unique_field_path", "unique_field_error"]:
            formfield.widget.attrs = {"style": "width:80%"}
        return formfield

    def secure(self, obj):
        return bool(obj.public_key) or obj.encrypt_data

    secure.boolean = True

    def admin_sync_show_inspect(self):
        return True

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "/static/clipboard%s.js" % extra,
            ]
        )

    @view(label="invalidate cache", html_attrs={"class": "aeb-warn"})
    def invalidate_cache(self, request, pk):
        obj = self.get_object(request, pk)
        obj.save()

    @choice(order=900, visible=lambda c: [], change_list=False)
    def encryption(self, button):
        original = button.context["original"]
        colors = ["#DC6C6C", "white"]
        if original.public_key:
            colors = ["#dfd", "black"]
            button.choices = [self.removekey]
        elif original.encrypt_data:
            colors = ["#dfd", "black"]
            self.toggle_encryption.func._handler.config["label"] = "Disable Symmetric"
            button.choices = [self.toggle_encryption]
        else:
            self.toggle_encryption.func._handler.config["label"] = "Enable Symmetric"
            self.generate_keys.func._handler.config["label"] = "Enable RSA"
            button.choices = [self.generate_keys, self.toggle_encryption]
        button.config["html_attrs"] = {"style": f"background-color:{colors[0]};color:{colors[1]}"}
        return button

    @view(label="Symmetric Encryption")
    def toggle_encryption(self, request, pk):
        self.object = self.get_object(request, pk)
        self.object.encrypt_data = not self.object.encrypt_data
        self.object.save()

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

    @choice(order=900, change_list=False)
    def admin(self, button):
        button.choices = [
            self.james_editor,
            self.inspect,
            self.clone,
            self.create_translation,
            self.create_custom_template,
        ]
        return button

    @view()
    def inspect(self, request, pk):
        ctx = self.get_common_context(
            request,
            pk,
            media=self.media,
            title="Inspect Registration",
        )
        return render(request, "admin/registration/registration/inspect.html", ctx)

    @view()
    def clone(self, request, pk):
        ctx = self.get_common_context(
            request,
            pk,
            media=self.media,
            title="Clone Registration",
        )
        reg: Registration = ctx["original"]
        if request.method == "POST":
            form = CloneForm(request.POST)
            if form.is_valid():
                try:
                    for dip in [
                        "form_dip",
                        "field_dip",
                        "formset_dip",
                        "form_del_dip",
                        "field_del_dip",
                        "formset_del_dip",
                    ]:
                        post_save.disconnect(dispatch_uid=dip)
                        post_delete.disconnect(dispatch_uid=dip)

                    with atomic():
                        source = Registration.objects.get(id=reg.pk)
                        title = form.cleaned_data["title"]
                        reg, __ = clone_model(source, name=namify(title), title=title, version=1, slug=slugify(title))
                        if form.cleaned_data["deep"]:
                            main_form, __ = clone_model(
                                source.flex_form, name=f"{source.flex_form.name}-(clone: {reg.name})"
                            )
                            reg.flex_form = main_form
                            reg.save()
                            for fld in source.flex_form.fields.all():
                                clone_model(fld, flex_form=main_form)

                            formsets = FormSet.objects.filter(parent=source.flex_form)
                            forms = {}
                            for fs in formsets:
                                forms[fs.flex_form.pk] = fs.flex_form
                                forms[fs.parent.pk] = fs.parent

                            for frm in forms.values():
                                frm2, created = clone_model(frm, name=f"{frm.name}-(clone: {reg.name})")
                                forms[frm.pk] = frm2
                                for field in frm.fields.all():
                                    clone_model(field, name=field.name, flex_form=frm2)

                            for fs in formsets:
                                clone_model(fs, parent=forms[fs.parent.pk], flex_form=forms[fs.flex_form.pk])
                        return HttpResponseRedirect(reverse("admin:registration_registration_inspect", args=[reg.pk]))
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)

            else:
                ctx["form"] = form
        else:
            form = CloneForm()
            ctx["form"] = form
        return render(request, "admin/registration/registration/clone.html", ctx)

    @view()
    def create_custom_template(self, request, pk):
        ctx = self.get_common_context(
            request,
            pk,
            media=self.media,
            title="Create Custom Template",
        )
        if request.method == "POST":
            obj = ctx["original"]
            form = TemplateForm(request.POST)
            if form.is_valid():
                from dbtemplates.models import Template as DbTemplate

                lang = form.cleaned_data["locale"]
                source: Template = select_template(
                    [
                        f"registration/{obj.locale}/{obj.slug}.html",
                        f"registration/{obj.slug}.html",
                        "registration/register.html",
                    ]
                )
                if lang == "-":
                    name = f"registration/{obj.slug}.html"
                else:
                    name = f"{lang}/registration/{obj.slug}.html"
                if hasattr(source, "template"):
                    content = source.template.source
                    source_name = source.template.name
                else:
                    content = ""
                tpl, created = DbTemplate.objects.get_or_create(name=name, defaults={"content": content})
                ctx["custom_template"] = tpl
                ctx["created"] = created
                ctx["source"] = source_name

        else:
            ctx["form"] = TemplateForm()
        return render(request, "admin/registration/registration/create_template.html", ctx)

    @view()
    def create_translation(self, request, pk):
        from aurora.i18n.forms import TranslationForm
        from aurora.i18n.models import Message

        ctx = self.get_common_context(
            request,
            pk,
            media=self.media,
            title="Generate Translation",
        )
        instance: Registration = ctx["original"]
        if request.method == "POST":
            form = TranslationForm(request.POST)
            if form.is_valid():
                locale = form.cleaned_data["locale"]
                existing = Message.objects.filter(locale=locale).count()
                uri = reverse("register", args=[instance.slug, instance.version])
                uri = translate_url(uri, locale)
                from django.test import Client

                settings.ALLOWED_HOSTS.append("testserver")
                headers = {"HTTP_ACCEPT_LANGUAGE": "locale", "HTTP_I18N": "true"}
                try:
                    client = Client(**headers)
                    r1 = client.get(uri)
                    # uri = request.build_absolute_uri(reverse("register", args=[instance.slug]))
                    # uri = translate_url(uri, locale)
                    # r1 = requests.get(uri, headers={"Accept-Language": locale, "I18N": "true"})
                    if r1.status_code == 302:
                        # return HttpResponse(r1.content, status=r1.status_code)
                        raise Exception(f"GET: {uri} - {r1.status_code}: {r1.headers['location']}")
                    if r1.status_code != 200:
                        # return HttpResponse(r1.content, status=r1.status_code)
                        raise Exception(f"GET: {uri} - {r1.status_code}")
                    # r2 = requests.post(uri, {}, headers={"Accept-Language": locale, "I18N": "true"})
                    r2 = client.post(uri, {}, **headers)
                    if r2.status_code != 200:
                        # return HttpResponse(r2.content, status=r2.status_code)
                        raise Exception(f"POST: {uri} - {r2.status_code}")
                except Exception as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)

                updated = Message.objects.filter(locale=locale).count()
                added = Message.objects.filter(locale=locale, draft=True, timestamp__date=today())
                self.message_user(request, f"{updated - existing} messages created. {updated} available")
                ctx["uri"] = uri
                ctx["locale"] = locale
                ctx["added"] = added
            else:
                ctx["form"] = form
        else:
            form = TranslationForm()
            ctx["form"] = form
        return render(request, "admin/registration/registration/translation.html", ctx)

    @button(change_form=True, html_attrs={"target": "_new"})
    def charts(self, request, pk):
        return HttpResponseRedirect(reverse("charts:registration", args=[pk]))

    @link(permission=is_root, html_attrs={"class": "aeb-warn"})
    def view_collected_data(self, button):
        try:
            if button.original:
                base = reverse("admin:registration_record_changelist")
                button.href = f"{base}?registration__exact={button.original.pk}"
                button.html_attrs["target"] = f"_{button.original.pk}"
        except Exception as e:
            logger.exception(e)

    @view()
    def james_fake_data(self, request, pk):
        reg = self.get_object(request, pk)
        data = cache.get(f"james_{pk}", version=get_system_cache_version())
        if not data:
            form_class = reg.flex_form.get_form_class()
            data = json.dumps(build_form_fake_data(form_class), indent=4)
            cache.set(f"james_{pk}", data, version=get_system_cache_version())

        return HttpResponse(data)

    @view()
    def james_editor(self, request, pk):
        ctx = self.get_common_context(request, pk, title="JAMESPath Editor")
        if request.method == "POST":
            form = JamesForm(request.POST, instance=ctx["original"])
            if form.is_valid():
                form.save()
                cache.set(f"james_{pk}", form.cleaned_data["data"], version=get_system_cache_version())
                return HttpResponseRedirect(".")
        else:
            data = cache.get(f"james_{pk}", version=get_system_cache_version())
            form = JamesForm(instance=ctx["original"], initial={"data": data})
        ctx["form"] = form
        return render(request, "admin/registration/registration/james_editor.html", ctx)

    @button(visible=False)
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Test")
        form = self.object.flex_form.get_form_class()
        ctx["registration"] = self.object
        ctx["form"] = form
        return render(request, "admin/registration/registration/test.html", ctx)

    def get_changeform_buttons(self, context):
        return sorted(
            [h for h in self.extra_button_handlers.values() if h.change_form in [True, None]],
            key=lambda item: item.config.get("order", 1),
        )

    def get_changelist_buttons(self, context):
        return sorted(
            [h for h in self.extra_button_handlers.values() if h.change_list in [True, None]],
            key=lambda item: item.config.get("order", 1),
        )


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
            offset = datetime.now() - timedelta(minutes=int(self.value()))
            queryset = queryset.filter(timestamp__gte=offset)

        return queryset


@register(Record)
class RecordAdmin(SmartModelAdmin):
    date_hierarchy = "timestamp"
    search_fields = ("registration__name",)
    list_display = ("timestamp", "remote_ip", "id", "registration", "ignored", "unique_field")
    readonly_fields = ("registration", "timestamp", "remote_ip", "id", "fields", "counters")
    autocomplete_fields = ("registration",)
    list_filter = (("registration", AutoCompleteFilter), HourFilter, ("unique_field", ValueFilter), "ignored")
    change_form_template = None
    change_list_template = None
    actions = ["fix_tax_id"]
    paginator = LargeTablePaginator
    show_full_result_count = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("registration")
        return qs

    def get_common_context(self, request, pk=None, **kwargs):
        return super().get_common_context(request, pk, is_root=is_root(request), **kwargs)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = {"is_root": is_root(request)}
        return super().changeform_view(request, object_id, form_url, extra_context)

    def fix_tax_id(self, request, queryset):
        results = {"updated": [], "processed": []}
        for record in queryset:
            try:
                for individual in record.fields["individuals"]:
                    if individual["role_i_c"] == "y":
                        record.unique_field = individual["tax_id_no_i_c"]
                        record.save()
                        results["updated"].append(record.pk)
                        break
                results["processed"].append(record.pk)

            except Exception as e:
                results[record.pk] = f"{e.__class__.__name__}: {str(e)}"
        return JsonResponse(results)

    @button(label="Fix TaxID")
    def _fix_tax_id(self, request):
        queryset = Record.objects.filter(unique_field__isnull=True, timestamp__gt="2022-06-15")
        return self.fix_tax_id(request, queryset)

    @link(html_attrs={"class": "aeb-warn "}, change_form=True)
    def receipt(self, button):
        try:
            if button.original:
                base = reverse("register-done", args=[button.original.registration.pk, button.original.pk])
                button.href = base
                button.html_attrs["target"] = f"_{button.original.pk}"
        except Exception as e:
            logger.exception(e)

    @button(label="Preview", permission=is_root)
    def preview(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Preview")

        return render(request, "admin/registration/record/preview.html", ctx)

    @button(label="inspect", permission=is_root)
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Inspect")
        ctx["files_as_dict"] = json.loads(self.object.files.tobytes().decode())
        return render(request, "admin/registration/record/inspect.html", ctx)

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

    def get_readonly_fields(self, request, obj=None):
        if is_root(request) or settings.DEBUG:
            return []
        return self.readonly_fields

    def has_view_permission(self, request, obj=None):
        return is_root(request) or settings.DEBUG

    def has_add_permission(self, request):
        return is_root(request) or settings.DEBUG

    def has_delete_permission(self, request, obj=None):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return is_root(request) or settings.DEBUG
