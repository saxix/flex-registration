from django import forms


class MultiCheckboxWidget(forms.CheckboxSelectMultiple):
    template_name = "django/forms/widgets/multi_checkbox.html"
    option_template_name = "django/forms/widgets/multi_checkbox_option.html"
