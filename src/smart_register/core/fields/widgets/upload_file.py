from django import forms


class UploadFileWidget(forms.ClearableFileInput):
    template_name = "django/forms/widgets/upload_file.html"

    def render(self, name, value, attrs=None, renderer=None):
        attrs["class"] = (
            "form-control block w-full px-3 py-1.5 text-base font-normal "
            "text-gray-700 bg-white bg-clip-padding border border-solid "
            "border-gray-300 rounded transition ease-in-out m-0 "
            "focus:text-gray-700 focus:bg-white focus:border-blue-600 focus:outline-none"
        )
        return super().render(name, value, attrs, renderer)
