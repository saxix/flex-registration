from django import forms

from . import widgets
from .gis import LocationField
from .picture import PictureField
from .select import SelectField

WIDGET_FOR_FORMFIELD_DEFAULTS = {forms.DateField: {"widget": widgets.SmartDateWidget}}
