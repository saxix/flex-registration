from django import forms
from django.conf import settings


class TranslationForm(forms.Form):
    locale = forms.ChoiceField(choices=settings.LANGUAGES)


class ImportForm(forms.Form):
    file = forms.FileField()
