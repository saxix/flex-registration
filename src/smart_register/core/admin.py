import io
import json
import logging
import tempfile
from json import JSONDecodeError
from pathlib import Path

import requests
from admin_extra_buttons.decorators import button, link, view
from admin_ordering.admin import OrderableAdmin
from adminfilters.autocomplete import AutoCompleteFilter
from concurrency.api import disable_concurrency
from django import forms
from django.conf import settings
from django.contrib.admin import TabularInline, register
from django.core.management import call_command
from django.core.signing import Signer, BadSignature
from django.db.models import JSONField
from django.http import JsonResponse
from django.urls import reverse
from jsoneditor.forms import JSONEditor
from requests.auth import HTTPBasicAuth
from smart_admin.modeladmin import SmartModelAdmin

from .forms import ValidatorForm
from .models import (
    CustomFieldType,
    FlexForm,
    FlexFormField,
    FormSet,
    OptionSet,
    Validator,
)
from .utils import render

logger = logging.getLogger(__name__)


@register(Validator)
class ValidatorAdmin(SmartModelAdmin):
    form = ValidatorForm


@register(FormSet)
class FormSetAdmin(SmartModelAdmin):
    list_display = ("name", "title", "parent", "flex_form", "extra", "max_num", "min_num")
    search_fields = ("name", "title")
    list_filter = (
        ("parent", AutoCompleteFilter),
        ("flex_form", AutoCompleteFilter),
    )


FLEX_FIELD_DEFAULT_ATTRS = {
    "smart": {"hint": "", "visible": False, "onchange": "", "description": ""},
}


class FormSetInline(OrderableAdmin, TabularInline):
    model = FormSet
    fk_name = "parent"
    extra = 0
    fields = ("name", "flex_form", "extra", "max_num", "min_num", "ordering")
    show_change_link = True
    ordering_field = "ordering"
    ordering_field_hide_input = True

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@register(FlexFormField)
class FlexFormFieldAdmin(OrderableAdmin, SmartModelAdmin):
    list_display = ("ordering", "flex_form", "name", "field_type", "required", "validator")
    list_filter = (("flex_form", AutoCompleteFilter),)
    list_editable = ["ordering"]

    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }
    ordering_field = "ordering"
    order = "ordering"

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("advanced", FLEX_FIELD_DEFAULT_ATTRS)
        return initial

    @button()
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk)
        try:
            fld = ctx["original"]
            instance = fld.get_instance()
            ctx["debug_info"] = {
                "instance": instance,
                "kwargs": fld.advanced,
                "options": getattr(instance, "options", None),
                "choices": getattr(instance, "choices", None),
                "widget": getattr(instance, "widget", None),
            }
            form_class_attrs = {
                "sample": instance,
            }
            formClass = type(forms.Form)("TestForm", (forms.Form,), form_class_attrs)

            if request.method == "POST":
                form = formClass(request.POST)
                if form.is_valid():
                    self.message_user(
                        request, f"Form validation success. " f"You have selected: {form.cleaned_data['sample']}"
                    )
            else:
                form = formClass()
            ctx["form"] = form
        except Exception as e:
            logger.exception(e)
            ctx["error"] = e

        return render(request, "admin/core/flexformfield/test.html", ctx)


class FlexFormFieldForm(forms.ModelForm):
    class Meta:
        model = FlexFormField
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if self.instance and self.instance.pk:
        self.fields["name"].widget.attrs = {"readonly": True, "style": "background-color:#f8f8f8;border:none"}


class FlexFormFieldInline(OrderableAdmin, TabularInline):
    model = FlexFormField
    form = FlexFormFieldForm
    fields = ("ordering", "label", "name", "field_type", "required", "validator")
    show_change_link = True
    extra = 0
    ordering_field = "ordering"
    ordering_field_hide_input = True


class SyncForm(forms.Form):
    APPS = ("core", "registration")
    host = forms.URLField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    apps = forms.MultipleChoiceField(choices=zip(APPS, APPS), widget=forms.CheckboxSelectMultiple())
    remember = forms.BooleanField(label="Remember me", required=False)


@register(FlexForm)
class FlexFormAdmin(SmartModelAdmin):
    SYNC_COOKIE = "sync"
    list_display = ("name", "validator", "used_by", "childs", "parents")
    search_fields = ("name",)
    inlines = [FlexFormFieldInline, FormSetInline]
    save_as = True

    def used_by(self, obj):
        return ", ".join(obj.registration_set.values_list("name", flat=True))

    def childs(self, obj):
        return ", ".join(obj.formsets.values_list("name", flat=True))

    def parents(self, obj):
        return ", ".join(obj.formset_set.values_list("parent__name", flat=True))

    @view(http_basic_auth=True, permission=lambda request, obj: request.user.is_superuser)
    def export(self, request):
        try:
            apps = request.GET.get("apps", "").split(",")
            buf = io.StringIO()
            call_command("dumpdata", *apps, stdout=buf, use_natural_foreign_keys=True, use_natural_primary_keys=True)
            return JsonResponse(json.loads(buf.getvalue()), safe=False)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({}, status=400)

    def _get_signed_cookie(self, request, form):
        signer = Signer(request.user.password)
        return signer.sign_object(form.cleaned_data)

    def _get_saved_credentials(self, request):
        try:
            signer = Signer(request.user.password)
            obj: dict = signer.unsign_object(request.COOKIES.get(self.SYNC_COOKIE, {}))
            return obj
        except BadSignature:
            return {}

    @button(label="Import")
    def _import(self, request):
        ctx = self.get_common_context(request, title="Import")
        cookies = {}
        if request.method == "POST":
            form = SyncForm(request.POST)
            if form.is_valid():
                try:
                    auth = HTTPBasicAuth(form.cleaned_data["username"], form.cleaned_data["password"])
                    if form.cleaned_data["remember"]:
                        cookies = {self.SYNC_COOKIE: self._get_signed_cookie(request, form)}
                    else:
                        cookies = {self.SYNC_COOKIE: ""}
                    url = f"{form.cleaned_data['host']}core/flexform/export/?apps={','.join(form.cleaned_data['apps'])}"
                    workdir = Path(".").absolute()
                    out = io.StringIO()
                    with requests.get(url, stream=True, auth=auth) as res:
                        if res.status_code != 200:
                            raise Exception(res.status_code)
                        ctx["url"] = url
                        with tempfile.NamedTemporaryFile(
                            dir=workdir, prefix="~SYNC", suffix=".json", delete=not settings.DEBUG
                        ) as fdst:
                            fdst.write(res.content)
                            with disable_concurrency():
                                fixture = (workdir / fdst.name).absolute()
                                call_command("loaddata", fixture, stdout=out, verbosity=3)
                            message = out.getvalue()
                            self.message_user(request, message)
                    ctx["res"] = res
                except (Exception, JSONDecodeError) as e:
                    logger.exception(e)
                    self.message_error_to_user(request, e)
        else:
            form = SyncForm(initial=self._get_saved_credentials(request))
        ctx["form"] = form
        return render(request, "admin/core/flexform/import.html", ctx, cookies=cookies)


@register(OptionSet)
class OptionSetAdmin(SmartModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "id", "separator", "columns")
    save_as = True

    @link(change_form=True, change_list=False, html_attrs={"target": "_new"})
    def view_json(self, button):
        original = button.context["original"]
        if original:
            url = reverse("optionset", args=[original.name])
            button.href = url

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if request.method == "POST" and "_saveasnew" in request.POST:
            object_id = None

        return super().change_view(request, object_id)


@register(CustomFieldType)
class CustomFieldTypeAdmin(SmartModelAdmin):
    list_display = (
        "name",
        "base_type",
        "attrs",
    )
    search_fields = ("name",)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }

    @button()
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk)
        fld = ctx["original"]
        field_type = fld.base_type
        kwargs = fld.attrs.copy()
        field = field_type(**kwargs)
        form_class_attrs = {
            "sample": field,
        }
        formClass = type(forms.Form)("TestForm", (forms.Form,), form_class_attrs)

        if request.method == "POST":
            form = formClass(request.POST)
            if form.is_valid():
                self.message_user(
                    request, f"Form validation success. " f"You have selected: {form.cleaned_data['sample']}"
                )
        else:
            form = formClass()
        ctx["form"] = form
        return render(request, "admin/core/customfieldtype/test.html", ctx)
