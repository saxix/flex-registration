from django import forms


class MultiCheckboxField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
