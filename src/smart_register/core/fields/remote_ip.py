from django import forms
from django.forms import HiddenInput

from smart_register.core.registry import field_registry
from smart_register.core.utils import get_client_ip
from smart_register.state import state


@field_registry.register
class RemoteIpField(forms.CharField):
    widget = HiddenInput

    def __init__(self, **kwargs):
        kwargs["required"] = False
        kwargs["label"] = ""
        kwargs["help_text"] = ""
        kwargs["label"] = ""
        super().__init__(**kwargs)

    def to_python(self, value):
        return get_client_ip(state.request)
