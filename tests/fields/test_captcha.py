import pytest

from aurora.core.fields.captcha import CaptchaTextInput, SmartCaptchaField


@pytest.mark.django_db()
def test_captcha(monkeypatch):
    monkeypatch.setattr("captcha.fields.settings.CAPTCHA_TEST_MODE", True)

    fld = SmartCaptchaField()
    assert fld.clean(["passed", "passed"])


@pytest.mark.django_db()
def test_widget(monkeypatch):
    monkeypatch.setattr("captcha.fields.settings.CAPTCHA_TEST_MODE", True)

    fld = CaptchaTextInput(attrs={})
    assert fld.render("name", "value", {})


#
# def test_custom():
#     fld = YesNoRadio(choices=[("y", "Si"), ("n", "No")])
#     assert fld.choices == [("y", "Si"), ("n", "No")]
#
#
# def test_error1():
#     with pytest.raises(ValueError):
#         YesNoRadio(choices=["Si", "No"])
#
#
# def test_error2():
#     with pytest.raises(ValueError):
#         YesNoRadio(choices=["Yes", "No", "Maybe"])
