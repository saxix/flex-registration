import pytest
from django.contrib.admin.sites import site
from django.urls import reverse

pytestmark = pytest.mark.admin


def pytest_generate_tests(metafunc):
    import django

    django.setup()
    if "panel" in metafunc.fixturenames:
        m = []
        ids = []
        for panel in site.console_panels:
            m.append(pytest.param(panel, marks=[pytest.mark.admin]))
            ids.append(panel["label"])
        metafunc.parametrize("panel", m, ids=ids)


@pytest.mark.admin
def test_panel(panel, django_app, admin_user):
    url = reverse(f"admin:{panel['name']}")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200


def test_panel_email(django_app, admin_user):
    url = reverse("admin:email")
    res = django_app.get(url, user=admin_user)
    res = res.form.submit()
    assert res.status_code == 200
