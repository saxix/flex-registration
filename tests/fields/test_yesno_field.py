import pytest

from smart_register.core.fields import YesNoRadio


def test_yesno():
    fld = YesNoRadio()
    assert fld.choices == [("y", "Yes"), ("n", "No")]


def test_custom():
    fld = YesNoRadio(choices=[("y", "Si"), ("n", "No")])
    assert fld.choices == [("y", "Si"), ("n", "No")]


def test_error1():
    with pytest.raises(ValueError):
        YesNoRadio(choices=["Si", "No"])


def test_error2():
    with pytest.raises(ValueError):
        YesNoRadio(choices=["Yes", "No", "Maybe"])
