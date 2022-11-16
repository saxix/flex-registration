# Generated by Django 3.2.15 on 2022-09-30 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("registration", "0038_alter_registration_unique_field"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="registration",
            options={
                "get_latest_by": "start",
                "permissions": (("manage", "Can Manage Registration"), ("register", "Can User Registration")),
            },
        ),
        migrations.AddField(
            model_name="registration",
            name="protected",
            field=models.BooleanField(
                default=False,
                help_text="If true, only authenticated 'users' with 'registration.can_use_registration' "
                "permission can use this Module",
            ),
        ),
        migrations.AddField(
            model_name="registration",
            name="restrict_to_groups",
            field=models.ManyToManyField(
                blank=True, help_text="Restrict access to the following groups", to="auth.Group"
            ),
        ),
    ]