"""
"""
import logging
from pathlib import Path

import djclick as click
from django.core.management import CommandError, call_command

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
def upgrade(admin_email, admin_password, static, migrate, prompt, verbosity, **kwargs):
    from smart_register.config import env

    extra = {"no_input": prompt, "verbosity": verbosity - 1, "stdout": None}
    if migrate:
        if verbosity >= 1:
            click.echo("Run migrations")
        call_command("migrate", **extra)
        call_command("create_extra_permissions")

    static_root = Path(env("STATIC_ROOT"))
    if not static_root.exists():
        static_root.mkdir(parents=True)
    print(f"STATIC_ROOT set to '{static_root}' ('{static_root.absolute()}')")
    if static:
        if verbosity >= 1:
            click.echo("Run collectstatic")
        call_command("collectstatic", **extra)

    if admin_email:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            print("Superuser already exists. Ignoring ADMIN_EMAIL")
        else:
            username, __ = admin_email.split("@")
            if User.objects.filter(username=username).exists():
                print("User with this name already exists")
            else:
                try:
                    call_command(
                        "createsuperuser", interactive=False, username=username, email=admin_email, verbosity=verbosity
                    )
                    u = User.objects.get(username=username)
                    u.set_password(admin_password)
                    u.save()
                except CommandError:
                    raise

        import django
        from django.conf import settings
        from django.utils import translation

        from smart_register.i18n.models import Message
        from smart_register.registration.models import Registration

        Message.objects.raw('ALTER TABLE i18n_message DROP COLUMN IF EXISTS orphan;')
        Registration.objects.raw('DROP INDEX CONCURRENTLY IF EXISTS registration_registration_slug_d104c7ea_uniq;')

        django.setup()
        print(f"LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
        print(f"LOCALE: {translation.to_locale(settings.LANGUAGE_CODE)}")
        translation.activate(settings.LANGUAGE_CODE)
        print("check_for_language", translation.check_for_language("settings.LANGUAGE_CODE"))
