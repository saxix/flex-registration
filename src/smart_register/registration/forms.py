from django import forms


class CloneForm(forms.Form):
    name = forms.CharField()
    # deep = forms.BooleanField(required=False)
