import os

import pytest
from django import forms
from django.core.files.storage import get_storage_class


def pytest_addoption(parser):
    parser.addoption(
        "--selenium", action="store_true", dest="enable_selenium", default=False, help="enable selenium tests"
    )

    parser.addoption(
        "--show-browser",
        "-S",
        action="store_true",
        dest="show_browser",
        default=False,
        help="will not start browsers in headless mode",
    )


def pytest_configure(config):
    os.environ["DEBUG"] = "0"
    os.environ["ADMINS"] = "admin@demo.org"
    os.environ["CAPTCHA_TEST_MODE"] = "true"

    if config.option.show_browser:
        setattr(config.option, "enable_selenium", True)

    if not config.option.enable_selenium:
        setattr(config.option, "markexpr", "not selenium")

    from django.conf import settings, global_settings

    settings.STATICFILES_STORAGE = global_settings.STATICFILES_STORAGE


@pytest.fixture()
def simple_form(db):
    from smart_register.core.models import FlexForm, Validator
    from smart_register.core.cache import cache

    cache.clear()

    v1, __ = Validator.objects.update_or_create(
        name="length_1_50",
        defaults=dict(
            message="String size 1 to 5",
            active=True,
            target=Validator.FIELD,
            code="value.length>1 && value.length<=50;",
        ),
    )
    v2, __ = Validator.objects.update_or_create(
        name="length_2_10",
        defaults=dict(
            message="String size 2 to 10",
            active=True,
            target=Validator.FIELD,
            code="value.length>2 && value.length<=10;",
        ),
    )
    frm, __ = FlexForm.objects.update_or_create(name="Form1")
    frm.fields.get_or_create(label="First Name", defaults={"field_type": forms.CharField, "required": True})
    frm.fields.get_or_create(
        label="Last Name", defaults={"field_type": forms.CharField, "required": True, "validator": v2}
    )
    frm.fields.get_or_create(label="Image", defaults={"field_type": forms.ImageField, "required": False})
    frm.fields.get_or_create(label="File", defaults={"field_type": forms.FileField, "required": False})
    return frm


@pytest.fixture()
def complex_form():
    from smart_register.core.models import FlexForm, Validator

    v1, __ = Validator.objects.get_or_create(
        name="length_2_8",
        defaults=dict(
            message="String size 1 to 8", active=True, target=Validator.FIELD, code="value.length>1 && value.length<=8;"
        ),
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

    ind.fields.get_or_create(label="Image", defaults={"field_type": forms.ImageField, "required": False})
    ind.fields.get_or_create(label="File", defaults={"field_type": forms.FileField, "required": False})
    hh.add_formset(ind)
    return hh


@pytest.fixture()
def mock_storage(monkeypatch):
    """Mocks the backend storage system by not actually accessing media"""

    def clean_name(name):
        return os.path.splitext(os.path.basename(name))[0]

    def _mock_save(instance, name, content):
        setattr(instance, f"mock_{clean_name(name)}_exists", True)
        return str(name).replace("\\", "/")

    def _mock_delete(instance, name):
        setattr(instance, f"mock_{clean_name(name)}_exists", False)

    def _mock_exists(instance, name):
        return getattr(instance, f"mock_{clean_name(name)}_exists", False)

    storage_class = get_storage_class()

    monkeypatch.setattr(storage_class, "_save", _mock_save)
    monkeypatch.setattr(storage_class, "delete", _mock_delete)
    monkeypatch.setattr(storage_class, "exists", _mock_exists)
