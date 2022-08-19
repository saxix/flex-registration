from django import forms


class CloneForm(forms.Form):
    title = forms.CharField(label="New Name")
    deep = forms.BooleanField(
        required=False,
        help_text="Clone all forms and fields too. "
        "This will create a fully independend registration, form and components",
    )
