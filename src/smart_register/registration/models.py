import json

from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.db import models

from smart_register.core.crypto import crypt, decrypt
from smart_register.core.models import FlexForm
from smart_register.core.utils import safe_json


class Registration(models.Model):
    name = CICharField(max_length=255, unique=True)
    flex_form = models.ForeignKey(FlexForm, on_delete=models.PROTECT)
    start = models.DateField(auto_now_add=True)
    end = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    intro = models.TextField(blank=True, null=True)

    public_key = models.TextField(
        blank=True,
        null=True,
    )

    # public_key2 = models.BinaryField(
    #     blank=True,
    #     null=True,
    # )
    class Meta:
        get_latest_by = "start"

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    def setup_encryption_keys(self):
        key = RSA.generate(2048)
        private_pem = key.export_key()
        public_pem: bytes = key.publickey().export_key()

        self.public_key: str = public_pem.decode()
        self.public_key2 = public_pem
        self.save()
        return private_pem, public_pem

    def setup_encryption_keys2(self):
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
        if not isinstance(value, str):
            value = json.dumps(value)
        return crypt(value, self.public_key)

    def add_record(self, data):
        if self.public_key:
            fields = {"storage": self.encrypt(data)}
        else:
            fields = {"storage": safe_json(data).encode()}
        return Record.objects.create(registration=self, **fields)


class Record(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    timestamp = models.DateField(auto_now_add=True)
    # data = models.JSONField(default=dict)
    storage = models.BinaryField(null=True, blank=True)

    def decrypt(self, private_key):
        return json.loads(decrypt(self.storage, private_key))

    @property
    def data(self):
        if self.registration.public_key:
            return {"error": "Cannot access encrypted data"}
        else:
            return json.loads(self.storage.tobytes().decode())
