from django import forms

from .widgets import PictureWidget


class PictureField(forms.CharField):
    widget = PictureWidget
