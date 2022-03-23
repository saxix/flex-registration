from django import forms

from .mixins import TailWindMixin


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

    class Media:
        js = [
            "select2/select2.min.js",
            "select2/ajax_select.js",
        ]
        css = {"all": ["select2/select2.min.css"]}
