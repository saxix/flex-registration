from django import forms

from . import widgets
from .gis import LocationField
from .picture import PictureField
from .select import SelectField, AjaxSelectField
from .custom import CustomField
from .multi_checkbox import MultiCheckboxField
from .radio import RadioField, YesNoRadio, YesNoChoice

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
