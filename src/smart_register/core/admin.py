from admin_extra_buttons.decorators import button
from admin_ordering.admin import OrderableAdmin
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


class FormSetInline(OrderableAdmin, TabularInline):
    model = FormSet
    fk_name = "parent"
    extra = 0
    fields = ("ordering", "name", "flex_form", "extra")
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


class FlexFormFieldInline(OrderableAdmin, TabularInline):
    model = FlexFormField
    fields = ("ordering", "label", "name", "field_type", "required", "validator")
    show_change_link = True
    extra = 0
    ordering_field = "ordering"
    ordering_field_hide_input = True

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
