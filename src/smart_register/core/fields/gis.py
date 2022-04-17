import base64
import json

from django import forms
from django.conf import settings


class LocationWidget(forms.HiddenInput):
    template_name = "django/forms/widgets/location.html"

    def __init__(self, attrs=None):
        attrs = {"class": "vLocationField", **(attrs or {})}
        super().__init__(attrs=attrs)

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "gis%s.js" % extra,
            ],
        )


class LocationField(forms.CharField):
    widget = LocationWidget

    def __init__(self, *, max_length=None, min_length=None, strip=True, empty_value="", **kwargs):
        kwargs["label"] = ""
        kwargs["help_text"] = ""
        super().__init__(max_length=max_length, min_length=min_length, strip=strip, empty_value=empty_value, **kwargs)

    def to_python(self, value):
        decoded = base64.decodebytes(value.encode())
        # as_json = json.loads(decoded)
        return json.loads(decoded)
