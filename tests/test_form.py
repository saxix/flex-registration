import pytest


@pytest.mark.django_db
def test_create_form(db):
    from smart_register.core.models import FlexForm

    form = FlexForm.objects.create(name='test')
    assert form


@pytest.mark.django_db
def test_add_formset(db):
    from smart_register.core.models import FlexForm

    master = FlexForm.objects.create(name='Master')
    detail = FlexForm.objects.create(name='Detail')
    fs = master.add_formset(detail)
    assert fs.name == 'details'


@pytest.mark.django_db
def test_add_formset(db):
    from smart_register.core.models import FlexForm

    master = FlexForm.objects.create(name='Master')
    detail = FlexForm.objects.create(name='Detail')
    fs = master.add_formset(detail)
    assert fs.name == 'details'
