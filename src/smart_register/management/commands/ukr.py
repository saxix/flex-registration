"""
"""
import logging

import djclick as click
from django.db.transaction import atomic

from smart_register.core.models import FlexForm
from smart_register.core import registry
from smart_register.core.models import CustomFieldType
from smart_register.core.registry import field_registry
from smart_register.registration.models import Registration

logger = logging.getLogger(__name__)


class NotRunningInTTYException(Exception):
    pass


@click.command()  # noqa: C901
def upgrade(**kwargs):
    custom_fields = [
        {
            "name": "MaritalStatus",
            "base_type": registry.forms.ChoiceField,
            "attrs": {"choices": ["Single", "Married", "Divorced", "Widowed", "Separated"]},
        },
        {
            "name": "ResidenceStatus",
            "base_type": registry.forms.ChoiceField,
            "attrs": {
                "choices": (
                    ("idp", "Displaced | Internally Displaced Person (IDP)"),
                    ("refugee", "Displaced | Refugee / Asylum Seeker"),
                    ("others_of_concern", "Displaced | Others of Concern"),
                    ("host", "Non-displaced | Hosting a displaced family"),
                    ("non_host", "Non-displaced | Not hosting a displaced family"),
                    ("returnee", "Returnee"),
                    ("repatriated", "Repatriate"),
                )
            },
        },
        {"name": "Gender", "base_type": registry.forms.ChoiceField, "attrs": {"choices": ["Female", "Male"]}},
        {
            "name": "ID Type",
            "base_type": registry.forms.ChoiceField,
            "attrs": {
                "choices": (
                    ("not_available", "Not Available"),
                    ("birth_certificate", "Birth Certificate"),
                    ("drivers_license", "Driver's License"),
                    ("electoral_card", "Electoral Card"),
                    ("unhcr_id", "UNHCR ID"),
                    ("national_id", "National ID"),
                    ("national_passport", "National Passport"),
                    ("scope_id", "WFP Scope ID"),
                    ("other", "Other"),
                )
            },
        },
        {
            "name": "Relationship",
            "base_type": registry.forms.ChoiceField,
            "attrs": {
                "choices": (
                    ("son_daughter", "Son / Daughter"),
                    ("wife_husband", "Wife / Husband"),
                    ("brother_sister", "Brother / Sister"),
                    ("mother_father", "Mother / Father"),
                    ("aunt_uncle", "Aunt / Uncle"),
                    ("grandmother_grandfather", "Grandmother / Grandfather"),
                    ("motherInLaw_fatherInLaw", "Mother-in-law / Father-in-law"),
                    ("daughterInLaw_sonInLaw", "Daughter-in-law / Son-in-law"),
                    ("sisterInLaw_brotherInLaw", "Sister-in-law / Brother-in-law"),
                    ("granddaugher_grandson", "Granddaughter / Grandson"),
                    ("nephew_niece", "Nephew / Niece"),
                    ("cousin", "Cousin"),
                )
            },
        },
        {
            "name": "Collector",
            "base_type": registry.forms.ChoiceField,
            "attrs": {
                "choices": (
                    ("primary", "Primary"),
                    ("alternate", "Alternate"),
                    ("no_role", "No"),
                )
            },
        },
    ]

    for fld in custom_fields:
        name = fld.pop("name")
        with atomic():
            fld = CustomFieldType.build(name, fld)
            field_registry.register(fld.get_class())

    base, __ = FlexForm.objects.get_or_create(name="Basic")
    hh, __ = FlexForm.objects.get_or_create(name="Household")
    ind, __ = FlexForm.objects.get_or_create(name="Individual")
    doc, __ = FlexForm.objects.get_or_create(name="Document")
    bank, __ = FlexForm.objects.get_or_create(name="Bank Account")
    base.add_formset(hh, extra=1, dynamic=False)

    base.add_field(
        "With whom may we share your information (select one or multiple among the following)?",
        registry.fields.MultiCheckboxField,
        choices=(
            ("unicef", "UNICEF"),
            ("priv_partner", "Private partners"),
            ("gov_partner", "Government partners"),
        ),
        name="enum_org",
    )
    base.add_field("Residence status", "smart_register.core.models.ResidenceStatus")
    Registration.objects.get_or_create(name="Ucraina", defaults=dict(flex_form=base))
