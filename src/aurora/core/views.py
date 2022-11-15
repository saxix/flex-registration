import time

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.cache import get_conditional_response
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.views.decorators.cache import cache_page
from django.views.generic.list import BaseListView
from django.conf import settings

from aurora.core.models import OptionSet
from aurora.core.utils import get_etag
from aurora.state import state


def filter_optionset(obj, pk, term, lang, parent=None):
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
            for record in obj.as_json(lang)
            if _filter(record)
        ],
    }
    return data


@method_decorator(cache_page(60 * 60), name="dispatch")
class OptionsListView(BaseListView):
    def get(self, request, *args, **kwargs):
        name = self.kwargs["name"]
        parent = self.kwargs.get("parent", None)
        lang = get_language()
        term = request.GET.get("q")
        parent = request.GET.get("parent", parent)
        pk = request.GET.get("pk")

        obj = get_object_or_404(OptionSet, name=name)

        if state.collect_messages:
            etag = get_etag(request, time.time())
        else:
            etag = get_etag(
                request,
                obj.pk,
                obj.version,
                lang,
                term,
                parent,
                pk,
            )
        response = get_conditional_response(request, str(etag))
        if response is None:
            data = filter_optionset(obj, pk, term, lang, parent)
            response = JsonResponse(data)
            response["Cache-Control"] = "public, max-age=315360000"
            response["ETag"] = etag
        return response


def service_worker(request):
    response = HttpResponse(open(settings.PWA_SERVICE_WORKER_PATH).read(), content_type='application/javascript')
    return response
