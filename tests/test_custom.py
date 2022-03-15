import pytest
from django import forms

from smart_register.core.models import CustomFieldType


@pytest.mark.django_db
def test_create_custom_field(db):
    custom = CustomFieldType(name="MaritalStatus", base_type=forms.CharField)
    custom.save()
