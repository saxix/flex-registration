from django import forms
from django.conf import settings

from ...utils import get_versioned_static_name
from .mixins import TailWindMixin


class SmartDateWidget(TailWindMixin, forms.DateInput):
    # class Media:
    #     js = [
    #         get_versioned_static_name("datetimepicker/datepicker"s.js"),
    #         # "https://cdnjs.cloudflare.com/ajax/libs/jquery-datetimepicker/2.5.20/jquery.datetimepicker.full.min.js",
    #         get_versioned_static_name("datetimepicker/dt.js"),
    #     ]
    #     css = {"all": [get_versioned_static_name("datetimepicker/datepicker.css")]}

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs=attrs, format=format)
        self.attrs.setdefault("class", {})
        self.attrs["class"] += " vDateField "
        self.attrs["size"] = 10

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "datetimepicker/datepicker%s.js" % extra,
                # "https://cdnjs.cloudflare.com/ajax/libs/jquery-datetimepicker/2.5.20/jquery.datetimepicker.full.min.js",
                "datetimepicker/dt%s.js" % extra,
            ],
            css={"all": [get_versioned_static_name("datetimepicker/datepicker.css")]},
        )
