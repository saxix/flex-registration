import hashlib

from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _

from .fields import LanguageField


class I18NModel:
    I18N_FIELDS = []
    I18N_ADVANCED = []


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    locale = LanguageField()
    msgid = models.TextField()
    msgstr = models.TextField(blank=True, null=True)
    md5: str = models.CharField(verbose_name=_("MD5"), max_length=512, null=False, blank=False, db_index=True)

    def __str__(self):
        return f"{self.locale} {truncatechars(self.msgid, 40)}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.md5 = hashlib.md5((self.locale + "__" + self.msgid).encode()).hexdigest()
        obj: Message = super().save()
        return obj
