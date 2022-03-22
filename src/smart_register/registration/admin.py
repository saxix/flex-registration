import logging

from admin_extra_buttons.decorators import button, link, view
from adminfilters.autocomplete import AutoCompleteFilter
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import register
from django.db.models import JSONField
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportMixin
from jsoneditor.forms import JSONEditor
from smart_admin.modeladmin import SmartModelAdmin

from .forms import CloneForm
from ..core.utils import is_root, clone_model, clone_form
from .models import Record, Registration

logger = logging.getLogger(__name__)


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration


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

    @link(html_attrs={"class": "aeb-warn "})
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


@register(Record)
class RecordAdmin(SmartModelAdmin):
    date_hierarchy = "timestamp"
    search_fields = ("registration__name",)
    list_display = (
        "timestamp",
        "id",
        "registration",
    )
    readonly_fields = ("registration", "timestamp", "id")
    list_filter = (("registration", AutoCompleteFilter),)
    change_form_template = None

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

    def has_add_permission(self, request):
        return is_root(request) or settings.DEBUG

    def has_delete_permission(self, request, obj=None):
        return is_root(request) or settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return is_root(request) or settings.DEBUG
