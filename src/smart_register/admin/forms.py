from django import forms


class ImportForm(forms.Form):
    file = forms.FileField()


class ExportForm(forms.Form):
    APPS = ("core", "registration", "i18n", "constance")
    apps = forms.MultipleChoiceField(choices=zip(APPS, APPS), widget=forms.CheckboxSelectMultiple())


class SQLForm(forms.Form):
    command = forms.CharField()


class ConsoleForm(forms.Form):
    ACTIONS = [
        ("redis", "Flush all Redis cache"),
        ("sentry", "Check Sentry Error Delivery"),
        ("400", "raise Error 400"),
        ("401", "raise Error 401"),
        ("403", "raise Error 403"),
        ("404", "raise Error 404"),
        ("500", "raise Error 500"),
    ]

    action = forms.ChoiceField(choices=ACTIONS, widget=forms.RadioSelect)


class RedisCLIForm(forms.Form):
    command = forms.CharField()
