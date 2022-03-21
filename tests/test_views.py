import pytest
from django.urls import reverse

LANGUAGES = {
    "english": "first",
    "ukrainian": "АаБбВвГгҐґДдЕеЄєЖжЗзИиІіЇїЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЬьЮюЯя",
    "chinese": "姓名",
    "japanese": "ファーストネーム",
    "arabic": "الاسم الأول",
}


@pytest.fixture()
def simple_registration(simple_form):
    from smart_register.registration.models import Registration

    reg, __ = Registration.objects.get_or_create(
        name="registration #1", defaults={"flex_form": simple_form, "active": True}
    )
    return reg


@pytest.fixture()
def encrypted_registration(simple_form):
    from smart_register.registration.models import Registration

    reg, __ = Registration.objects.get_or_create(
        name="registration #1", defaults={"flex_form": simple_form, "active": True}
    )
    priv, pub = reg.setup_encryption_keys()
    reg._private_pem = priv
    return reg


@pytest.fixture()
def complex_registration(complex_form):
    from smart_register.registration.models import Registration

    reg, __ = Registration.objects.get_or_create(
        name="registration #2", defaults={"flex_form": complex_form, "active": True}
    )
    return reg


# @pytest.mark.parametrize("first_name", LANGUAGES.values(), ids=LANGUAGES.keys())
# def test_register_latest(django_app, first_name, simple_registration):
#     url = reverse("register-latest")
#     res = django_app.get(url)
#     res = res.form.submit()
#     res.form["first_name"] = first_name
#     res.form["last_name"] = "l"
#     res = res.form.submit()
#     res.form["first_name"] = first_name
#     res.form["last_name"] = "last"
#     res = res.form.submit().follow()
#     assert res.context["record"].data["first_name"] == first_name


@pytest.mark.django_db
def test_register_simple(django_app, simple_registration):
    url = reverse("register", args=[simple_registration.locale, simple_registration.slug])
    res = django_app.get(url)
    res = res.form.submit()
    res.form["first_name"] = "first_name"
    res.form["last_name"] = "f"
    res = res.form.submit()
    res.form["first_name"] = "first"
    res.form["last_name"] = "last"
    res = res.form.submit().follow()
    assert res.context["record"].data["first_name"] == "first"


def add_dynamic_field(form, name, value):
    """Add an extra text field to a form. More work required to support files"""
    from webtest.forms import Text

    field = Text(form, "input", None, None, value)
    form.fields[name] = [field]
    form.field_order.append((name, field))


def add_extra_form_to_formset_with_data(form, prefix, field_names_and_values):
    from webtest.forms import Field as WebTestField

    total_forms_field_name = prefix + "-TOTAL_FORMS"
    next_form_index = int(form[total_forms_field_name].value)
    for extra_field_name, extra_field_value in field_names_and_values.items():
        input_field_name = "-".join((prefix, str(next_form_index), extra_field_name))
        extra_field = WebTestField(form, tag="input", name=input_field_name, pos=0, value=extra_field_value)
        form.fields[input_field_name] = [extra_field]
        form[input_field_name] = extra_field_value
        form.field_order.append((input_field_name, extra_field))
        form[total_forms_field_name].value = str(next_form_index + 1)


@pytest.mark.django_db
def test_register_complex(django_app, complex_registration):
    url = reverse("register", args=[complex_registration.locale, complex_registration.slug])
    res = django_app.get(url)
    res.form["family_name"] = "HH #1"

    add_extra_form_to_formset_with_data(
        res.form,
        "form2s",
        {
            "first_name": "First1",
            "last_name": "Last",
            "date_of_birth": "2000-12-01",
        },
    )
    add_extra_form_to_formset_with_data(
        res.form,
        "form2s",
        {
            "first_name": "First2",
            "last_name": "Last",
            "date_of_birth": "2000-12-01",
        },
    )
    res = res.form.submit().follow()
    assert res.context["record"].data["form2s"][0]["first_name"] == "First1"
    assert res.context["record"].data["form2s"][0]["last_name"] == "Last"
    assert res.context["record"].data["form2s"][1]["first_name"] == "First2"


@pytest.mark.parametrize("first_name", LANGUAGES.values(), ids=LANGUAGES.keys())
def test_register_encrypted(django_app, first_name, encrypted_registration):
    url = reverse("register", args=[encrypted_registration.locale, encrypted_registration.slug])
    res = django_app.get(url)
    res = res.form.submit()
    res.form["first_name"] = first_name
    res.form["last_name"] = "f"
    res = res.form.submit()
    res.form["first_name"] = first_name
    res.form["last_name"] = "last"
    res = res.form.submit().follow()
    record = res.context["record"]
    data = record.decrypt(encrypted_registration._private_pem)
    assert data["first_name"] == first_name
