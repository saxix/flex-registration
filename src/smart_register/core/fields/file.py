from django import forms


class FileWidget(forms.ClearableFileInput):
    template_name = "django/forms/widgets/upload_file.html"


class FileField(forms.FileField):
    widget = FileWidget

    class Media:
        js = [
            "upload/upload.js",
        ]
        css = {"all": ["upload/upload.css"]}
