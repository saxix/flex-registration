import logging

from ..state import state
from .models import Message

logger = logging.getLogger(__name__)


class Dictionary:
    def __init__(self, locale):
        self.locale = locale
        self.messages = {}
        self._loaded = False

    def reset(self):
        self.messages = {}

    def load_all(self):
        entries = Message.objects.filter(locale=self.locale, draft=False).values("msgid", "msgstr")
        self.messages = {k["msgid"]: k["msgstr"] for k in entries}
        self._loaded = True

    def __getitem__(self, msgid):
        translation = msgid
        if not msgid.strip():
            return translation
        try:
            translation = self.messages[msgid]
        except KeyError:
            if state.collect_messages:
                try:
                    msg = Message.objects.get(locale=self.locale, msgid__iexact=str(msgid))
                    if not msg.draft:
                        translation = msg.msgstr
                except Message.MultipleObjectsReturned as e:
                    logger.exception(e)
                    msg = Message.objects.filter(locale=self.locale, msgid__iexact=str(msgid)).first()
                    if not msg.draft:
                        translation = msg.msgstr

                except Message.DoesNotExist:
                    msg, __ = Message.objects.get_or_create(msgid=msgid, locale=self.locale, defaults={"msgstr": msgid})
                    translation = msg.msgstr
        return translation


class Cache:
    def __init__(self):
        self.locales = {}

    def activate(self, locale):
        e = self[locale]
        e.load_all()
        return e

    def __getitem__(self, locale):
        try:
            entry = self.locales[locale]
        except KeyError:
            entry = Dictionary(locale)
            self.locales[locale] = entry
        return entry


translator = Cache()
del Cache
