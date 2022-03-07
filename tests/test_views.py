import pytest
from django import forms
from django.urls import reverse


@pytest.fixture()
def flex_form():
    from smart_register.core.models import FlexForm, Validator

    v1, __ = Validator.objects.get_or_create(
        name='length_2_25',
        defaults=dict(
            message='String size 1 to 5',
            target=Validator.FIELD,
            code='value.length>1 && value.length<=5;',
        ),
    )
    frm, __ = FlexForm.objects.get_or_create(name='Form1')
    frm.fields.get_or_create(
        label='First Name',
        defaults={'field': forms.CharField, 'required': True, 'validator': v1},
    )
    frm.fields.get_or_create(
        label='Last Name',
        defaults={'field': forms.CharField, 'required': True, 'validator': v1},
    )
    return frm


@pytest.fixture()
def registration(flex_form):
    from smart_register.registration.models import DataSet

    reg, __ = DataSet.objects.get_or_create(
        name='registration #1', defaults=dict(flex_form=flex_form)
    )
    return reg


@pytest.mark.django_db
def test_register(django_app, registration):
    url = reverse('register', args=[registration.pk])
    res = django_app.get(url)
    res = res.form.submit()
    res.form['first_name'] = 'first_name'
    res.form['last_name'] = 'f'
    res = res.form.submit()
    res.form['first_name'] = 'first'
    res.form['last_name'] = 'last'
    res = res.form.submit()
    assert res.context['record'].data['first_name'] == 'first'
