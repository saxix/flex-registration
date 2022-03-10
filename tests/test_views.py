import base64
import json

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.urls import reverse
from webtest import Upload


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


@pytest.mark.django_db
def test_register_latest(django_app, simple_registration):
    url = reverse("register-latest")
    res = django_app.get(url)
    res = res.form.submit()
    res.form["first_name"] = "first_name"
    res.form["last_name"] = "f"
    res = res.form.submit()
    res.form["first_name"] = "first"
    res.form["last_name"] = "last"
    res = res.form.submit()
    assert res.context["record"].data["data"]["first_name"] == "first"


@pytest.mark.django_db
def test_register_simple(django_app, simple_registration):
    url = reverse("register", args=[simple_registration.pk])
    res = django_app.get(url)
    res = res.form.submit()
    res.form["first_name"] = "first_name"
    res.form["last_name"] = "f"
    res = res.form.submit()
    res.form["first_name"] = "first"
    res.form["last_name"] = "last"
    res = res.form.submit()
    assert res.context["record"].data["data"]["first_name"] == "first"


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
    url = reverse("register", args=[complex_registration.pk])
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
    res = res.form.submit()
    assert res.context["record"].data["data"]["form2s"][0]["first_name"] == "First1"
    assert res.context["record"].data["data"]["form2s"][0]["last_name"] == "Last"
    assert res.context["record"].data["data"]["form2s"][1]["first_name"] == "First2"


def decrypt(private_pem, data):
    private_key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())

    stream = data["data"]
    decoded = base64.b64decode(stream)
    decrypted = private_key.decrypt(
        decoded, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return json.loads(decrypted.decode())


@pytest.mark.django_db
def test_register_encrypted(django_app, encrypted_registration):
    url = reverse("register", args=[encrypted_registration.pk])
    res = django_app.get(url)
    res = res.form.submit()
    res.form["first_name"] = "first_name"
    res.form["last_name"] = "f"
    res = res.form.submit()
    res.form["first_name"] = "first"
    res.form["last_name"] = "last"
    res = res.form.submit()
    record = res.context["record"]
    decrypted = decrypt(encrypted_registration._private_pem, record.data)

    assert decrypted["first_name"] == "first"


@pytest.mark.django_db
def test_upload_image(django_app, complex_registration, mock_storage):
    url = reverse("register", args=[complex_registration.pk])
    res = django_app.get(url)
    res.form["family_name"] = "HH #1"

    add_extra_form_to_formset_with_data(
        res.form,
        "form2s",
        {
            "first_name": "First1",
            "last_name": "Last",
            "date_of_birth": "2000-12-01",
            "image": Upload("tests/data/image.jpeg"),
        },
    )
    res = res.form.submit()
    assert res.context["record"].data["data"]["family_name"] == "HH #1"
    assert res.context["record"].data["data"]["form2s"][0]["image"] == "image.jpeg"


@pytest.mark.skip("Problem with encrypted file")
@pytest.mark.django_db
def test_upload_image_register_encrypted(django_app, encrypted_registration, mock_storage):
    url = reverse("register", args=[encrypted_registration.pk])
    res = django_app.get(url)
    res.form["first_name"] = "first"
    res.form["last_name"] = "last"
    res.form["image"] = Upload("tests/data/image.jpeg")

    res = res.form.submit()
    record = res.context["record"]
    decrypted = decrypt(encrypted_registration._private_pem, record.data)

    assert decrypted["first_name"] == "first"
    assert decrypted["image"] == "image.jpeg"
