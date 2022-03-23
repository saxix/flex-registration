from django import forms
from django.templatetags.static import static


class PythonEditor(forms.Textarea):
    template_name = "admin/core/widgets/editor.html"

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", "midnight")
        self.toolbar = kwargs.pop("toolbar", True)
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
            "/static/admin/js/vendor/jquery/jquery.js",
            "/static/admin/js/jquery.init.js",
            static("codemirror/codemirror.js"),
            static("codemirror/javascript.js"),
            static("codemirror/fullscreen.js"),
            static("codemirror/active-line.js"),
            static("codemirror/foldcode.js"),
            static("codemirror/foldgutter.js"),
            static("codemirror/indent-fold.js"),
        )
