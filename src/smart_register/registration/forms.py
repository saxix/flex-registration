from django import forms


class CloneForm(forms.Form):
    title = forms.CharField()
    deep = forms.BooleanField(required=False, help_text="Clone all forms and fields too")
    # full = forms.BooleanField(required=False, help_text="Clone all forms and fields too")
