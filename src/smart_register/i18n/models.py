import hashlib

from django.db import models
from django.utils.translation import gettext_lazy as _

from .fields import LanguageField


class Message(models.Model):
    locale = LanguageField()
    msgid = models.TextField()
    msgstr = models.TextField(blank=True, null=True)
    md5: str = models.CharField(verbose_name=_("MD5"), max_length=512, null=False, blank=False, db_index=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.md5 = hashlib.md5((self.locale + "__" + self.msgid).encode()).digest()
        obj: Message = super().save()
        return obj
