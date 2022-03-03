from django import forms

from .widgets import PythonEditor


class ValidatorForm(forms.ModelForm):
    code = forms.CharField(widget=PythonEditor)
