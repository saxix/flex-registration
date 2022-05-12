from django import forms
from django.conf import settings
from django.forms import widgets


class CompilationTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None, dt=None, mode=0):
        _widgets = (
            widgets.TextInput(
                attrs={"class": "CompilationTimeField a"},
            ),
            widgets.TextInput(
                attrs={"class": "CompilationTimeField b"},
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

    def decompress(self, value):
        if value:
            return 0, 0
        return [None, None]


class CompilationTimeField(forms.CharField):
    widget = CompilationTimeWidget

    def __init__(self, **kwargs):
        kwargs["required"] = False
        kwargs["label"] = ""
        kwargs["help_text"] = ""
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.setdefault("class", "")
        attrs["class"] += self.__class__.__name__
        return attrs
