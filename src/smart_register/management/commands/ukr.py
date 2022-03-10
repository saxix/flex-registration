"""
"""
import logging

import djclick as click
from django import forms

from smart_register.core import fields, registry
from smart_register.core.models import OptionSet, CustomFieldType

logger = logging.getLogger(__name__)


class NotRunningInTTYException(Exception):
    pass


@click.command()  # noqa: C901
def upgrade(**kwargs):
    from smart_register.core.models import FlexForm, Validator
    from smart_register.registration.models import Registration

    custom_fields = [
        {"name": "MaritalStatus", "base_type": registry.forms.ChoiceField, "options": ()},
        {"name": "Residence Status", "base_type": registry.forms.RadioSelect, "options": ()},
        {"name": "", "base_type": registry.forms.ChoiceField, "options": ()},
        {"name": "", "base_type": registry.forms.ChoiceField, "options": ()},
    ]
    for fld in custom_fields:
        name = fld.pop("name")
        CustomFieldType.objects.update_or_create(name=name, **fld)

    base, __ = FlexForm.objects.get_or_create(name="Basic")
    hh, __ = FlexForm.objects.get_or_create(name="Household")
    ind, __ = FlexForm.objects.get_or_create(name="Individual")
    doc, __ = FlexForm.objects.get_or_create(name="Document")
    bank, __ = FlexForm.objects.get_or_create(name="Bank Account")

    base.add_field(
        "Can you meet the basic needs of your household according to your priorities?",
        registry.fields.RadioField,
        choices=["Yes", "No"],
    )

    # hh.fields.get_or_create(label="Family Name", field_type=forms.CharField, required=True)
    #
    # hh.fields.get_or_create(label="Family Name", field_type=forms.CharField, required=True)
    #
    # ind.fields.get_or_create(label="First Name", defaults=dict(field_type=forms.CharField, required=True, validator=v1))
    # ind.fields.get_or_create(label="Last Name", defaults=dict(field_type=forms.CharField, validator=v1))
    # ind.fields.get_or_create(label="Date Of Birth", defaults=dict(field_type=forms.DateField, validator=v2))
    #
    # ind.fields.get_or_create(
    #     label="Options", defaults=dict(field_type=forms.ChoiceField, choices="opt 1, opt 2, opt 3")
    # )
    #
    # ind.fields.get_or_create(
    #     label="Location", defaults={"field_type": fields.SelectField, "choices": "italian_locations"}
    # )
    #
    # hh.formsets.get_or_create(name="individuals", defaults=dict(flex_form=ind))
    #
    # Registration.objects.get_or_create(name="Registration1", defaults=dict(flex_form=hh))
