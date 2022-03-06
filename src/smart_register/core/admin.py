from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib.admin import TabularInline, register
from smart_admin.modeladmin import SmartModelAdmin

from .forms import ValidatorForm
from .models import FlexForm, FlexFormField, FormSet, Validator, OptionSet, CustomField


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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@register(FlexFormField)
class FlexFormFieldAdmin(SmartModelAdmin):
    list_display = ("flex_form", "name", "field", "required", "validator")
    list_filter = (("flex_form", AutoCompleteFilter),)


class FlexFormFieldInline(TabularInline):
    model = FlexFormField
    fields = ("label", "name", "field", "required", "validator")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj.pk:
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


@register(CustomField)
class CustomFieldAdmin(SmartModelAdmin):
    list_display = (
        "name",
        "attrs",
    )
    search_fields = ("name",)
