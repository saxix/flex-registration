import pytest
from _pytest.python import Metafunc
from django.urls import reverse
from rest_framework.test import APIClient
from django_regex.utils import RegexList as _RegexList


class RegexList(_RegexList):
    def extend(self, __iterable) -> None:
        for e in __iterable:
            self.append(e)


def pytest_generate_tests(metafunc: Metafunc):
    import django
    from aurora.api.urls import router

    django.setup()
    if "basename" in metafunc.fixturenames:
        m = []
        ids = []
        for name, viewset, basename in router.registry:
            viewset.permission_classes = []
            m.append([basename, viewset.queryset.model])
            ids.append(basename)
        metafunc.parametrize("basename,model", m, ids=ids)


KWARGS = {}


@pytest.fixture()
def record(db, request):
    from testutils.factories import get_factory_for_model

    # TIPS: database access is forbidden in pytest_generate_tests
    model = request.getfixturevalue("model")
    instance = model.objects.first()
    if not instance:
        full_name = f"{model._meta.app_label}.{model._meta.object_name}"
        factory = get_factory_for_model(model)
        try:
            instance = factory(**KWARGS.get(full_name, {}))
        except Exception as e:
            raise Exception(f"Error creating fixture for {model}") from e
    return instance


def test_list(db, basename, model, record):
    client = APIClient()
    client.force_authenticate()
    res = client.get(reverse(f"api:{basename}-list"))
    assert res.status_code == 200


def test_detail(db, basename, model, record):
    client = APIClient()
    client.force_authenticate()
    res = client.get(reverse(f"api:{basename}-detail", args=[record.pk]))
    assert res.status_code == 200
