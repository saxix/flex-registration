import pytest

from smart_register.core.fields import SelectField
from smart_register.core.models import OptionSet


@pytest.fixture
def options(db):
    return OptionSet.objects.get_or_create(
        name="italian_locations",
        defaults={
            "data": "1:Rome\n2:Milan",
            "separator": ":",
        },
    )[0]


def test_select(options):
    fld = SelectField(choices=[["italian_locations", "italian_locations"]])
    assert fld.choices == [["1", "Rome"], ["2", "Milan"]]


def test_error():
    with pytest.raises(ValueError):
        SelectField(choices="italian_locations")
