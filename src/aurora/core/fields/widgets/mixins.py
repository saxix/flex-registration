from django.utils.translation import get_language

from aurora.state import state


class TailWindMixin:
    def __init__(self, attrs=None, **kwargs):
        attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 my-1 cursor-pointer"
            "text-gray-700 leading-tight focus:outline-none focus:shadow-outline ",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, **kwargs)


class SmartWidgetMixin:
    def get_context(self, name, value, attrs):
        ret = super().get_context(name, value, attrs)
        ret["LANGUAGE_CODE"] = get_language()
        ret["request"] = state.request
        ret["user"] = state.request.user
        return ret
