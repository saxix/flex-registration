import base64
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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    def setup_encryption_keys(self):
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key = public_pem.decode()
        self.save()
        return private_pem, public_pem

    def encrypt(self, value):
        public_key = serialization.load_pem_public_key(self.public_key.encode(), backend=default_backend())
        if not isinstance(value, str):
            value = json.dumps(value, cls=JSONEncoder).encode("utf8")
        e = public_key.encrypt(
            value,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        return base64.b64encode(e).decode()

    def add_record(self, data):
        if self.public_key:
            e = self.encrypt(data)
            payload = {"data": e}
        else:
            payload = {"data": data}
        return Record.objects.create(registration=self, data=jsonfy(payload))


class Record(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    timestamp = models.DateField(auto_now_add=True)
    data = models.JSONField(default=dict)
