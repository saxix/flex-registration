"""
"""
import logging
from pathlib import Path

import djclick as click
from django.db.transaction import atomic

from smart_register.core.models import OptionSet
from smart_register.core import registry
from smart_register.core.models import CustomFieldType
from smart_register.core.registry import field_registry

logger = logging.getLogger(__name__)


class NotRunningInTTYException(Exception):
    pass


@click.command()  # noqa: C901
def upgrade(**kwargs):
    optionsets = [
        {
            "name": "ua_admin1",
            "separator": ";",
            "columns": "pk,__,label",
        },
        {
            "name": "ua_admin2",
            "separator": ";",
            "columns": "pk,parent,label",
        },
        {
            "name": "ua_admin3",
            "separator": ";",
            "columns": "pk,parent,label",
        },
        {
            "name": "countries",
            "separator": ";",
            "columns": "label,pk",
        },
    ]
    for fld in optionsets:
        name = fld.pop("name")
        fld["data"] = (Path(__file__).parent / f"data/{name}.txt").read_text()
        with atomic():
            fld = OptionSet.objects.update_or_create(name=name, defaults=fld)

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
        {
            "name": "Registration Method",
            "base_type": registry.forms.ChoiceField,
            "attrs": {
                "choices": (
                    ("hh_registration", "Household Registration"),
                    ("community", "Community-level Registration"),
                )
            },
        },
        {
            "name": "Data Sharing",
            "base_type": registry.fields.multi_checkbox.MultiCheckboxField,
            "attrs": {
                "choices": (
                    ("unicef", "UNICEF"),
                    ("humanitarian_partner", "Humanitarian partners"),
                    ("private_partner", "Private partners"),
                    ("government_partner", "Government partners"),
                )
            },
        },
    ]

    for fld in custom_fields:
        name = fld.pop("name")
        with atomic():
            fld = CustomFieldType.build(name, fld)
            field_registry.register(fld.get_class())
