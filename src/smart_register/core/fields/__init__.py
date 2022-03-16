from django import forms

from . import widgets
from .captcha import SmartCaptchaField
from .custom import CustomField
from .document import DocumentField
from .gis import LocationField
from .multi_checkbox import MultiCheckboxField
from .picture import PictureField
from .radio import RadioField, YesNoChoice, YesNoRadio
from .select import AjaxSelectField, SelectField

WIDGET_FOR_FORMFIELD_DEFAULTS = {
    forms.DateField: {"widget": widgets.SmartDateWidget},
    forms.CharField: {"widget": widgets.SmartTextWidget},
    forms.IntegerField: {"widget": widgets.NumberWidget},
    forms.FloatField: {"widget": widgets.NumberWidget},
    forms.ChoiceField: {"widget": widgets.SmartChoiceWidget},
    RadioField: {"widget": widgets.RadioWidget},
    YesNoRadio: {"widget": widgets.YesNoRadioWidget},
    YesNoChoice: {"widget": widgets.SmartSelectWidget},
    MultiCheckboxField: {"widget": widgets.MultiCheckboxWidget},
}


class SmartFieldMixin:
    def __init__(self, *args, **kwargs) -> None:
        self.smart_attrs = kwargs.pop("smart_attrs", {})
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs |= self.smart_attrs
        return attrs
