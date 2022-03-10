from django import forms


class UploadFileWidget(forms.ClearableFileInput):
    template_name = "django/forms/widgets/upload_file.html"
