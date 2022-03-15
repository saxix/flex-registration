import os

import pytest
from django import forms


def pytest_configure(config):
    os.environ["DEBUG"] = "0"
    os.environ["ADMINS"] = "admin@demo.org"


@pytest.fixture()
def simple_form(db):
    from smart_register.core.models import FlexForm, Validator

    v1, __ = Validator.objects.get_or_create(
        name="length_1_50",
        defaults=dict(message="String size 1 to 5", target=Validator.FIELD, code="value.length>1 && value.length<=50;"),
    )
    v2, __ = Validator.objects.get_or_create(
        name="length_2_10",
        defaults=dict(
            message="String size 2 to 10", target=Validator.FIELD, code="value.length>2 && value.length<=10;"
        ),
    )
    frm, __ = FlexForm.objects.get_or_create(name="Form1")
    frm.fields.get_or_create(label="First Name", defaults={"field_type": forms.CharField, "required": True})
    frm.fields.get_or_create(
        label="Last Name", defaults={"field_type": forms.CharField, "required": True, "validator": v2}
    )
    return frm


@pytest.fixture()
def complex_form():
    from smart_register.core.models import FlexForm, Validator

    v1, __ = Validator.objects.get_or_create(
        name="length_2_8",
        defaults=dict(message="String size 1 to 8", target=Validator.FIELD, code="value.length>1 && value.length<=8;"),
    )
    hh, __ = FlexForm.objects.get_or_create(name="Form1")
    hh.fields.get_or_create(
        label="Family Name", defaults={"field_type": forms.CharField, "required": True, "validator": v1}
    )

    ind, __ = FlexForm.objects.get_or_create(name="Form2")
    ind.fields.get_or_create(
        label="First Name", defaults={"field_type": forms.CharField, "required": True, "validator": v1}
    )
    ind.fields.get_or_create(
        label="Last Name", defaults={"field_type": forms.CharField, "required": True, "validator": v1}
    )
    ind.fields.get_or_create(label="Date Of Birth", defaults={"field_type": forms.DateField, "required": True})

    hh.add_formset(ind)
    return hh
