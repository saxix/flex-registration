import logging

from django import forms
from django.forms import BoundField
from django.urls import reverse

from smart_register.core.fields.widgets import SmartSelectWidget
from smart_register.core.fields.widgets.select import AjaxSelectWidget

logger = logging.getLogger(__name__)


class SelectField(forms.ChoiceField):
    widget = SmartSelectWidget

    def __init__(self, **kwargs):
        self._choices = ()
        self.parent = kwargs.pop("parent", None)
        options = kwargs.pop("datasource", [])
        super().__init__(**kwargs)
        self.choices = options

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.parent:
            attrs["data-parent"] = self.parent
        return attrs

    def _get_options(self):
        return self._options

    def _set_options(self, value):
        if value:  # pragma: no branch
            try:
                from smart_register.core.models import OptionSet

                if ":" in value:
                    name, cols = value.split(":")
                    columns = cols.split(",")
                else:
                    name = value
                    columns = None
                optset = OptionSet.objects.get(name=name)
                value = list(optset.as_choices(columns))
            except OptionSet.DoesNotExist as e:
                logger.exception(e)
                value = []
        self._options = self.widget.choices = value

    choices = property(_get_options, _set_options)


class AjaxSelectField(forms.Field):
    widget = AjaxSelectWidget

    def __init__(self, **kwargs):
        self.parent = kwargs.pop("parent", "")
        self.datasource = kwargs.pop("datasource", None)
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        from smart_register.core.models import OptionSet

        attrs = super().widget_attrs(widget)
        attrs["data-parent"] = self.parent
        attrs["data-source"] = self.datasource
        try:
            source = OptionSet.objects.get(name=self.datasource)
            attrs["data-ajax-url"] = reverse("optionset", args=[source.name])
        except OptionSet.DoesNotExist:
            pass

        return attrs

    def get_bound_field(self, form, field_name):
        ret = BoundField(form, self, field_name)
        ret.field.widget.attrs["data-name"] = ret.name
        ret.field.widget.attrs["data-label"] = ret.label
        return ret
