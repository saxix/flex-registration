from django import forms


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
                "codemirror/codemirror.css",
                "codemirror/fullscreen.css",
                "codemirror/midnight.css",
                "codemirror/foldgutter.css",
            )
        }
        js = (
            "/static/admin/js/vendor/jquery/jquery.js",
            "/static/admin/js/jquery.init.js",
            "codemirror/codemirror.js",
            "codemirror/javascript.js",
            "codemirror/fullscreen.js",
            "codemirror/active-line.js",
            "codemirror/foldcode.js",
            "codemirror/foldgutter.js",
            "codemirror/indent-fold.js",
        )
