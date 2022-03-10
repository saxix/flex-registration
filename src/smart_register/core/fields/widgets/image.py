from django import forms


class ImageWidget(forms.ClearableFileInput):
    template_name = "django/forms/widgets/image.html"
