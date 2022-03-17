class TailWindMixin:
    def __init__(self, attrs=None, **kwargs):
        attrs = {
            "class": "shadow appearance-none border rounded w-full py-2 px-3 my-1"
            "text-gray-700 leading-tight focus:outline-none focus:shadow-outline ",
            **(attrs or {}),
        }
        super().__init__(attrs=attrs, **kwargs)
