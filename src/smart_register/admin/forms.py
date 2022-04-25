from django import forms


class ImportForm(forms.Form):
    file = forms.FileField()


class ExportForm(forms.Form):
    APPS = ("core", "registration", "i18n", "constance")
    apps = forms.MultipleChoiceField(choices=zip(APPS, APPS), widget=forms.CheckboxSelectMultiple())
