from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.functional import cached_property

from aurora.core.models import FlexFormField


class AdvancendAttrsMixin:
    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop("field", None)
        self.prefix = kwargs.get("prefix")
        kwargs["initial"] = self.field.advanced.get(self.prefix, {})
        super().__init__(*args, **kwargs)


class FlexFieldAttributesForm(AdvancendAttrsMixin, forms.ModelForm):
    required = forms.ChoiceField(widget=forms.CheckboxInput, required=False, choices=[("y", "Yes"), ("n", "No")])

    class Meta:
        model = FlexFormField
        fields = ("field_type", "label", "name", "choices", "required", "validator", "regex")


class FormFieldAttributesForm(AdvancendAttrsMixin, forms.Form):
    default_value = forms.CharField(required=False, help_text="default value for the field")


class WidgetAttributesForm(AdvancendAttrsMixin, forms.Form):
    placeholder = forms.CharField(required=False, help_text="placeholder for the input")
    class_ = forms.CharField(label="Field class", required=False, help_text="Input CSS class to apply (will")
    extra_classes = forms.CharField(required=False, help_text="Input CSS classes to add input")
    fieldset = forms.CharField(label="Fieldset class", required=False, help_text="Fieldset CSS class to apply")
    onchange = forms.CharField(required=False, help_text="Javascfipt onchange event")


class SmartAttributesForm(AdvancendAttrsMixin, forms.Form):
    question = forms.CharField(required=False, help_text="If set, user must check related box to display the field")
    hint = forms.CharField(required=False, help_text="Text to display above the input")
    description = forms.CharField(required=False, help_text="Text to display below the input")
    datasource = forms.CharField(required=False, help_text="Datasource name for ajax field")


class FieldEditor:
    FORMS = {
        "field": FlexFieldAttributesForm,
        "kwargs": FormFieldAttributesForm,
        "widget_kwargs": WidgetAttributesForm,
        "smart": SmartAttributesForm,
    }

    def __init__(self, modeladmin, request, pk):
        self.modeladmin = modeladmin
        self.request = request
        self.pk = pk

    @cached_property
    def field(self):
        return FlexFormField.objects.get(pk=self.pk)

    def patch(self, request, pk):
        pass

    def get_code(self):
        # config = cache.get(f"/editor/field/{request.user.pk}/{pk}/", {})
        # base = self.get_object(request, pk)
        # base.required = config.get("kwargs", {}).get("required") == "on"
        # self._editor_get_instance(base, config)
        # rendered = json.dumps(base.advanced, indent=4)
        ctx = self.modeladmin.get_common_context(self.request)
        instance = self.field.get_instance()
        form_class_attrs = {
            "sample": instance,
        }
        form_class = type(forms.Form)("TestForm", (forms.Form,), form_class_attrs)
        ctx = self.modeladmin.get_common_context(self.request)
        ctx["form"] = form_class()
        ctx["instance"] = instance
        return render(self.request, "admin/core/flexformfield/field_editor/code.html", ctx, content_type="text/plain")

    def render(self):
        if self.request.method == "POST":
            pass
        instance = self.field.get_instance()
        form_class_attrs = {
            "sample": instance,
        }
        form_class = type(forms.Form)("TestForm", (forms.Form,), form_class_attrs)
        ctx = self.modeladmin.get_common_context(self.request)
        ctx["form"] = form_class()
        ctx["instance"] = instance

        return render(self.request, "admin/core/flexformfield/field_editor/preview.html", ctx)

        # config = cache.get(f"/editor/field/{request.user.pk}/{pk}/", {})
        # base = self.get_object(request, pk)
        # base.required = config.get("kwargs", {}).get("required") == "on"
        # self._editor_get_instance(base, config)
        # rendered = json.dumps(base.advanced, indent=4)
        # rendered = ""
        # return HttpResponse(rendered, content_type="text/plain")

    def get_forms(self, instance=None):
        return [Form(prefix=prefix, field=self.field) for prefix, Form in self.FORMS.items()]

    def refresh(self):
        return HttpResponse("Ok")

    def get(self, request, pk):
        ctx = self.modeladmin.get_common_context(request, pk)
        # i = {"field_type": fqn(obj.field_type)}
        # i.update(**obj.advanced.get("kwargs", {}))
        formField = FlexFieldAttributesForm(prefix="field", instance=self.field, field=self.field)
        formAttrs = FormFieldAttributesForm(prefix="kwargs", field=self.field)
        formWidget = WidgetAttributesForm(prefix="widget_kwargs", field=self.field)
        formSmart = SmartAttributesForm(prefix="smart", field=self.field)

        ctx["form_field"] = formField
        ctx["form_attrs"] = formAttrs
        ctx["form_widget"] = formWidget
        ctx["form_smart"] = formSmart
        return render(request, "admin/core/flexformfield/field_editor/main.html", ctx)

    def post(self, request, pk):
        pass
