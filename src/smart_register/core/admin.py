from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from django import forms
from django.contrib.admin import TabularInline, register
from django.db.models import JSONField
from django.shortcuts import render
from jsoneditor.forms import JSONEditor
from smart_admin.modeladmin import SmartModelAdmin

from .forms import ValidatorForm
from .models import FlexForm, FlexFormField, FormSet, Validator, OptionSet, CustomFieldType


@register(Validator)
class ValidatorAdmin(SmartModelAdmin):
    form = ValidatorForm


@register(FormSet)
class FormSetAdmin(SmartModelAdmin):
    list_display = ("name", "parent", "flex_form", "extra")


class FormSetInline(TabularInline):
    model = FormSet
    fk_name = "parent"
    extra = 0
    fields = ("name", "flex_form", "extra")
    show_change_link = True

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@register(FlexFormField)
class FlexFormFieldAdmin(SmartModelAdmin):
    list_display = ("flex_form", "name", "field_type", "required", "validator")
    list_filter = (("flex_form", AutoCompleteFilter),)
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }


class FlexFormFieldInline(TabularInline):
    model = FlexFormField
    fields = ("label", "name", "field_type", "required", "validator")
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj:
            fields.append("name")
        return fields


@register(FlexForm)
class FlexFormAdmin(SmartModelAdmin):
    list_display = ("name", "validator")
    search_fields = ("name",)
    inlines = [FlexFormFieldInline, FormSetInline]


@register(OptionSet)
class OptionSetAdmin(SmartModelAdmin):
    list_display = (
        "name",
        "separator",
    )


class XXX(forms.ChoiceField):
    pass


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
                self.message_user(request, "Form validation success")
        else:
            form = formClass()
        ctx["form"] = form
        return render(request, "admin/core/customfieldtype/test.html", ctx)
