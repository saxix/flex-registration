import pytest
from django.core.exceptions import ValidationError

from smart_register.core.models import Validator


def test_error_message(db):
    v = Validator(code='"Error"')
    with pytest.raises(ValidationError) as e:
        v.validate(22)
    assert e.value.messages == ["Error"]


def test_error_dict(db):
    v = Validator(code='{first_name:"Mandatory"}')
    with pytest.raises(ValidationError) as e:
        v.validate(22)
        assert e.message == ""


def test_default_error(db):
    v = Validator(code="var a=1;", message="default_error")
    with pytest.raises(ValidationError) as e:
        v.validate(22)
        assert e.message == "default_error"


def test_success_true(db):
    v = Validator(code="true")
    v.validate(22)


def test_form_valid(db):
    v = Validator(code="true")
    v.validate({"last_name": "Last"})


def test_form_simple(db):
    v = Validator(code="value.last_name.length==3;", message="wrong length")
    with pytest.raises(ValidationError) as e:
        v.validate({"last_name": "Last"})
    assert e.value.messages == ["wrong length"]


def test_form_complex(db):
    v = Validator(code='JSON.stringify({last_name: "Invalid"})', message="wrong length")
    with pytest.raises(ValidationError) as e:
        v.validate({"last_name": "Last"})
    assert e.value.message_dict == {"last_name": ["Invalid"]}


@pytest.mark.parametrize(
    "code",
    [
        'var error = (value.last_name.length==3) ? "": "Error"; error',
        '(value.last_name.length==3) ? "": "Error"',
        # 'throw Error("Not Valid")',
    ],
)
def test_form_fail_custom_message(db, code):
    v = Validator(code=code, message="wrong length")
    with pytest.raises(ValidationError) as e:
        v.validate({"last_name": "Last"})
    assert e.value.messages == ["Error"]


@pytest.mark.parametrize(
    "code",
    [
        "var error = (value.last_name.length==3) ? true: false; error",
        '(value.last_name.length==3) ? "": false',
        # 'throw Error("Not Valid")',
    ],
)
def test_form_fail_default_message(db, code):
    v = Validator(code=code, message="wrong length")
    with pytest.raises(ValidationError) as e:
        v.validate({"last_name": "Last"})
    assert e.value.messages == ["wrong length"]


@pytest.mark.parametrize(
    "code",
    [
        'var error = (value.last_name.length==3) ? true: "Error"; error',
        '(value.last_name.length==3) ? true: "Error"',
    ],
)
def test_form_success_custom_message(db, code):
    v = Validator(code=code, message="wrong length")
    v.validate({"last_name": "ABC"})
