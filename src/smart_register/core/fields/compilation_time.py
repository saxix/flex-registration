from django import forms
from django.conf import settings
from django.forms import widgets


class CompilationTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None, dt=None, mode=0):
        _widgets = (
            widgets.HiddenInput(
                attrs={"class": "CompilationTimeField start"},
            ),
            widgets.HiddenInput(
                attrs={"class": "CompilationTimeField elapsed"},
            ),
            widgets.HiddenInput(
                attrs={"class": "CompilationTimeField round"},
            ),
            widgets.HiddenInput(
                attrs={"class": "CompilationTimeField total"},
            ),
        )
        super().__init__(_widgets, attrs)

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        base = super().media
        return base + forms.Media(
            js=[
                "elapsed%s.js" % extra,
            ],
        )

    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs, renderer)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build an attribute dictionary."""
        return {**base_attrs, **(extra_attrs or {})}

    def decompress(self, value):
        if value:
            return value
        return [None, 0, 0, 0]


class CompilationTimeField(forms.CharField):
    widget = CompilationTimeWidget

    def __init__(self, **kwargs):
        kwargs["required"] = False
        kwargs["label"] = ""
        kwargs["help_text"] = ""
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.pop("class", "")
        # attrs.setdefault("class", "")
        # attrs["class"] += self.__class__.__name__
        return attrs
