from django import forms


class RadioWidget(forms.RadioSelect):
    template_name = "django/forms/widgets/radio.html"
    option_template_name = "django/forms/widgets/radio_option.html"


class YesNoRadioWidget(forms.RadioSelect):
    template_name = "django/forms/widgets/yesnoradio.html"
    option_template_name = "django/forms/widgets/radio_option.html"
