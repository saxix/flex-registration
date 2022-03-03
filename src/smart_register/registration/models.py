from django.contrib.postgres.fields import CICharField
from django.db import models

from smart_register.core.models import FlexForm


class DataSet(models.Model):
    name = CICharField(max_length=255, unique=True)
    flex_form = models.ForeignKey(FlexForm, on_delete=models.PROTECT)
    start = models.DateField(auto_now_add=True)
    end = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class Record(models.Model):
    registration = models.ForeignKey(DataSet, on_delete=models.PROTECT)
    timestamp = models.DateField(auto_now_add=True)
    data = models.JSONField(default=dict)
