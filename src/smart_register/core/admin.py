from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib.admin import TabularInline, register
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


@register(CustomFieldType)
class CustomFieldTypeAdmin(SmartModelAdmin):
    list_display = (
        "name",
        "attrs",
    )
    search_fields = ("name",)
