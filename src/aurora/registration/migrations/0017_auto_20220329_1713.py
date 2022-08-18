# Generated by Django 3.2.12 on 2022-03-29 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0016_auto_20220328_1602"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="ignored",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name="registration",
            name="locale",
            field=models.CharField(
                choices=[("uk-ua", "український"), ("en-us", "English"), ("pl-pl", "Polskie")],
                default="en-us",
                max_length=10,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="registration",
            unique_together={("name", "locale")},
        ),
        migrations.RemoveField(
            model_name="registration",
            name="locales",
        ),
    ]