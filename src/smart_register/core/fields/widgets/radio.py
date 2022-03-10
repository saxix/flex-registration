from django import forms


class RadioWidget(forms.RadioSelect):
    pass


class YesNoRadioWidget(forms.RadioSelect):
    template_name = "django/forms/widgets/yesnoradio.html"
    option_template_name = "django/forms/widgets/radio_option.html"
