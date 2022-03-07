from django import forms
from django.core.exceptions import ValidationError

from .fields.widgets import PythonEditor


class ValidatorForm(forms.ModelForm):
    code = forms.CharField(widget=PythonEditor)


class FlexFormBaseForm(forms.Form):
    flex_form = None

    def is_valid(self):
        return super().is_valid()

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.is_valid() and self.flex_form and self.flex_form.validator:
            try:
                self.flex_form.validator.validate(cleaned_data)
            except Exception as e:
                raise ValidationError(e)
        return cleaned_data
