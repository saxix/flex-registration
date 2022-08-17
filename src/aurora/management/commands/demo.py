"""
"""
import datetime
import logging
import random

import djclick as click
import pytz
from django import forms

from aurora.core import fields
from aurora.core.models import OptionSet
from aurora.registration.models import Record

logger = logging.getLogger(__name__)


class NotRunningInTTYException(Exception):
    pass


@click.command()  # noqa: C901
def upgrade(**kwargs):
    from aurora.core.models import FlexForm, Validator
    from aurora.registration.models import Registration

    vf1, __ = Validator.objects.update_or_create(
        name='name must start with "S"',
        defaults=dict(
            message="name must start with 'S'", target=Validator.FORM, code="value.family_name.startsWith('S');"
        ),
    )
    v1, __ = Validator.objects.get_or_create(
        name="max_length_25",
        defaults=dict(message="String too long (max 25.chars)", target=Validator.FIELD, code="value.length<25;"),
    )
    v2, __ = Validator.objects.get_or_create(
        name="date_after_3000",
        defaults=dict(
            message="Date must be after 3000-12-01",
            target=Validator.FIELD,
            code="""var limit = Date.parse("3000-12-01");
var dt = Date.parse(value);
dt > limit;""",
        ),
    )
    OptionSet.objects.get_or_create(
        name="italian_locations",
        defaults={
            "data": "1:Rome\n2:Milan",
            "separator": ":",
        },
    )

    hh, __ = FlexForm.objects.get_or_create(name="Demo Household", defaults=dict(validator=vf1))
    hh.fields.get_or_create(label="Family Name", field_type=forms.CharField, required=True)

    ind, __ = FlexForm.objects.get_or_create(name="Demo Individual")
    ind.fields.get_or_create(label="First Name", defaults=dict(field_type=forms.CharField, required=True, validator=v1))
    ind.fields.get_or_create(label="Last Name", defaults=dict(field_type=forms.CharField, validator=v1))
    ind.fields.get_or_create(label="Date Of Birth", defaults=dict(field_type=forms.DateField, validator=v2))

    ind.fields.get_or_create(
        label="Options", defaults=dict(field_type=forms.ChoiceField, choices="opt 1, opt 2, opt 3")
    )

    ind.fields.get_or_create(
        label="Location", defaults={"field_type": fields.SelectField, "choices": "italian_locations"}
    )

    hh.formsets.get_or_create(name="individuals", defaults=dict(flex_form=ind))

    reg, __ = Registration.objects.get_or_create(name="Demo Registration1", defaults=dict(flex_form=hh), active=True)
    today = datetime.datetime.today()

    last_month = datetime.datetime.combine(today - datetime.timedelta(days=31), datetime.datetime.min.time())

    Record.objects.all().delete()
    ranges = (
        (5, 20),
        (5, 30),
    )
    for day in range(1, 31):
        for _ in range(0, random.randint(*ranges[0])):
            hour = random.randint(0, 23)
            for _ in range(0, random.randint(*ranges[1])):
                minute = random.randint(0, 59)
                ts = datetime.datetime(last_month.year, last_month.month, day, hour, minute, tzinfo=pytz.utc)
                Record.objects.create(registration=reg, timestamp=ts)
