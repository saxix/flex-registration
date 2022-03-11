from django import forms

from .mixins import TailWindMixin


class SmartSelectWidget(TailWindMixin, forms.Select):
    template_name = "django/forms/widgets/smart_select.html"
