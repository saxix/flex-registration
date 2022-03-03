from django import forms
from strategy_field.registry import Registry


class FieldRegistry(Registry):
    pass


registry = FieldRegistry(forms.Field)
registry.register(forms.CharField)
registry.register(forms.EmailField)
registry.register(forms.IntegerField)
registry.register(forms.IntegerField)


