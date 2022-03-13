import logging

from django import forms
from django.forms import BoundField
from django.urls import reverse

from smart_register.core.fields.widgets import SmartSelectWidget
from smart_register.core.fields.widgets.select import AjaxSelectWidget

logger = logging.getLogger(__name__)


class SelectField(forms.ChoiceField):
    widget = SmartSelectWidget

    def __init__(self, *, choices=(), **kwargs):
        self.parent = kwargs.pop("parent", None)
        super().__init__(**kwargs)
        self.choices = choices

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.parent:
            attrs["data-parent"] = self.parent
        return attrs

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        if value:  # pragma: no branch
            try:
                if isinstance(value, (list, tuple)):
                    value = value[0][0]
                from smart_register.core.models import OptionSet

                options = OptionSet.objects.get(name=value)
                value = list(options.as_choices())
            except OptionSet.DoesNotExist as e:
                logger.exception(e)
                raise ValueError(f"OptionSet '{value}' does not exists")
        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)


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
        """
        Return a BoundField instance that will be used when accessing the form
        field in a template.
        """
        ret = BoundField(form, self, field_name)
        ret.field.widget.attrs["data-name"] = ret.name
        ret.field.widget.attrs["data-label"] = ret.label
        return ret
