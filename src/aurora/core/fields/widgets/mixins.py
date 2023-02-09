from django.utils.translation import get_language

from aurora.state import state


class TailWindMixin:
    default_class = (
        "shadow appearance-none border rounded w-full py-2 px-3 my-1 cursor-pointer "
        "text-gray-700 leading-tight focus:outline-none focus:shadow-outline "
    )

    def __init__(self, attrs=None, **kwargs):
        attrs = {
            "class": self.default_class,
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Build an attribute dictionary."""
        if extra_classes := base_attrs.pop("extra_classes", None):
            base_attrs["class"] += f" {extra_classes}"
        required = self.smart_attrs.get("required_by_question", "")
        if required == "required":
            if self.smart_attrs.get("question", None):
                base_attrs.pop("required", None)
                extra_attrs.pop("required", None)
                base_attrs["class"] += " required_by_question"
        else:
            base_attrs.pop("required", None)
            extra_attrs.pop("required", None)
        return {**base_attrs, **(extra_attrs or {})}


class SmartWidgetMixin:
    def get_context(self, name, value, attrs):
        ret = super().get_context(name, value, attrs)
        ret["LANGUAGE_CODE"] = get_language()
        ret["request"] = state.request
        ret["user"] = state.request.user
        return ret
