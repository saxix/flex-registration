import os

import pytest
from django import forms
from django.core.files.storage import get_storage_class


def pytest_configure(config):
    os.environ["DEBUG"] = "0"


@pytest.fixture()
def simple_form():
    from smart_register.core.models import FlexForm, Validator

    v1, __ = Validator.objects.get_or_create(
        name="length_2_25",
        defaults=dict(message="String size 1 to 5", target=Validator.FIELD, code="value.length>1 && value.length<=5;"),
    )
    frm, __ = FlexForm.objects.get_or_create(name="Form1")
    frm.fields.get_or_create(
        label="First Name", defaults={"field_type": forms.CharField, "required": True, "validator": v1}
    )
    frm.fields.get_or_create(
        label="Last Name", defaults={"field_type": forms.CharField, "required": True, "validator": v1}
    )
    frm.fields.get_or_create(
        label="Image", defaults={"field_type": forms.ImageField, "required": False}
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

    ind.fields.get_or_create(
        label="Image", defaults={"field_type": forms.ImageField, "required": False}
    )
    hh.add_formset(ind)
    return hh


@pytest.fixture()
def mock_storage(monkeypatch):
    """Mocks the backend storage system by not actually accessing media"""

    def clean_name(name):
        return os.path.splitext(os.path.basename(name))[0]

    def _mock_save(instance, name, content):
        setattr(instance, f"mock_{clean_name(name)}_exists", True)
        return str(name).replace('\\', '/')

    def _mock_delete(instance, name):
        setattr(instance, f"mock_{clean_name(name)}_exists", False)

    def _mock_exists(instance, name):
        return getattr(instance, f"mock_{clean_name(name)}_exists", False)

    storage_class = get_storage_class()

    monkeypatch.setattr(storage_class, "_save", _mock_save)
    monkeypatch.setattr(storage_class, "delete", _mock_delete)
    monkeypatch.setattr(storage_class, "exists", _mock_exists)
