from django.forms import forms

from smart_register.core.fields.widgets import UploadFileWidget


class SmartFileField(forms.FileField):
    widget = UploadFileWidget
