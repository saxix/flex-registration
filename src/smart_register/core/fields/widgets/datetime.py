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
        attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline vDateField",
            "size": "10",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, format=format)
