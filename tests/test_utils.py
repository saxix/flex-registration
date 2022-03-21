import pytest

from smart_register.core.utils import namify, underscore_to_camelcase


@pytest.mark.parametrize("v", ["underscore_to_camelcase", "underscore to camelcase", "underscore__to_camelcase"])
def test_underscore_to_camelcase(v):
    assert underscore_to_camelcase(v) == "UnderscoreToCamelcase"


@pytest.mark.parametrize("unicode", (True, False))
@pytest.mark.parametrize(
    "value,expected",
    (
        ("a-b", "a_b"),
        ("à-b", "a_b"),
        ("à-è-î-ô-ü", "a_e_i_o_u"),
    ),
)
def test_namify_allow_unicode(unicode, value, expected):
    assert namify(value, unicode) == expected
