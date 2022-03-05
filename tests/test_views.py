import pytest
from django.urls import reverse


@pytest.fixture()
def simple_registration(simple_form):
    from smart_register.registration.models import DataSet
    reg, __ = DataSet.objects.get_or_create(name='registration #1',
                                            defaults=dict(flex_form=simple_form))
    return reg

@pytest.fixture()
def complex_registration(complex_form):
    from smart_register.registration.models import DataSet
    reg, __ = DataSet.objects.get_or_create(name='registration #1',
                                            defaults=dict(flex_form=complex_form))
    return reg


@pytest.mark.django_db
def test_register_simple(django_app, simple_registration):
    url = reverse("register", args=[simple_registration.pk])
    res = django_app.get(url)
    res = res.form.submit()
    res.form['first_name'] = 'first_name'
    res.form['last_name'] = 'f'
    res = res.form.submit()
    res.form['first_name'] = 'first'
    res.form['last_name'] = 'last'
    res = res.form.submit()
    assert res.context['record'].data['first_name'] == 'first'


@pytest.mark.django_db
def test_register_complex(django_app, complex_registration):
    url = reverse("register", args=[complex_registration.pk])
    res = django_app.get(url)
    res.form['family_name'] = 'HH #1'
    # res.form['first_name'] = 'HH #1'
    # res.form['family_name'] = 'HH #1'
    # res = res.form.submit()
    # FIXME: remove me (res.showbrowser)
    res.showbrowser()
    assert res.context['record'].data['first_name'] == 'first'
