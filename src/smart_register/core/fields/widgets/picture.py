from django import forms


class PictureWidget(forms.Textarea):
    template_name = "django/forms/widgets/picture.html"

    class Media:
        js = [
            "webcam/webcam.js",
        ]
        css = {"all": ["webcam/webcam.css"]}

    def __init__(self, attrs=None):
        attrs = {"class": "vPictureField", **(attrs or {})}
        super().__init__(attrs=attrs)
