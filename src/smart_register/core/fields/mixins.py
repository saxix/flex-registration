class TailWindMixin:
    def __init__(self, attrs=None, **kwargs):
        attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 my-1 cursor-pointer"
            "text-gray-700 leading-tight focus:outline-none focus:shadow-outline ",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, **kwargs)


class SmartFieldMixin:
    NONE = None
    PRIMARY = 1
    BLOB = 2
    storage = PRIMARY

    def __init__(self, *args, **kwargs) -> None:
        self.flex_field = kwargs.pop("flex_field")
        self.smart_attrs = kwargs.pop("smart_attrs", {})
        self.data_attrs = kwargs.pop("data", {})
        super().__init__(*args, **kwargs)

    def is_stored(self):
        return self.storage in [self.PRIMARY, self.BLOB]

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        for k, v in self.smart_attrs.items():
            if k.startswith("data-") or k.startswith("on"):
                attrs[k] = v
        for k, v in self.data_attrs.items():
            attrs[f"data-{k}"] = v
        widget.smart_attrs = self.smart_attrs
        widget.flex_field = self.flex_field
        # attrs["smart_attrs"] = self.smart_attrs
        return attrs
