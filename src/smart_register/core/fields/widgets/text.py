from django import forms


class SmartTextWidget(forms.TextInput):
    def __init__(self, attrs=None, format=None):
        attrs = {"class": "appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500", "size": "10", **(attrs or {})}
        super().__init__(attrs=attrs, format=format)
