from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.db import models

from smart_register.core.models import FlexForm


class Registration(models.Model):
    name = CICharField(max_length=255, unique=True)
    flex_form = models.ForeignKey(FlexForm, on_delete=models.PROTECT)
    start = models.DateField(auto_now_add=True)
    end = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        get_latest_by = "start"

    def __str__(self):
        return self.name


class Record(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    timestamp = models.DateField(auto_now_add=True)
    data = models.JSONField(default=dict)
