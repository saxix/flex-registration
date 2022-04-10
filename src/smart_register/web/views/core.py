from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.list import BaseListView

from smart_register.core.models import OptionSet


def filter_optionset(obj, request, columns):
    term = request.GET.get("q")
    parent = request.GET.get("parent")
    pk = request.GET.get("pk")

    def _filter(record):
        valid = True
        if pk:
            valid = valid and record["pk"].lower() == pk.lower()
        if term:
            valid = valid and record["label"].lower().startswith(term.lower())
        if parent:
            valid = valid and record["parent"] == parent
        return valid

    data = {
        "results": [
            {
                "id": record["pk"],
                "parent": record["parent"],
                "text": record["label"],
            }
            for record in obj.as_json(columns)
            if _filter(record)
        ],
    }
    response = JsonResponse(data)
    response["Cache-Control"] = "public, max-age=315360000"
    response["ETag"] = f"{obj.get_cache_key()}-{term}-{parent}-{columns}-{obj.version}"
    return response


@method_decorator(cache_page(60 * 60), name="dispatch")
class OptionsListView(BaseListView):
    def get(self, request, *args, **kwargs):
        name = self.kwargs["name"]
        pk = int(self.kwargs["pk"])
        label = int(self.kwargs["label"])
        parent = int(self.kwargs.get("parent", "-1"))
        obj = get_object_or_404(OptionSet, name=name)
        return filter_optionset(obj, request, [pk, label, parent])
