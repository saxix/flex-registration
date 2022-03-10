from django import forms
from django.core.exceptions import ObjectDoesNotExist
from strategy_field.exceptions import StrategyAttributeError
from strategy_field.registry import Registry

from . import fields
from .fields.captcha import SmartCaptchaField
from .forms import FlexFormBaseForm


def get_custom_field(value):
    from .models import CustomFieldType

    *path, name = value.split(".")
    return CustomFieldType.objects.get(name=name)


def import_custom_field(value, exc):
    try:
        return get_custom_field(value).get_class()
    except ObjectDoesNotExist:
        return None


class FieldRegistry(Registry):
    def __contains__(self, y):
        try:
            return super().__contains__(y)
        except StrategyAttributeError:
            return get_custom_field(y)


field_registry = FieldRegistry(forms.Field)

field_registry.register(forms.BooleanField)
field_registry.register(forms.CharField)
field_registry.register(forms.ChoiceField)
field_registry.register(forms.DateField)
field_registry.register(forms.DateTimeField)
field_registry.register(forms.DurationField)
field_registry.register(forms.EmailField)
field_registry.register(forms.FloatField)
field_registry.register(forms.GenericIPAddressField)
field_registry.register(forms.IntegerField)
field_registry.register(forms.MultipleChoiceField)
field_registry.register(forms.NullBooleanField)
field_registry.register(forms.TimeField)
field_registry.register(forms.URLField)
field_registry.register(SmartCaptchaField)

field_registry.register(fields.PictureField)
field_registry.register(fields.SelectField)
field_registry.register(fields.MultiCheckboxField)
field_registry.register(fields.RadioField)
field_registry.register(fields.YesNoRadio)
field_registry.register(fields.YesNoChoice)

form_registry = FieldRegistry(forms.BaseForm)
form_registry.register(forms.Form)
form_registry.register(FlexFormBaseForm)
