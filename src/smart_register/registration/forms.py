from django import forms

from .models import Registration


class CloneForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Registration
        fields = ("name",)
