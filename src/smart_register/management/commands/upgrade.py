"""
"""
import logging
from pathlib import Path

import djclick as click
from django import forms
from django.core.management import call_command

logger = logging.getLogger(__name__)


class NotRunningInTTYException(Exception):
    pass


@click.command()  # noqa: C901
@click.option("-v", "--verbosity", default=1, help="verbosity")
@click.option(
    "--prompt/--no-input",
    default=False,
    is_flag=True,
    help="Do not prompt for parameters",
)
@click.option("--admin-email", "-e", default="", envvar="ADMIN_EMAIL", help="Admin email")
@click.option(
    "--admin-password",
    "-p",
    default="",
    envvar="ADMIN_PASSWORD",
    help="Admin password",
)
@click.option("--migrate/--no-migrate", default=True, is_flag=True, help="Run database migrations")
@click.option("--static/--no-static", default=True, is_flag=True, help="Collect static assets")
@click.option("--init-stripe", default=True, is_flag=True, help="Upload price list to Stripe")
def upgrade(admin_email, admin_password, static, migrate, prompt, verbosity, init_stripe, **kwargs):
    from smart_register.config import env

    extra = {"no_input": prompt, "verbosity": verbosity - 1, "stdout": None}
    if migrate:
        if verbosity >= 1:
            click.echo("Run migrations")
        call_command("migrate", **extra)
        call_command("create_extra_permissions")

    if static:
        if verbosity >= 1:
            click.echo("Run collectstatic")
        if not Path(env("STATIC_ROOT")).exists():
            Path(env("STATIC_ROOT")).mkdir(parents=True)
        call_command("collectstatic", **extra)

    from smart_register.core.models import FlexForm, Validator
    from smart_register.registration.models import Registration

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

    hh, __ = FlexForm.objects.get_or_create(name="Household", defaults=dict(validator=vf1))
    hh.fields.get_or_create(label="Family Name", field=forms.CharField, required=True)

    ind, __ = FlexForm.objects.get_or_create(name="Individual")
    ind.fields.get_or_create(label="First Name", defaults=dict(field=forms.CharField, required=True, validator=v1))
    ind.fields.get_or_create(label="Last Name", defaults=dict(field=forms.CharField, validator=v1))
    ind.fields.get_or_create(label="Date Of Birth", defaults=dict(field=forms.DateField, validator=v2))

    ind.fields.get_or_create(label="Options", defaults=dict(field=forms.ChoiceField, choices="opt 1, opt 2, opt 3"))

    hh.formsets.get_or_create(name="individuals", defaults=dict(flex_form=ind))

    Registration.objects.get_or_create(name="Registration1", defaults=dict(flex_form=hh))
