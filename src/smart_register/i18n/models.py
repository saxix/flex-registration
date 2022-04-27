import hashlib

from django.db import models
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from natural_keys import NaturalKeyModel

from .fields import LanguageField


class I18NModel:
    I18N_FIELDS = []
    I18N_ADVANCED = []


class Message(NaturalKeyModel):
    timestamp = models.DateTimeField(auto_now_add=True)
    locale = LanguageField(db_index=True)
    msgid = models.TextField(db_index=True)
    msgstr = models.TextField(blank=True, null=True)
    md5: str = models.CharField(verbose_name=_("MD5"), max_length=512, null=False, blank=False, unique=True)
    auto = models.BooleanField(default=False)
    draft = models.BooleanField(default=True)

    class Meta:
        unique_together = ("msgid", "locale")

    def __str__(self):
        return f"{self.locale} {truncatechars(self.msgid, 40)}"

    @staticmethod
    def get_md5(locale, msgid):
        return hashlib.md5((locale + "__" + msgid).encode()).hexdigest()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # self.md5 = hashlib.md5((self.locale + "__" + self.msgid).encode()).hexdigest()
        self.md5 = self.get_md5(self.locale, self.msgid)
        obj: Message = super().save()
        return obj
