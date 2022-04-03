import json
import logging

from Crypto.PublicKey import RSA
from concurrency.fields import AutoIncVersionField
from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from smart_register.core.crypto import crypt, decrypt, Crypto
from smart_register.core.models import FlexForm, Validator
from smart_register.core.utils import dict_setdefault, safe_json, get_client_ip
from smart_register.state import state

logger = logging.getLogger(__name__)

undefined = object()


class Registration(models.Model):
    ADVANCED_DEFAULT_ATTRS = {
        "smart": {
            "buttons": {
                "link": {"widget": {"attrs": {}}},
            }
        }
    }
    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)

    name = CICharField(max_length=255, unique=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=500, blank=True, null=True)

    flex_form = models.ForeignKey(FlexForm, on_delete=models.PROTECT)
    start = models.DateField(auto_now_add=True)
    end = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    intro = models.TextField(blank=True, null=True)
    footer = models.TextField(blank=True, null=True)
    validator = models.ForeignKey(
        Validator, limit_choices_to={"target": Validator.MODULE}, blank=True, null=True, on_delete=models.SET_NULL
    )

    public_key = models.TextField(
        blank=True,
        null=True,
    )
    encrypt_data = models.BooleanField(default=False)
    advanced = models.JSONField(default=dict, blank=True)

    class Meta:
        get_latest_by = "start"
        unique_together = (("name", "locale"),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("register", args=[self.locale, self.slug])

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.title:
            self.title = self.name
        dict_setdefault(self.advanced, self.ADVANCED_DEFAULT_ATTRS)
        super().save(force_insert, force_update, using, update_fields)

    def translations(self):
        return Registration.objects.filter(slug=self.slug, active=True)

    def setup_encryption_keys(self):
        key = RSA.generate(2048)
        private_pem = key.export_key()
        public_pem: bytes = key.publickey().export_key()

        self.public_key: str = public_pem.decode()
        self.public_key2 = public_pem
        self.save()
        return private_pem, public_pem

    def encrypt(self, value):
        if not isinstance(value, str):
            value = safe_json(value)
        return crypt(value, self.public_key)

    def add_record(self, data):
        if self.public_key:
            fields = {"storage": self.encrypt(data)}
        elif self.encrypt_data:
            fields = {"storage": Crypto().encrypt(data).encode()}
        else:
            fields = {"storage": safe_json(data).encode()}
        return Record.objects.create(registration=self, **fields)


class RemoteIp(models.GenericIPAddressField):
    def pre_save(self, model_instance, add):
        if add:
            value = get_client_ip(state.request)
            setattr(model_instance, self.attname, value)
        return getattr(model_instance, self.attname)


class Record(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    remote_ip = RemoteIp(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    storage = models.BinaryField(null=True, blank=True)
    ignored = models.BooleanField(default=False, blank=True)

    def decrypt(self, private_key=undefined, secret=undefined):
        if private_key != undefined:
            return json.loads(decrypt(self.storage, private_key))
        elif secret != undefined:
            return json.loads(Crypto(secret).decrypt(self.storage))

    @property
    def data(self):
        if self.registration.public_key:
            return {"Forbidden": "Cannot access encrypted data"}
        elif self.registration.encrypt_data:
            return self.decrypt(secret=None)
        else:
            return json.loads(self.storage.tobytes().decode())
