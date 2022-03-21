from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.templatetags.static import static

from .fields.widgets import PythonEditor


class ValidatorForm(forms.ModelForm):
    code = forms.CharField(widget=PythonEditor)


class CustomFieldMixin:
    custom = None


class FlexFormBaseForm(forms.Form):
    flex_form = None

    def is_valid(self):
        return super().is_valid()

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "/static/smart%s.js" % extra,
            ]
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.is_valid() and self.flex_form and self.flex_form.validator:
            try:
                self.flex_form.validator.validate(cleaned_data)
            except Exception as e:
                raise ValidationError(e)
        return cleaned_data


class SmartBaseFormSet(BaseFormSet):
    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                static("jquery.formset%s.js" % extra),
                static("smart.formset%s.js" % extra),
            ]
        )
