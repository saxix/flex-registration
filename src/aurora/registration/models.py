import base64
import json
import logging

import jmespath
from concurrency.fields import AutoIncVersionField
from Crypto.PublicKey import RSA
from django import forms
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import CICharField
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext as _
from natural_keys import NaturalKeyModel

from aurora.core.crypto import Crypto, crypt, decrypt
from aurora.core.models import FlexForm, Validator
from aurora.core.utils import (
    cache_aware_reverse,
    dict_setdefault,
    get_client_ip,
    jsonfy,
    safe_json,
    total_size,
)
from aurora.i18n.models import I18NModel
from aurora.registration.fields import ChoiceArrayField
from aurora.registration.storage import router
from aurora.state import state

logger = logging.getLogger(__name__)

undefined = object()


class Registration(NaturalKeyModel, I18NModel, models.Model):
    _natural_key = ("slug",)

    ADVANCED_DEFAULT_ATTRS = {
        "smart": {
            "wizard": False,
            "buttons": {
                "link": {"widget": {"attrs": {}}},
            },
        }
    }
    I18N_FIELDS = ["intro", "footer"]

    version = AutoIncVersionField()
    last_update_date = models.DateTimeField(auto_now=True)

    name = CICharField(max_length=255, unique=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=500, blank=True, null=True, unique=True)

    flex_form = models.ForeignKey(FlexForm, on_delete=models.PROTECT)
    start = models.DateField(default=timezone.now, editable=True)
    end = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=False)
    archived = models.BooleanField(
        default=False, null=False, help_text=_("Archived/Terminated registration cannot be activated/reopened")
    )
    locale = models.CharField(
        verbose_name="Default locale", max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE
    )
    locales = ChoiceArrayField(models.CharField(max_length=10, choices=settings.LANGUAGES), blank=True, null=True)
    intro = models.TextField(blank=True, null=True, default="")
    footer = models.TextField(blank=True, null=True, default="")
    client_validation = models.BooleanField(blank=True, null=False, default=False)
    validator = models.ForeignKey(
        Validator,
        limit_choices_to={"target": Validator.MODULE},
        related_name="validator_for",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    scripts = models.ManyToManyField(
        Validator, related_name="script_for", limit_choices_to={"target": Validator.SCRIPT}, blank=True
    )
    # DEPRECATED uses `unique_field_path`
    unique_field = models.CharField(
        max_length=255, blank=True, null=True, help_text="Form field to be used as unique key (DEPRECATED)"
    )

    unique_field_path = models.CharField(
        max_length=1000, blank=True, null=True, help_text="JMESPath expression to retrieve unique field"
    )
    unique_field_error = models.CharField(
        max_length=255, blank=True, null=True, help_text="Error message in case of duplicate 'unique_field'"
    )
    public_key = models.TextField(
        blank=True,
        null=True,
    )
    encrypt_data = models.BooleanField(default=False)
    advanced = models.JSONField(default=dict, blank=True)
    protected = models.BooleanField(
        default=False,
        help_text="If true, only authenticated 'users' with " "'registration.register' permission can use this Module",
    )
    restrict_to_groups = models.ManyToManyField(Group, blank=True, help_text="Restrict access to the following groups")

    class Meta:
        get_latest_by = "start"
        permissions = (
            ("manage", _("Can manage Registration")),
            ("register", _("Can use Registration")),
        )

    @property
    def media(self):
        return forms.Media(js=[script.get_script_url() for script in self.scripts.all()])

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return cache_aware_reverse("register", args=[self.slug, self.version])

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

    def add_record(self, fields_data):
        fields, files = router.decompress(fields_data)

        if self.public_key:
            kwargs = {
                # "storage": self.encrypt(fields_data),
                "files": self.encrypt(files),
                "fields": base64.b64encode(self.encrypt(fields)).decode(),
            }
        elif self.encrypt_data:
            kwargs = {
                # "storage": Crypto().encrypt(fields_data).encode(),
                "files": Crypto().encrypt(files).encode(),
                "fields": Crypto().encrypt(fields),
            }
        else:
            kwargs = {
                # "storage": safe_json(fields_data).encode(),
                "files": safe_json(files).encode(),
                "fields": jsonfy(fields),
            }
        if self.unique_field_path and not kwargs.get("unique_field", None):
            unique_value = self.get_unique_value(fields)
            kwargs["unique_field"] = unique_value

        kwargs.update(
            {
                "size": total_size(fields) + total_size(files),
                "counters": fields_data.get("counters", {}),
                "index1": fields_data.get("index1", None),
            }
        )

        return Record.objects.create(registration=self, **kwargs)

    def get_unique_value(self, cleaned_data):
        unique_value = None
        if self.unique_field_path:
            try:
                unique_value = jmespath.search(self.unique_field_path, cleaned_data)
            except Exception as e:
                logger.exception(e)
        return unique_value

    @cached_property
    def languages(self):
        return [(k, v) for k, v in settings.LANGUAGES if k in self.all_locales]

    @cached_property
    def all_locales(self):
        locales = [self.locale]
        if self.locales:
            locales += self.locales
        return set(locales)


class RemoteIp(models.GenericIPAddressField):
    def pre_save(self, model_instance, add):
        if add:
            value = get_client_ip(getattr(state, "request", None))
            setattr(model_instance, self.attname, value)
        return getattr(model_instance, self.attname)


class Record(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.PROTECT)
    unique_field = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    remote_ip = RemoteIp(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    storage = models.BinaryField(null=True, blank=True)
    ignored = models.BooleanField(default=False, blank=True, null=True)
    size = models.IntegerField(blank=True, null=True)
    counters = models.JSONField(blank=True, null=True)

    fields = models.JSONField(null=True, blank=True)
    files = models.BinaryField(null=True, blank=True)

    index1 = models.CharField(null=True, blank=True, max_length=255)
    index2 = models.CharField(null=True, blank=True, max_length=255)
    index3 = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        unique_together = ("registration", "unique_field")

    def decrypt(self, private_key=undefined, secret=undefined):
        if private_key != undefined:
            # return json.loads(decrypt(self.storage, private_key))
            files = json.loads(decrypt(self.files, private_key))
            fields = json.loads(decrypt(base64.b64decode(self.fields), private_key))
            return router.compress(fields, files)
        elif secret != undefined:
            files = json.loads(Crypto(secret).decrypt(self.files))
            fields = json.loads(Crypto(secret).decrypt(self.fields))
            return router.compress(fields, files)

    @property
    def unicef_id(self):
        ts = self.timestamp.strftime("%Y%m%d")
        return f"HOPE-{ts}-{self.registration.id}/{self.id}"

    @property
    def data(self):
        if self.registration.public_key:
            return {"Forbidden": "Cannot access encrypted data"}
        elif self.registration.encrypt_data:
            return self.decrypt(secret=None)
        else:
            files = {}
            if self.files:
                files = json.loads(self.files.tobytes().decode())
            return merge(files, self.fields or {})


def merge(a, b, path=None, update=True):
    """merges b into a"""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx, val in enumerate(b[key]):
                    a[key][idx] = merge(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
            elif update:
                a[key] = b[key]
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
