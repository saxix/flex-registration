from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.list import BaseListView

from smart_register.core.models import OptionSet


def filter_optionset(obj, request):
    term = request.GET.get("q")
    parent = request.GET.get("parent")

    def _filter(record):
        valid = True
        if term:
            valid = valid and record["label"].lower().startswith(term.lower())
        if parent:
            valid = valid and record["parent"] == parent
        return valid

    data = {
        "results": [
            {"id": record["pk"], "parent": record["parent"], "text": record["label"]}
            for record in obj.as_json()
            if _filter(record)
        ],
    }
    response = JsonResponse(data)
    response["Cache-Control"] = "public, max-age=315360000"
    response["ETag"] = f"{obj.get_cache_key()}-{term}-{parent}"
    return response


class OptionsListView(BaseListView):
    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(OptionSet, name=self.kwargs["name"])
        return filter_optionset(obj, request)
