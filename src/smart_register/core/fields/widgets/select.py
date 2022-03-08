from django import forms

from .mixins import TailWindMixin


class SmartSelectWidget(TailWindMixin, forms.Select):
    pass
