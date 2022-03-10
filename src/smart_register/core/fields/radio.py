from django import forms

from .widgets import YesNoRadioWidget


class RadioField(forms.ChoiceField):
    pass


class YesNoRadio(RadioField):
    widget = YesNoRadioWidget

    def __init__(self, *, choices=(("y", "Yes"), ("n", "No")), **kwargs):
        super().__init__(choices=choices, **kwargs)


class YesNoChoice(forms.ChoiceField):
    def __init__(self, *, choices=(("y", "Yes"), ("n", "No")), **kwargs):
        super().__init__(choices=choices, **kwargs)
