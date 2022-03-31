from django import forms

from .mixins import TailWindMixin


class SmartDateWidget(TailWindMixin, forms.DateInput):
    class Media:
        js = [
            "datetimepicker/datepicker.js",
            # "https://cdnjs.cloudflare.com/ajax/libs/jquery-datetimepicker/2.5.20/jquery.datetimepicker.full.min.js",
            "datetimepicker/dt.js",
        ]
        css = {"all": ["datetimepicker/datepicker.css"]}

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs=attrs, format=format)
        self.attrs.setdefault("class", {})
        self.attrs["class"] += " vDateField "
        self.attrs["size"] = 10
