from django import forms

from .mixins import SmartFieldMixin
from .widgets.mixins import TailWindMixin


class LabelOnlyWidget(TailWindMixin, forms.TextInput):
    template_name = "django/forms/widgets/label.html"


class LabelOnlyField(forms.CharField):
    widget = LabelOnlyWidget
    storage = None
