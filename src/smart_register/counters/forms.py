from django import forms

from smart_register.registration.models import Registration


class ChartForm(forms.Form):
    registration = forms.ModelChoiceField(Registration.objects.all())
