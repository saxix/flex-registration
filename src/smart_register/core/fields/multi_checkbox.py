from django import forms

from smart_register.core.fields.widgets.mixins import SmartWidgetMixin


class MultiCheckboxWidget(SmartWidgetMixin, forms.CheckboxSelectMultiple):
    template_name = "django/forms/widgets/multi_checkbox.html"
    option_template_name = "django/forms/widgets/multi_checkbox_option.html"


class MultiCheckboxField(forms.MultipleChoiceField):
    widget = MultiCheckboxWidget
