from django import forms

from . import widgets
from .captcha import SmartCaptchaField
from .custom import CustomField
from .document import DocumentField
from .gis import LocationField
from .label import LabelOnlyField
from .multi_checkbox import MultiCheckboxField
from .picture import PictureField
from .radio import RadioField, YesNoChoice, YesNoRadio
from .remote_ip import RemoteIpField
from .select import AjaxSelectField, SelectField, SmartSelectWidget
from .widgets.mixins import SmartFieldMixin
from .image import ImageField
from .file import FileField

WIDGET_FOR_FORMFIELD_DEFAULTS = {
    forms.DateField: {"widget": widgets.SmartDateWidget},
    forms.CharField: {"widget": widgets.SmartTextWidget},
    forms.IntegerField: {"widget": widgets.NumberWidget},
    forms.FloatField: {"widget": widgets.NumberWidget},
    forms.ChoiceField: {"widget": SmartSelectWidget},
    # forms.ImageField: {"widget": widgets.ImageWidget},
    # forms.FileField: {"widget": widgets.UploadFileWidget},
    SelectField: {"widget": SmartSelectWidget},
    RadioField: {"widget": widgets.RadioWidget},
    YesNoRadio: {"widget": widgets.YesNoRadioWidget},
    YesNoChoice: {"widget": SmartSelectWidget},
    MultiCheckboxField: {"widget": widgets.MultiCheckboxWidget},
}
