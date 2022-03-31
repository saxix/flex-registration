from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet
from django.templatetags.static import static

from .fields.widgets import PythonEditor


class ValidatorForm(forms.ModelForm):
    code = forms.CharField(widget=PythonEditor)


class Select2Widget(forms.Select):
    template_name = "django/forms/widgets/select2.html"


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
                static("smart%s.js" % extra),
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
    def non_form_errors(self):
        return super().non_form_errors()

    def clean(self):
        if self.fs.validator:
            data = {
                "total_form_count": self.total_form_count(),
                "errors": self._errors,
                "non_form_errors": self._non_form_errors,
                "cleaned_data": getattr(self, "cleaned_data", []),
            }
            try:
                self.fs.validator.validate(data)
            except ValidationError as e:
                raise ValidationError([e])

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
