import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.db import models

from smart_register.core.models import FlexForm
from smart_register.core.utils import jsonfy, JSONEncoder


class Registration(models.Model):
    name = CICharField(max_length=255, unique=True)
    flex_form = models.ForeignKey(FlexForm, on_delete=models.PROTECT)
    start = models.DateField(auto_now_add=True)
    end = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    public_key = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        get_latest_by = "start"

    def __str__(self):
        return self.name

    def add_record(self, data):
        if self.public_key:
            public_key = serialization.load_pem_public_key(self.public_key, backend=default_backend())
            message = json.dumps(data, cls=JSONEncoder)
            encrypted = public_key.encrypt(
                message,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
            )
            payload = {"data": encrypted}
        else:
            payload = {"data": data}
        return Record.objects.create(registration=self, data=jsonfy(payload))


class Record(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    timestamp = models.DateField(auto_now_add=True)
    data = models.JSONField(default=dict)
