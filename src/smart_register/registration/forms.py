from django import forms
from django.conf import settings

from .models import Registration


class CloneForm(forms.ModelForm):
    locale = forms.ChoiceField(choices=settings.LANGUAGES)

    class Meta:
        model = Registration
        fields = ("locale",)
