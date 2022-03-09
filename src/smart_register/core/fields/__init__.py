from django import forms

from . import widgets
from .gis import LocationField
from .picture import PictureField
from .select import SelectField
from .custom import CustomField
from .multi_checkbox import MultiCheckboxField

WIDGET_FOR_FORMFIELD_DEFAULTS = {
    forms.DateField: {"widget": widgets.SmartDateWidget},
    forms.CharField: {"widget": widgets.SmartTextWidget},
    SelectField: {"widget": widgets.SmartSelectWidget},
    forms.ChoiceField: {"widget": widgets.SmartSelectWidget},
}
