from django.apps import apps
from django.http import HttpResponse

from smart_register.publish.utils import get_registration_data


def extract(request, model, pk):
    m = apps.get_model(model)
    reg = m.objects.get(pk=pk)
    ret = get_registration_data(reg)
    response = HttpResponse(content_type="application/json")
    response.content = ret
    return response


def load(request):
    pass
