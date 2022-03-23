from django import forms

from smart_register.core.registry import field_registry


@field_registry.register
class RemoteIpField(forms.CharField):
    pass
