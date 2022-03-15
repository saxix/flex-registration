from django import forms

from .widgets import YesNoRadioWidget


class RadioField(forms.ChoiceField):
    pass


class YesNoMixin:
    def __init__(self, *, choices=(), **kwargs):
        if not choices:
            choices = (("y", "Yes"), ("n", "No"))
        else:
            if len(choices) != 2:
                raise ValueError("YesNo accept only 2 choice label")
            for el in choices:
                if not isinstance(el, (list, tuple)) and el[0] not in ["y", "n"]:
                    raise ValueError(f"Choice value must be 'y' or 'n' not '{el[0]}' ")

        super().__init__(choices=choices, **kwargs)


class YesNoRadio(YesNoMixin, RadioField):
    widget = YesNoRadioWidget


class YesNoChoice(YesNoMixin, forms.ChoiceField):
    pass
