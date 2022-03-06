from django import forms


class SmartDateWidget(forms.DateInput):
    # https://www.cssscript.com/vanilla-date-range-picker/
    class Media:
        js = [
            "datetimepicker/datepicker.js",
            "datetimepicker/dt.js",
        ]
        css = {"all": ["datetimepicker/datepicker.css"]}

    def __init__(self, attrs=None, format=None):
        attrs = {"class": "vDateField", "size": "10", **(attrs or {})}
        super().__init__(attrs=attrs, format=format)
