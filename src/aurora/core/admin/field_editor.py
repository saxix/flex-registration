import json
from django.conf import settings
from typing import Dict

from django import forms
from django.core.cache import caches
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import Context, Template
from django.utils.functional import cached_property

from aurora.core.fields.widgets import JavascriptEditor
from aurora.core.forms import VersionMedia, FlexFormBaseForm
from aurora.core.models import FlexFormField, OptionSet
from aurora.core.utils import merge_data

cache = caches["default"]


class AdvancendAttrsMixin:
    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop("field", None)
        self.prefix = kwargs.get("prefix")
        if self.field:
            kwargs["initial"] = self.field.advanced.get(self.prefix, {})
        super().__init__(*args, **kwargs)


class FlexFieldAttributesForm(AdvancendAttrsMixin, forms.ModelForm):
    required = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    enabled = forms.BooleanField(widget=forms.CheckboxInput, required=False)
    # onchange = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)

    def __init__(self, *args, **kwargs):
        kwargs["instance"] = kwargs["field"]
        super().__init__(*args, **kwargs)

    class Meta:
        model = FlexFormField
        fields = ("field_type", "label", "required", "enabled", "validator", "regex", "validation")


class FormFieldAttributesForm(AdvancendAttrsMixin, forms.Form):
    default_value = forms.CharField(required=False, help_text="default value for the field")


class WidgetAttributesForm(AdvancendAttrsMixin, forms.Form):
    placeholder = forms.CharField(required=False, help_text="placeholder for the input")
    css_class = forms.CharField(label="Field class", required=False, help_text="Input CSS class to apply (will")
    extra_classes = forms.CharField(required=False, help_text="Input CSS classes to add input")
    fieldset = forms.CharField(label="Fieldset class", required=False, help_text="Fieldset CSS class to apply")
    # onchange = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    # onblur = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    # onkeyup = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)


def get_datasources():
    v = OptionSet.objects.order_by("name").values_list("name", flat=True)
    return [("", "")] + list(zip(v, v))


class SmartAttributesForm(AdvancendAttrsMixin, forms.Form):
    question = forms.CharField(required=False, help_text="If set, user must check related box to display the field")
    question_onchange = forms.CharField(
        widget=forms.Textarea, required=False, help_text="Js to tigger on 'question' check/uncheck "
    )
    hint = forms.CharField(required=False, help_text="Text to display above the input")
    description = forms.CharField(required=False, help_text="Text to display below the input")
    datasource = forms.ChoiceField(choices=get_datasources, required=False, help_text="Datasource name for ajax field")
    parent_datasource = forms.ChoiceField(
        choices=get_datasources, required=False, help_text="Parent Datasource name for ajax field"
    )
    choices = forms.JSONField(required=False)
    # onchange = forms.CharField(widget=forms.Textarea, required=False, help_text="Javascript onchange event")
    # onblur = forms.CharField(widget=forms.Textarea, required=False, help_text="Javascript onblur event")
    visible = forms.BooleanField(required=False, help_text="Hide/Show field")


class CssForm(AdvancendAttrsMixin, forms.Form):
    input = forms.CharField(required=False, help_text="")
    label = forms.CharField(required=False, help_text="")
    fieldset = forms.CharField(required=False, help_text="")
    question = forms.CharField(required=False, help_text="")


class EventForm(AdvancendAttrsMixin, forms.Form):
    onchange = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    onblur = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    onkeyup = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    onload = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    onfocus = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)

    validation = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)
    init = forms.CharField(widget=JavascriptEditor(toolbar=True), required=False)


DEFAULTS = {
    "css": {"question": "cursor-pointer", "label": "block uppercase tracking-wide text-gray-700 font-bold mb-2"},
}


def get_initial(field, prefix):
    base = DEFAULTS.get(prefix, {})
    for k, v in field.advanced.get(prefix, {}).items():
        if v:
            base[k] = v
    return base


class FieldEditor:
    FORMS = {
        "field": FlexFieldAttributesForm,
        "kwargs": FormFieldAttributesForm,
        "widget": WidgetAttributesForm,
        "smart": SmartAttributesForm,
        "css": CssForm,
        "events": EventForm,
    }

    def __init__(self, modeladmin, request, pk):
        self.modeladmin = modeladmin
        self.request = request
        self.pk = pk
        self.cache_key = f"/editor/field/{self.request.user.pk}/{self.pk}/"

    @cached_property
    def field(self):
        return FlexFormField.objects.get(pk=self.pk)

    @cached_property
    def patched_field(self):
        fld = self.field
        if config := cache.get(self.cache_key, None):
            forms = self.get_forms(config)
            fieldForm = forms.pop("field", None)
            if fieldForm.is_valid():
                for k, v in fieldForm.cleaned_data.items():
                    setattr(fld, k, v)
            for prefix, frm in forms.items():
                frm.is_valid()
                merged = merge_data(fld.advanced, {**{prefix: frm.cleaned_data}})
                fld.advanced = merged
        return fld

    def patch(self, request, pk):
        pass

    def get_configuration(self):
        self.patched_field.get_instance()
        rendered = json.dumps(self.field.advanced, indent=4)
        return HttpResponse(rendered, content_type="text/plain")

    def get_code(self):
        from bs4 import BeautifulSoup as bs
        from bs4 import formatter
        from pygments import highlight
        from pygments.formatters.html import HtmlFormatter
        from pygments.lexers import HtmlLexer

        instance = self.patched_field.get_instance()
        form_class_attrs = {
            self.field.name: instance,
        }
        form_class = type(forms.Form)("TestForm", (forms.Form,), form_class_attrs)
        ctx = self.get_context(self.request)
        ctx["form"] = form_class()
        ctx["instance"] = instance
        code = Template(
            "{% for field in form %}{% spaceless %}"
            '{% include "smart/_fieldset.html" %}{% endspaceless %}{% endfor %}'
        ).render(Context(ctx))
        formatter = formatter.HTMLFormatter(indent=2)
        soup = bs(code)
        prettyHTML = soup.prettify(formatter=formatter)

        formatter = HtmlFormatter(style="default", full=True)
        ctx["code"] = highlight(prettyHTML, HtmlLexer(), formatter)
        return render(self.request, "admin/core/flexformfield/field_editor/code.html", ctx, content_type="text/html")

    def render(self):
        instance = self.patched_field.get_instance()
        form_class_attrs = {
            self.field.name: instance,
        }
        form_class = type(FlexFormBaseForm)("TestForm", (FlexFormBaseForm,), form_class_attrs)
        ctx = self.get_context(self.request)
        if self.request.method == "POST":
            form = form_class(self.request.POST)
            ctx["valid"] = form.is_valid()
        else:
            form = form_class(initial={self.field.name: self.patched_field.get_default_value()})
            ctx["valid"] = None

        ctx["form"] = form
        ctx["instance"] = instance

        return render(self.request, "admin/core/flexformfield/field_editor/preview.html", ctx)

    def get_forms(self, data=None) -> Dict:
        if data:
            return {prefix: Form(data, prefix=prefix, field=self.field) for prefix, Form in self.FORMS.items()}
        if self.request.method == "POST":
            return {
                prefix: Form(
                    self.request.POST, prefix=prefix, field=self.field, initial=get_initial(self.field, prefix)
                )
                for prefix, Form in self.FORMS.items()
            }
        return {
            prefix: Form(prefix=prefix, field=self.field, initial=get_initial(self.field, prefix))
            for prefix, Form in self.FORMS.items()
        }

    def refresh(self):
        forms = self.get_forms()
        if all(map(lambda f: f.is_valid(), forms.values())):
            data = self.request.POST.dict()
            data.pop("csrfmiddlewaretoken")
            cache.set(self.cache_key, data)
        else:
            return JsonResponse({prefix: frm.errors for prefix, frm in forms.items()}, status=400)
        return JsonResponse(data)

    def get_context(self, request, pk=None, **kwargs):
        return {
            **self.modeladmin.get_common_context(request, pk),
            **kwargs,
        }

    def get(self, request, pk):
        ctx = self.get_context(request, pk)
        extra = "" if settings.DEBUG else ".min"
        ctx["media"] = VersionMedia(
            js=[
                "admin/js/vendor/jquery/jquery%s.js" % extra,
                "admin/js/jquery.init%s.js" % extra,
                "jquery.compat%s.js" % extra,
                "smart_validation%s.js" % extra,
                "smart%s.js" % extra,
                "smart_field%s.js" % extra,
            ]
        )
        for prefix, frm in self.get_forms().items():
            ctx[f"form_{prefix}"] = frm
            ctx["media"] += frm.media
        return render(request, "admin/core/flexformfield/field_editor/main.html", ctx)

    def post(self, request, pk):
        forms = self.get_forms()
        if all(map(lambda f: f.is_valid(), forms.values())):
            self.patched_field.save()
            return HttpResponseRedirect(".")
