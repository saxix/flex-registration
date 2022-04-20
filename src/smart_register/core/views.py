from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic.list import BaseListView

from smart_register.core.models import OptionSet
from smart_register.core.utils import get_etag, get_default_language


def filter_optionset(obj, request, parent=None):
    term = request.GET.get("q")
    parent = request.GET.get("parent", parent)
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

    etag = get_etag(request, obj.pk, obj.version, get_default_language(request), term, parent, pk)
    data = {
        "data": {
            "etag": etag,
        },
        "results": [
            {
                "id": record["pk"],
                "parent": record["parent"],
                "text": record["label"],
            }
            for record in obj.as_json(request)
            if _filter(record)
        ],
    }
    response = JsonResponse(data)
    response["Cache-Control"] = "public, max-age=315360000"
    # response["ETag"] = f"{obj.get_cache_key()}-{term}-{parent}-{columns}-{obj.version}"
    response["ETag"] = etag
    return response


@method_decorator(cache_page(60 * 60), name="dispatch")
class OptionsListView(BaseListView):
    def get(self, request, *args, **kwargs):
        name = self.kwargs["name"]
        # pk = int(self.kwargs["pk"])
        parent = self.kwargs.get("parent", None)
        obj = get_object_or_404(OptionSet, name=name)
        return filter_optionset(obj, request, parent)
