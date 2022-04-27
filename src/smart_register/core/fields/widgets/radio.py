from django import forms

from .mixins import SmartWidgetMixin


class RadioWidget(SmartWidgetMixin, forms.RadioSelect):
    template_name = "django/forms/widgets/radio.html"
    option_template_name = "django/forms/widgets/radio_option.html"


class YesNoRadioWidget(SmartWidgetMixin, forms.RadioSelect):
    template_name = "django/forms/widgets/yesnoradio.html"
    option_template_name = "django/forms/widgets/radio_option.html"
