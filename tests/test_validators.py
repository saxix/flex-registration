import pytest
from django.core.exceptions import ValidationError

from smart_register.core.models import Validator

HH_SIZE = """if (value.household[0].size_h_c != value.individuals.length){
    "Household size and provided members do not match"
}"""

ONLY_ONE_HEAD = """
if (value.cleaned_data.length===0){
    true
}else{
    var heads = value.cleaned_data.filter(e=>e.relationship_i_c == "head");
    var ret = true;

    if (heads.length==0){
        ret = "At least one member must be set as Head Of Household";
    }else if (heads.length>1){
        ret = "Only one member can be set as Head Of Household";
    }
    ret;
}
"""


def test_error_message():
    v = Validator(code='"Error"', active=True)
    with pytest.raises(ValidationError) as e:
        v.validate(22)
    assert e.value.messages == ["Error"]


def test_error_dict():
    v = Validator(code='{first_name:"Mandatory"}', active=True)
    with pytest.raises(ValidationError) as e:
        v.validate(22)
        assert e.message == ""


def test_default_error():
    v = Validator(code="var a=1;", message="default_error", active=True)
    with pytest.raises(ValidationError) as e:
        v.validate(22)
        assert e.message == "default_error"


def test_success_true():
    v = Validator(code="true", active=True)
    v.validate(22)


def test_form_valid():
    v = Validator(code="true", active=True)
    v.validate({"last_name": "Last"})


def test_form_simple():
    v = Validator(code="value.last_name.length==3;", message="wrong length", active=True)
    with pytest.raises(ValidationError) as e:
        v.validate({"last_name": "Last"})
    assert e.value.messages == ["wrong length"]


def test_form_complex():
    v = Validator(code='JSON.stringify({last_name: "Invalid"})', message="wrong length", active=True)
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
def test_form_fail_custom_message(code):
    v = Validator(code=code, message="wrong length", active=True)
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
def test_form_fail_default_message(code):
    v = Validator(code=code, message="wrong length", active=True)
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
def test_form_success_custom_message(code):
    v = Validator(code=code, message="wrong length", active=True)
    v.validate({"last_name": "ABC"})
