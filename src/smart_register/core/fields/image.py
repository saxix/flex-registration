from django import forms


class ImageWidget(forms.ClearableFileInput):
    template_name = "django/forms/widgets/image.html"

    # def render(self, name, value, attrs=None, renderer=None):
    #     attrs["class"] = (
    #         "bg-white "
    #         "form-control block w-full px-3 py-1.5 text-base font-normal "
    #         "text-gray-700 bg-white bg-clip-padding border border-solid "
    #         "border-gray-300 rounded transition ease-in-out m-0 "
    #         "focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
    #     )
    #     return super().render(name, value, attrs, renderer)


class ImageField(forms.ImageField):
    widget = ImageWidget

    class Media:
        js = [
            "upload/upload.js",
        ]
        css = {"all": ["upload/upload.css"]}
