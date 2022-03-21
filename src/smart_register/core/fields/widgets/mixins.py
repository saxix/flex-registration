class TailWindMixin:
    def __init__(self, attrs=None, **kwargs):
        attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 my-1 cursor-pointer"
            "text-gray-700 leading-tight focus:outline-none focus:shadow-outline ",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, **kwargs)


class SmartFieldMixin:
    def __init__(self, *args, **kwargs) -> None:
        self.flex_field = kwargs.pop("flex_field")
        self.smart_attrs = kwargs.pop("smart_attrs", {})
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs |= self.smart_attrs
        return attrs
