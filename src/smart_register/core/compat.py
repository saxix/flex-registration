from django import forms
from django_regex.fields import RegexField as RegexField_
from django_regex.utils import Regex
from strategy_field.fields import StrategyClassField as StrategyClassField_
from strategy_field.utils import fqn


class RegexEditor(forms.Textarea):
    template_name = "django/forms/widgets/regex.html"


class RegexField(RegexField_):
    widget = RegexEditor

    def value_from_object(self, obj):
        """Return the value of this field in the given model instance."""
        return getattr(obj, self.attname)

    def get_prep_value(self, value):
        if isinstance(value, Regex):
            return value.pattern
        return value


class StrategyClassField(StrategyClassField_):
    def value_to_string(self, obj):
        return fqn(self.value_from_object(obj))
