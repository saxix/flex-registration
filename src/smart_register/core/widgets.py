from django import forms
from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static


class PythonEditor(forms.Textarea):
    template_name = "admin/core/widgets/editor.html"

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", "midnight")
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "python-editor"
        self.attrs["theme"] = theme

    class Media:
        css = {
            "all": (
                static("codemirror/codemirror.css"),
                static("codemirror/fullscreen.css"),
                static("codemirror/midnight.css"),
                static("codemirror/foldgutter.css"),
            )
        }
        js = (
            static("codemirror/codemirror.js"),
            static("codemirror/python.js"),
            static("codemirror/fullscreen.js"),
            static("codemirror/active-line.js"),
            static("codemirror/foldcode.js"),
            static("codemirror/foldgutter.js"),
            static("codemirror/indent-fold.js"),
        )


class ContentTypeChoiceField(forms.ModelChoiceField):
    def __init__(
            self,
            *,
            empty_label="---------",
            required=True,
            widget=None,
            label=None,
            initial=None,
            help_text="",
            to_field_name=None,
            limit_choices_to=None,
            **kwargs,
    ):
        queryset = ContentType.objects.order_by("model", "app_label")
        super().__init__(
            queryset,
            empty_label=empty_label,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            to_field_name=to_field_name,
            limit_choices_to=limit_choices_to,
            **kwargs,
        )

    def label_from_instance(self, obj):
        return f"{obj.name.title()} ({obj.app_label})"


class SmartDateWidget(forms.DateInput):
    class Media:
        js = [
            "datetimepicker/jquery.datetimepicker.js",
            "datetimepicker/datepicker.js",
        ]
        css = {'all': ["datetimepicker/jquery.datetimepicker.css"]}

    def __init__(self, attrs=None, format=None):
        attrs = {'class': 'vDateField', 'size': '10', **(attrs or {})}
        super().__init__(attrs=attrs, format=format)
