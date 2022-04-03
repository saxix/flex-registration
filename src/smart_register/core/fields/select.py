import logging

from django import forms
from django.conf import settings
from django.forms import BoundField
from django.urls import NoReverseMatch, reverse

from .widgets.mixins import TailWindMixin

logger = logging.getLogger(__name__)


class SmartChoiceWidget(TailWindMixin, forms.Select):
    template_name = "django/forms/widgets/smart_select.html"


class SmartSelectWidget(TailWindMixin, forms.Select):
    template_name = "django/forms/widgets/smart_select.html"


class AjaxSelectWidget(TailWindMixin, forms.Select):
    template_name = "django/forms/widgets/ajax_select.html"

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs)
        self.attrs.setdefault("class", {})
        self.attrs["class"] += " ajaxSelect"

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "https://cdnjs.cloudflare.com/ajax/libs/select2/4.1.0-beta.1/js/select2.min.js",
                "select2/ajax_select%s.js" % extra,
            ],
            css={
                "all": [
                    "https://cdnjs.cloudflare.com/ajax/libs/select2/4.1.0-beta.1/css/select2.min.css",
                ]
            },
        )


class SelectField(forms.ChoiceField):
    widget = SmartSelectWidget

    def __init__(self, **kwargs):
        self._choices = ()
        self.parent = kwargs.pop("parent", None)
        options = kwargs.pop("datasource", "")
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

                name, columns = OptionSet.parse_datasource(value)
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
        try:
            name, columns = OptionSet.parse_datasource(self.datasource)
            attrs["data-source"] = name
            # OptionSet.objects.get(name=name)
            attrs["data-ajax--url"] = reverse("optionset", args=[name, *columns])
        except (OptionSet.DoesNotExist, NoReverseMatch, TypeError) as e:
            logger.exception(e)

        return attrs

    def get_bound_field(self, form, field_name):
        ret = BoundField(form, self, field_name)
        ret.field.widget.attrs["data-name"] = ret.name
        ret.field.widget.attrs["data-label"] = ret.label
        return ret
