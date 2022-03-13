import pytest

from smart_register.core.fields import SelectField
from smart_register.core.models import OptionSet


@pytest.fixture
def complex(db):
    return OptionSet.objects.get_or_create(
        name="italian_locations",
        defaults={
            "data": "1:Rome\n2:Milan",
            "separator": ":",
        },
    )[0]


@pytest.fixture
def flat(db):
    return OptionSet.objects.get_or_create(
        name="italian_locations",
        defaults={
            "data": "Rome\nMilan",
        },
    )[0]


@pytest.fixture
def nested(db):
    return OptionSet.objects.get_or_create(
        name="italian_locations",
        defaults={
            "data": "Rome\nMilan",
        },
    )[0]


def test_select_complex(complex):
    fld = SelectField(choices=[["italian_locations", "italian_locations"]])
    assert fld.choices == [["1", "Rome"], ["2", "Milan"]]


def test_select_flat(flat):
    fld = SelectField(choices=[["italian_locations", "italian_locations"]])
    assert fld.choices == [["rome", "Rome"], ["milan", "Milan"]]


def test_error(db):
    with pytest.raises(ValueError):
        SelectField(choices="italian_locations")
